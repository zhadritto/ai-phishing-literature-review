from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "email_classification_summary.csv"
OUTPUT_DIR = ROOT / "reports" / "figures"


def main() -> None:
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(f"Required aggregate file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    required = {
        "email_id",
        "legitimate",
        "phishing",
        "total_responses",
        "phishing_percentage",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Aggregate file is missing columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Aggregate file contains no email examples.")
    if df["email_id"].isna().any() or df["email_id"].duplicated().any():
        raise ValueError("email_id values must be present and unique.")

    for column in ["legitimate", "phishing", "total_responses", "phishing_percentage"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if (df[["legitimate", "phishing", "total_responses"]] < 0).any().any():
        raise ValueError("Response counts cannot be negative.")
    if not (df["legitimate"] + df["phishing"] == df["total_responses"]).all():
        raise ValueError("total_responses does not equal legitimate + phishing.")
    if (df["total_responses"] == 0).any():
        raise ValueError("Each email example must have at least one response.")

    calculated = df["phishing"] / df["total_responses"] * 100
    if not (calculated.sub(df["phishing_percentage"]).abs() < 0.02).all():
        raise ValueError("phishing_percentage does not match the response counts.")

    df = df.sort_values("email_id").reset_index(drop=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: raw response counts by email. These are choices, not accuracy.
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(df))
    ax.bar(x, df["phishing"], label="Selected: phishing")
    ax.bar(x, df["legitimate"], bottom=df["phishing"], label="Selected: legitimate")
    ax.set_xticks(list(x), df["email_id"], rotation=45, ha="right")
    ax.set_ylabel("Number of participant selections")
    ax.set_xlabel("Email example")
    ax.set_title("Participant Response Counts by Email Example")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "email_response_distribution.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "email_response_distribution.pdf", bbox_inches="tight")
    plt.close(fig)

    # Figure 2: proportion choosing phishing for each example.
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_df = df.sort_values("phishing_percentage", ascending=True)
    ax.barh(plot_df["email_id"], plot_df["phishing_percentage"])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Participants selecting phishing (%)")
    ax.set_ylabel("Email example")
    ax.set_title("Phishing-Selection Percentage by Email Example")
    for position, value in enumerate(plot_df["phishing_percentage"]):
        ax.text(min(value + 1, 96), position, f"{value:.1f}%", va="center")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "phishing_selection_percentage_by_email.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "phishing_selection_percentage_by_email.pdf", bbox_inches="tight")
    plt.close(fig)

    print(f"Validated {len(df)} email examples and {int(df['total_responses'].sum())} classifications.")
    print(f"Figures saved to: {OUTPUT_DIR}")
    print("Note: figures show participant choices, not detection accuracy.")


if __name__ == "__main__":
    main()
