
from pathlib import Path

import pandas as pd


# ==================================================
# PROJECT PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "responses.csv"

ANSWER_KEY_FILE = (
    ROOT / "data" / "metadata" / "email_answer_key.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"

EXPECTED_EMAILS = 12

# Google Forms column positions (zero-based).
EMAIL_START = 5
EMAIL_END = 17

METADATA_COLUMNS = {
    "age_group": 2,
    "cyber_knowledge": 3,
    "phishing_experience": 4,
    "first_indicator": 17,
    "confidence": 18,
}


# ==================================================
# ANSWER NORMALIZATION
# ==================================================

def normalize_answer(value):
    """
    Normalize Russian Google Forms answers
    into standard English classification labels.
    """

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


# ==================================================
# LOAD AND VALIDATE ANSWER KEY
# ==================================================

def load_answer_key():

    if not ANSWER_KEY_FILE.exists():
        raise FileNotFoundError(
            f"Answer key not found: {ANSWER_KEY_FILE}"
        )

    key = pd.read_csv(
        ANSWER_KEY_FILE,
        dtype=str,
        keep_default_na=False
    )

    required = {
        "email_id",
        "true_label",
        "email_source"
    }

    if not required.issubset(key.columns):
        raise ValueError(
            f"Answer key must contain: {sorted(required)}"
        )

    key["email_id"] = key["email_id"].str.strip()

    key["true_label"] = (
        key["true_label"].str.strip().str.lower()
    )

    key["email_source"] = (
        key["email_source"].str.strip().str.lower()
    )

    expected_ids = {
        f"email_{i:02d}"
        for i in range(1, EXPECTED_EMAILS + 1)
    }

    if key["email_id"].duplicated().any():
        raise ValueError("Duplicate email IDs in answer key.")

    if set(key["email_id"]) != expected_ids:
        raise ValueError(
            "Answer key must contain exactly email_01 to email_12."
        )

    if not set(key["true_label"]).issubset(
        {"phishing", "legitimate"}
    ):
        raise ValueError("Invalid ground-truth labels.")

    if not set(key["email_source"]).issubset(
        {"ai_generated", "human_written", "unknown"}
    ):
        raise ValueError("Invalid email authorship categories.")

    if key[
        ["true_label", "email_source"]
    ].eq("").any().any():
        raise ValueError(
            "Ground truth and source fields cannot be empty."
        )

    # Verify the expected classification and authorship mapping.
    expected_mapping = {
        "email_01": ("phishing", "ai_generated"),
        "email_02": ("legitimate", "unknown"),
        "email_03": ("phishing", "human_written"),
        "email_04": ("legitimate", "unknown"),
        "email_05": ("phishing", "ai_generated"),
        "email_06": ("legitimate", "unknown"),
        "email_07": ("phishing", "human_written"),
        "email_08": ("legitimate", "unknown"),
        "email_09": ("phishing", "ai_generated"),
        "email_10": ("legitimate", "unknown"),
        "email_11": ("phishing", "human_written"),
        "email_12": ("legitimate", "unknown"),
    }

    for _, row in key.iterrows():

        expected = expected_mapping[row["email_id"]]

        actual = (
            row["true_label"],
            row["email_source"]
        )

        if actual != expected:
            raise ValueError(
                f"Incorrect mapping for {row['email_id']}: "
                f"{actual}; expected {expected}."
            )

    return key


# ==================================================
# LOAD RAW SURVEY
# ==================================================

def load_survey():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Survey file not found: {INPUT_FILE}"
        )

    # Duplicate Google Forms headings are handled by position,
    # not by column names.
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    if len(df.columns) < 19:
        raise ValueError(
            f"Expected at least 19 columns, found {len(df.columns)}."
        )

    if df.empty:
        raise ValueError("The survey file contains no participants.")

    return df


# ==================================================
# CREATE PARTICIPANT METADATA
# ==================================================

def extract_metadata(raw):

    metadata = pd.DataFrame()

    metadata["participant_id"] = [
        f"P{i:03d}"
        for i in range(1, len(raw) + 1)
    ]

    metadata["age_group"] = (
        raw.iloc[:, METADATA_COLUMNS["age_group"]]
    )

    metadata["cyber_knowledge"] = (
        raw.iloc[:, METADATA_COLUMNS["cyber_knowledge"]]
    )

    metadata["phishing_experience"] = (
        raw.iloc[:, METADATA_COLUMNS["phishing_experience"]]
    )

    metadata["first_indicator"] = (
        raw.iloc[:, METADATA_COLUMNS["first_indicator"]]
    )

    metadata["confidence"] = pd.to_numeric(
        raw.iloc[:, METADATA_COLUMNS["confidence"]],
        errors="coerce"
    )

    invalid_confidence = metadata["confidence"].notna() & (
        ~metadata["confidence"].between(1, 5)
    )

    if invalid_confidence.any():
        raise ValueError(
            "Confidence values must be between 1 and 5."
        )

    return metadata


# ==================================================
# VALIDATE SURVEY ANSWERS
# ==================================================

def extract_email_answers(raw):

    email_answers = raw.iloc[
        :,
        EMAIL_START:EMAIL_END
    ].copy()

    if email_answers.shape[1] != EXPECTED_EMAILS:
        raise ValueError(
            "The survey must contain exactly 12 email questions."
        )

    email_answers.columns = [
        f"email_{i:02d}"
        for i in range(1, EXPECTED_EMAILS + 1)
    ]

    for column in email_answers.columns:

        original = email_answers[column].copy()

        normalized = original.apply(normalize_answer)

        invalid = (
            original.notna()
            & original.astype(str).str.strip().ne("")
            & normalized.isna()
        )

        if invalid.any():

            invalid_values = (
                original[invalid].astype(str).unique().tolist()
            )

            raise ValueError(
                f"Unrecognized answers in {column}: "
                f"{invalid_values}"
            )

        email_answers[column] = normalized

    return email_answers


# ==================================================
# CONVERT WIDE DATA TO LONG FORMAT
# ==================================================

def convert_to_long_format(
    email_answers,
    metadata,
    answer_key
):

    email_answers = email_answers.copy()

    email_answers.insert(
        0,
        "participant_id",
        metadata["participant_id"]
    )

    long_data = email_answers.melt(
        id_vars=["participant_id"],
        var_name="email_id",
        value_name="predicted_label"
    )

    long_data = long_data.merge(
        metadata,
        on="participant_id",
        how="left",
        validate="many_to_one"
    )

    long_data = long_data.merge(
        answer_key,
        on="email_id",
        how="left",
        validate="many_to_one"
    )

    # Missing answers remain missing.
    long_data["is_correct"] = (
        long_data["predicted_label"]
        == long_data["true_label"]
    )

    long_data["is_correct"] = (
        long_data["is_correct"].astype("boolean")
    )

    long_data.loc[
        long_data["predicted_label"].isna(),
        "is_correct"
    ] = pd.NA

    return long_data


# ==================================================
# CREATE EMAIL SUMMARY
# ==================================================

def create_email_summary(long_data):

    results = []

    for email_id, group in long_data.groupby("email_id"):

        valid = group.dropna(
            subset=["predicted_label"]
        )

        total = len(valid)

        correct = int(
            valid["is_correct"].sum()
        ) if total else 0

        phishing_count = int(
            (valid["predicted_label"] == "phishing").sum()
        )

        legitimate_count = int(
            (valid["predicted_label"] == "legitimate").sum()
        )

        key_row = group.iloc[0]

        results.append({
            "email_id": email_id,
            "true_label": key_row["true_label"],
            "email_source": key_row["email_source"],
            "total_responses": total,
            "missing_responses": len(group) - total,
            "phishing_selections": phishing_count,
            "legitimate_selections": legitimate_count,
            "correct_responses": correct,
            "accuracy": (
                correct / total if total else pd.NA
            ),
            "accuracy_percent": (
                correct / total * 100 if total else pd.NA
            )
        })

    return pd.DataFrame(results).sort_values("email_id")


# ==================================================
# CREATE PARTICIPANT SUMMARY
# ==================================================

def create_participant_summary(long_data):

    valid = long_data.dropna(
        subset=["is_correct"]
    )

    summary = (
        valid.groupby("participant_id")
        .agg(
            valid_classifications=("is_correct", "count"),
            correct_classifications=("is_correct", "sum"),
            accuracy=("is_correct", "mean")
        )
        .reset_index()
    )

    return summary


# ==================================================
# CREATE DESCRIPTIVE SUMMARIES
# ==================================================

def create_category_summary(metadata, column):

    result = (
        metadata[column]
        .fillna("Missing")
        .value_counts()
        .rename_axis("category")
        .reset_index(name="participants")
    )

    result["percentage"] = (
        result["participants"]
        / len(metadata)
        * 100
    )

    return result


# ==================================================
# MAIN PROCESSING
# ==================================================

def main():

    print("Loading survey data...")

    raw = load_survey()

    answer_key = load_answer_key()

    metadata = extract_metadata(raw)

    email_answers = extract_email_answers(raw)

    long_data = convert_to_long_format(
        email_answers,
        metadata,
        answer_key
    )

    email_summary = create_email_summary(
        long_data
    )

    participant_summary = create_participant_summary(
        long_data
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Local participant-level dataset.
    # This file must remain private.
    long_data.to_csv(
        OUTPUT_DIR / "student_responses_long.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Approved aggregate outputs.
    email_summary.to_csv(
        OUTPUT_DIR / "email_classification_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    participant_summary.drop(
        columns=["participant_id"]
    ).describe().to_csv(
        OUTPUT_DIR / "participant_performance_summary.csv",
        encoding="utf-8-sig"
    )

    for column in [
        "age_group",
        "cyber_knowledge",
        "phishing_experience",
        "first_indicator"
    ]:

        create_category_summary(
            metadata,
            column
        ).to_csv(
            OUTPUT_DIR / f"{column}_summary.csv",
            index=False,
            encoding="utf-8-sig"
        )

    confidence_count = int(
        metadata["confidence"].notna().sum()
    )

    missing_answers = int(
        long_data["predicted_label"].isna().sum()
    )

    survey_summary = pd.DataFrame([{
        "participants": len(metadata),
        "email_questions": EXPECTED_EMAILS,
        "total_classifications": len(long_data),
        "valid_classifications": (
            long_data["predicted_label"].notna().sum()
        ),
        "missing_answers": missing_answers,
        "participants_with_confidence": confidence_count,
        "ground_truth_complete": (
            long_data["true_label"].notna().all()
        )
    }])

    survey_summary.to_csv(
        OUTPUT_DIR / "survey_metrics_summary.csv",
        index=False
    )

    print("\nPROCESSING COMPLETED")

    print("Participants:", len(metadata))
    print("Email questions:", EXPECTED_EMAILS)
    print("Total classifications:", len(long_data))
    print("Missing classifications:", missing_answers)
    print("Confidence responses:", confidence_count)

    print("\nEmail summary:")
    print(email_summary.to_string(index=False))

    print("\nAggregate outputs saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
