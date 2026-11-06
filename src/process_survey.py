
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "responses.csv"
ANSWER_KEY_FILE = ROOT / "data" / "metadata" / "email_answer_key.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

EXPECTED_EMAILS = 12

# Google Forms export, zero-based positions
EMAIL_START = 5
EMAIL_END = 17  # exclusive

METADATA_COLUMNS = {
    "age_group": 2,
    "cyber_knowledge": 3,
    "phishing_experience": 4,
    "first_indicator": 17,
    "confidence": 18,
}


def normalize_answer(value):
    """Convert Russian survey options into standard labels."""
    if pd.isna(value) or str(value).strip() == "":
        return pd.NA

    answer = str(value).strip().casefold()

    mapping = {
        "фишинговое письмо": "phishing",
        "фишинговое": "phishing",
        "фишинг": "phishing",
        "настоящее письмо": "legitimate",
        "настоящее": "legitimate",
        "легитимное письмо": "legitimate",
        "легитимное": "legitimate",
    }

    return mapping.get(answer, pd.NA)


def load_answer_key(path):
    key = pd.read_csv(path, dtype=str).fillna("")

    required = {"email_id", "true_label", "email_source"}
    if not required.issubset(key.columns):
        raise ValueError(
            f"Answer key must contain: {sorted(required)}"
        )

    key["email_id"] = key["email_id"].str.strip()
    key["true_label"] = key["true_label"].str.strip().str.lower()
    key["email_source"] = key["email_source"].str.strip().str.lower()

    expected_ids = {
        f"email_{i:02d}" for i in range(1, EXPECTED_EMAILS + 1)
    }

    if key["email_id"].duplicated().any():
        raise ValueError("Duplicate email_id in answer key.")

    if set(key["email_id"]) != expected_ids:
        raise ValueError("Answer key must contain email_01 to email_12.")

    if not set(key["true_label"]).issubset({"phishing", "legitimate"}):
        raise ValueError("Invalid true_label in answer key.")

    if key["true_label"].eq("").any():
        raise ValueError("Every email must have a verified true_label.")

    if not set(key["email_source"]).issubset(
        {"ai_generated", "human_written", "unknown"}
    ):
        raise ValueError("Invalid email_source in answer key.")

    return key


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Private survey export not found: {INPUT_FILE}"
        )

    if not ANSWER_KEY_FILE.exists():
        raise FileNotFoundError(
            f"Answer key not found: {ANSWER_KEY_FILE}"
        )

    # Keep positional columns because Google Forms repeats question names.
    raw = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    if raw.shape[1] < 19:
        raise ValueError(
            f"Expected at least 19 columns, found {raw.shape[1]}."
        )

    # Remove completely empty trailing columns, if any.
    raw = raw.dropna(axis=1, how="all")

    if raw.shape[1] < 19:
        raise ValueError(
            "Required survey columns are missing after empty-column removal."
        )

    email_data = raw.iloc[:, EMAIL_START:EMAIL_END].copy()

    if email_data.shape[1] != EXPECTED_EMAILS:
        raise ValueError("Exactly 12 email questions are required.")

    email_data.columns = [
        f"email_{i:02d}" for i in range(1, EXPECTED_EMAILS + 1)
    ]

    # Create pseudonymous IDs; timestamps are not exported.
    email_data.insert(
        0,
        "participant_id",
        [f"P{i:03d}" for i in range(1, len(raw) + 1)]
    )

    metadata = pd.DataFrame({
        "participant_id": email_data["participant_id"],
        "age_group": raw.iloc[:, METADATA_COLUMNS["age_group"]],
        "cyber_knowledge": raw.iloc[:, METADATA_COLUMNS["cyber_knowledge"]],
        "phishing_experience": raw.iloc[
            :, METADATA_COLUMNS["phishing_experience"]
        ],
        "first_indicator": raw.iloc[
            :, METADATA_COLUMNS["first_indicator"]
        ],
        "confidence": raw.iloc[:, METADATA_COLUMNS["confidence"]],
    })

    for column in email_data.columns:
        if column != "participant_id":
            email_data[column] = email_data[column].apply(normalize_answer)

    invalid_values = []
    for column in email_data.columns:
        if column == "participant_id":
            continue

        original = raw.iloc[:, EMAIL_START + int(column.split("_")[1]) - 1]
        normalized = email_data[column]

        invalid = original.notna() & original.astype(str).str.strip().ne("")
        invalid &= normalized.isna()

        if invalid.any():
            invalid_values.extend(original[invalid].astype(str).unique().tolist())

    if invalid_values:
        raise ValueError(
            f"Unrecognized answer options: {sorted(set(invalid_values))}"
        )

    long_data = email_data.melt(
        id_vars="participant_id",
        var_name="email_id",
        value_name="predicted_label"
    )

    long_data = long_data.merge(
        metadata,
        on="participant_id",
        how="left",
        validate="many_to_one"
    )

    answer_key = load_answer_key(ANSWER_KEY_FILE)

    long_data = long_data.merge(
        answer_key,
        on="email_id",
        how="left",
        validate="many_to_one"
    )

    long_data["is_correct"] = (
        long_data["predicted_label"] == long_data["true_label"]
    )

    long_data.loc[
        long_data["predicted_label"].isna(), "is_correct"
    ] = pd.NA

    # Quality checks
    n_participants = long_data["participant_id"].nunique()
    n_rows = len(long_data)
    n_missing = int(long_data["predicted_label"].isna().sum())

    expected_rows = n_participants * EXPECTED_EMAILS

    if n_rows != expected_rows:
        raise ValueError("Unexpected number of participant-email records.")

    if long_data.duplicated(["participant_id", "email_id"]).any():
        raise ValueError("Duplicate participant-email records detected.")

    # Per-email aggregate results
    email_summary = (
        long_data.groupby(
            ["email_id", "true_label", "email_source"],
            dropna=False
        )
        .agg(
            total_responses=("predicted_label", "count"),
            phishing_selections=(
                "predicted_label",
                lambda x: (x == "phishing").sum()
            ),
            legitimate_selections=(
                "predicted_label",
                lambda x: (x == "legitimate").sum()
            ),
            correct_responses=("is_correct", "sum"),
        )
        .reset_index()
    )

    email_summary["accuracy_percent"] = (
        email_summary["correct_responses"]
        / email_summary["total_responses"]
        * 100
    )

    email_summary["phishing_selection_percent"] = (
        email_summary["phishing_selections"]
        / email_summary["total_responses"]
        * 100
    )

    # Overall confusion matrix counts
    valid = long_data.dropna(
        subset=["predicted_label", "true_label"]
    )

    tp = int(
        (
            (valid["true_label"] == "phishing")
            & (valid["predicted_label"] == "phishing")
        ).sum()
    )
    fn = int(
        (
            (valid["true_label"] == "phishing")
            & (valid["predicted_label"] == "legitimate")
        ).sum()
    )
    fp = int(
        (
            (valid["true_label"] == "legitimate")
            & (valid["predicted_label"] == "phishing")
        ).sum()
    )
    tn = int(
        (
            (valid["true_label"] == "legitimate")
            & (valid["predicted_label"] == "legitimate")
        ).sum()
    )

    def ratio(num, den):
        return num / den if den else float("nan")

    accuracy = ratio(tp + tn, tp + tn + fp + fn)
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    fpr = ratio(fp, fp + tn)
    f1 = ratio(
        2 * precision * recall,
        precision + recall
    ) if precision + recall else float("nan")

    overall_metrics = pd.DataFrame([
        ["Accuracy", tp + tn, tp + tn + fp + fn, accuracy],
        ["Precision", tp, tp + fp, precision],
        ["Phishing Recall", tp, tp + fn, recall],
        ["Specificity", tn, tn + fp, specificity],
        ["False Positive Rate", fp, fp + tn, fpr],
        ["F1-score", 2 * tp, 2 * tp + fp + fn, f1],
    ], columns=["metric", "numerator", "denominator", "value"])

    # Recall by phishing authorship group
    phishing_only = valid[valid["true_label"] == "phishing"]

    source_metrics = (
        phishing_only.groupby("email_source")
        .apply(
            lambda group: pd.Series({
                "correct": (
                    group["predicted_label"] == "phishing"
                ).sum(),
                "total": len(group),
                "recall": (
                    group["predicted_label"] == "phishing"
                ).mean(),
            }),
            include_groups=False
        )
        .reset_index()
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Participant-level data remains local and is gitignored.
    long_data.to_csv(
        OUTPUT_DIR / "student_responses_long.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Publish only aggregate outputs.
    email_summary.to_csv(
        OUTPUT_DIR / "email_classification_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    overall_metrics.to_csv(
        OUTPUT_DIR / "overall_metrics_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    source_metrics.to_csv(
        OUTPUT_DIR / "phishing_source_metrics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("SURVEY PROCESSING COMPLETED")
    print(f"Participants: {n_participants}")
    print(f"Email questions: {EXPECTED_EMAILS}")
    print(f"Total classifications: {n_rows}")
    print(f"Missing classifications: {n_missing}")
    print(f"Valid classifications: {len(valid)}")
    print()
    print(overall_metrics.to_string(index=False))
    print()
    print(source_metrics.to_string(index=False))
    print()
    print(f"Aggregate results saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
