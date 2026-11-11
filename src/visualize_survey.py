
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "processed" / "student_responses_long.csv"
)

OUTPUT_DIR = ROOT / "reports" / "figures"

RANDOM_SEED = 42
BOOTSTRAP_ITERATIONS = 5000

sns.set_theme(
    style="whitegrid",
    palette="colorblind",
    font_scale=1.1
)


# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Survey data not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required = {
        "participant_id",
        "email_id",
        "true_label",
        "predicted_label",
        "email_source",
        "is_correct",
        "cyber_knowledge",
        "phishing_experience",
        "first_indicator"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    df["true_label"] = (
        df["true_label"].astype(str).str.lower().str.strip()
    )

    df["predicted_label"] = (
        df["predicted_label"].astype(str).str.lower().str.strip()
    )

    df["email_source"] = (
        df["email_source"].astype("string").str.lower().str.strip()
    )

    df["is_correct"] = (
        df["is_correct"].astype("boolean")
    )

    if df.duplicated(
        ["participant_id", "email_id"]
    ).any():
        raise ValueError(
            "Duplicate participant-email records found."
        )

    return df


# --------------------------------------------------
# BOOTSTRAP CONFIDENCE INTERVAL
# --------------------------------------------------

def bootstrap_ci(
    values,
    iterations=BOOTSTRAP_ITERATIONS,
    seed=RANDOM_SEED
):

    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if len(values) < 2:
        return np.nan, np.nan

    rng = np.random.default_rng(seed)

    samples = rng.choice(
        values,
        size=(iterations, len(values)),
        replace=True
    )

    bootstrap_means = samples.mean(axis=1)

    lower, upper = np.percentile(
        bootstrap_means,
        [2.5, 97.5]
    )

    return lower, upper


# --------------------------------------------------
# SAVE FIGURES
# --------------------------------------------------

def save_figure(fig, filename):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.savefig(
        OUTPUT_DIR / f"{filename}.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        OUTPUT_DIR / f"{filename}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)


# --------------------------------------------------
# PARTICIPANT-LEVEL SUMMARY
# --------------------------------------------------

def participant_summary(df):

    summary = (
        df.groupby("participant_id")
        .agg(
            accuracy=("is_correct", "mean"),
            cyber_knowledge=("cyber_knowledge", "first"),
            phishing_experience=(
                "phishing_experience", "first"
            ),
            first_indicator=("first_indicator", "first")
        )
        .reset_index()
    )

    return summary


# --------------------------------------------------
# FIGURE 1: ACCURACY BY EMAIL
# --------------------------------------------------

def plot_accuracy_by_email(df):

    valid = df.dropna(
        subset=["is_correct"]
    ).copy()

    rows = []

    for email_id, group in valid.groupby("email_id"):

        scores = group["is_correct"].astype(float).to_numpy()

        lower, upper = bootstrap_ci(scores)

        rows.append({
            "email_id": email_id,
            "accuracy": scores.mean() * 100,
            "lower": lower * 100,
            "upper": upper * 100,
            "n": len(scores)
        })

    result = pd.DataFrame(rows).sort_values("email_id")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        result["email_id"],
        result["accuracy"],
        color=sns.color_palette("colorblind")[0]
    )

    ax.errorbar(
        result["email_id"],
        result["accuracy"],
        yerr=[
            result["accuracy"] - result["lower"],
            result["upper"] - result["accuracy"]
        ],
        fmt="none",
        ecolor="black",
        capsize=4
    )

    ax.set_xlabel("Email Example")
    ax.set_ylabel("Classification Accuracy (%)")
    ax.set_title("Detection Accuracy by Email")

    ax.set_ylim(0, 100)

    save_figure(fig, "survey_accuracy_by_email")

# --------------------------------------------------
# FIGURE 2: RECALL BY AI-GENERATED PHISHING EMAIL
# --------------------------------------------------

def plot_recall_by_phishing_email(df):

    phishing = df[
        (df["true_label"] == "phishing")
        & (df["email_source"] == "ai_generated")
        & (df["predicted_label"].isin(["phishing", "legitimate"]))
    ].copy()

    expected_ids = {
        "email_01", "email_03", "email_05",
        "email_07", "email_09", "email_11"
    }

    if set(phishing["email_id"]) != expected_ids:
        raise ValueError(
            "Expected six AI-generated phishing email examples."
        )

    rows = []

    for email_id, group in phishing.groupby("email_id"):

        detected = (
            group["predicted_label"] == "phishing"
        ).astype(float).to_numpy()

        lower, upper = bootstrap_ci(detected)

        rows.append({
            "email_id": email_id,
            "recall": detected.mean() * 100,
            "lower": lower * 100,
            "upper": upper * 100,
        })

    result = pd.DataFrame(rows).sort_values("email_id")

    fig, ax = plt.subplots(figsize=(10, 6))

    positions = np.arange(len(result))

    ax.bar(
        positions,
        result["recall"],
        color=sns.color_palette("colorblind")[0]
    )

    ax.errorbar(
        positions,
        result["recall"],
        yerr=[
            result["recall"] - result["lower"],
            result["upper"] - result["recall"]
        ],
        fmt="none",
        ecolor="black",
        capsize=4
    )

    ax.set_xticks(positions)
    ax.set_xticklabels(result["email_id"])

    ax.set_xlabel("AI-Generated Phishing Email")
    ax.set_ylabel("Detection Recall (%)")
    ax.set_title(
        "Detection Recall by AI-Generated Phishing Email (95% CI)"
    )
    ax.set_ylim(0, 100)

    save_figure(fig, "survey_phishing_email_recall")



# --------------------------------------------------
# FIGURE 3: CONFUSION MATRIX
# --------------------------------------------------

def plot_confusion_matrix(df):

    valid = df.dropna(
        subset=["true_label", "predicted_label"]
    )

    actual = valid["true_label"]
    predicted = valid["predicted_label"]

    matrix = np.array([
        [
            ((actual == "phishing") &
             (predicted == "phishing")).sum(),

            ((actual == "phishing") &
             (predicted == "legitimate")).sum()
        ],
        [
            ((actual == "legitimate") &
             (predicted == "phishing")).sum(),

            ((actual == "legitimate") &
             (predicted == "legitimate")).sum()
        ]
    ])

    fig, ax = plt.subplots(figsize=(7, 6))

    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="viridis",
        linewidths=0.5,
        xticklabels=[
            "Predicted Phishing",
            "Predicted Legitimate"
        ],
        yticklabels=[
            "Actual Phishing",
            "Actual Legitimate"
        ],
        ax=ax
    )

    ax.set_xlabel("Predicted Class")
    ax.set_ylabel("Actual Class")
    ax.set_title("Phishing Classification Confusion Matrix")

    save_figure(fig, "survey_confusion_matrix")


# --------------------------------------------------
# FIGURE 4: CYBERSECURITY KNOWLEDGE
# --------------------------------------------------

def plot_cyber_knowledge(df):

    summary = participant_summary(
        df.dropna(subset=["is_correct"])
    )

    order = ["Низкие", "Средние", "Высокие"]

    summary = summary[
        summary["cyber_knowledge"].isin(order)
    ]

    rows = []

    for level in order:

        values = summary.loc[
            summary["cyber_knowledge"] == level,
            "accuracy"
        ].to_numpy()

        if len(values) == 0:
            continue

        lower, upper = bootstrap_ci(values)

        rows.append({
            "level": level,
            "accuracy": values.mean() * 100,
            "lower": lower * 100,
            "upper": upper * 100
        })

    result = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(8, 5))

    positions = np.arange(len(result))

    ax.bar(
        positions,
        result["accuracy"],
        color=sns.color_palette("colorblind")[:len(result)]
    )

    ax.errorbar(
        positions,
        result["accuracy"],
        yerr=[
            result["accuracy"] - result["lower"],
            result["upper"] - result["accuracy"]
        ],
        fmt="none",
        ecolor="black",
        capsize=5
    )

    ax.set_xticks(positions)
    ax.set_xticklabels(result["level"])

    ax.set_xlabel("Self-Reported Cybersecurity Knowledge")
    ax.set_ylabel("Mean Participant Accuracy (%)")
    ax.set_title("Detection Accuracy by Cybersecurity Knowledge")

    ax.set_ylim(0, 100)

    save_figure(fig, "survey_cyber_knowledge")


# --------------------------------------------------
# FIGURE 5: PHISHING EXPERIENCE
# --------------------------------------------------

def plot_phishing_experience(df):

    summary = participant_summary(
        df.dropna(subset=["is_correct"])
    )

    result = (
        summary.groupby("phishing_experience")["accuracy"]
        .agg(["mean", "count"])
        .reset_index()
    )

    result = result.dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        result["phishing_experience"],
        result["mean"] * 100,
        color=sns.color_palette("colorblind")[:len(result)]
    )

    ax.set_xlabel("Previous Phishing Experience")
    ax.set_ylabel("Mean Participant Accuracy (%)")
    ax.set_title("Detection Accuracy by Previous Experience")
    ax.set_ylim(0, 100)

    ax.tick_params(
        axis="x",
        rotation=20
    )

    save_figure(fig, "survey_phishing_experience")


# --------------------------------------------------
# FIGURE 6: FIRST DETECTION INDICATOR
# --------------------------------------------------

def plot_first_indicator(df):

    summary = participant_summary(df)

    indicators = (
        summary["first_indicator"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    indicators.columns = [
        "indicator",
        "participants"
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=indicators,
        x="participants",
        y="indicator",
        hue="indicator",
        legend=False,
        palette="colorblind",
        ax=ax
    )

    ax.set_xlabel("Number of Participants")
    ax.set_ylabel("First Detection Indicator")
    ax.set_title("Indicators Used First by Participants")

    save_figure(fig, "survey_first_indicator")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("Loading survey data...")

    df = load_data()

    print("Participants:", df["participant_id"].nunique())
    print("Classifications:", len(df))

    print("Generating research figures...")

    plot_accuracy_by_email(df)
    plot_recall_by_phishing_email(df)
    plot_confusion_matrix(df)
    plot_cyber_knowledge(df)
    plot_phishing_experience(df)
    plot_first_indicator(df)

    print("All figures exported successfully.")
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
