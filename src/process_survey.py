
import csv
import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_CSV = ROOT / "data/raw/responses.csv"
ANSWER_KEY = ROOT / "data/raw/email_answer_key.csv"
OUTPUT_DIR = ROOT / "data/processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

EXPECTED_PARTICIPANTS = 27
EXPECTED_EMAILS = 12

EMAIL_COLUMNS = list(range(5, 17))

ANSWER_MAP = {
    "настоящее письмо": "legitimate",
    "фишинговое": "phishing",
    "фишинговое письмо": "phishing",
    "фишинг": "phishing",
    "да": "phishing",

    "настоящее письмо": "legitimate",
    "легитимное": "legitimate",
    "легитимное письмо": "legitimate",
    "не фишинговое": "legitimate",
    "нефишинговое": "legitimate",
    "нет": "legitimate",
}


# --------------------------------------------------
# LOAD SURVEY
# --------------------------------------------------

if not INPUT_CSV.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_CSV}"
    )

df = pd.read_csv(INPUT_CSV)

print("SURVEY PROCESSING")
print("-----------------")
print("Participants:", len(df))
print("Columns:", len(df.columns))

if len(df) != EXPECTED_PARTICIPANTS:
    print(
        f"WARNING: Expected {EXPECTED_PARTICIPANTS} "
        f"participants, found {len(df)}."
    )

if len(df.columns) < 17:
    raise ValueError(
        "The CSV must contain at least 17 columns."
    )


# --------------------------------------------------
# EXTRACT EMAIL ANSWERS
# --------------------------------------------------

email_data = df.iloc[:, EMAIL_COLUMNS].copy()

email_data.columns = [
    f"email_{i:02d}"
    for i in range(1, EXPECTED_EMAILS + 1)
]

email_data.insert(
    0,
    "participant_id",
    [f"P{i:03d}" for i in range(1, len(df) + 1)]
)

if email_data.shape[1] - 1 != EXPECTED_EMAILS:
    raise ValueError(
        "Unexpected number of email questions."
    )


# --------------------------------------------------
# EXTRACT PARTICIPANT METADATA
# --------------------------------------------------

metadata = pd.DataFrame({
    "participant_id": email_data["participant_id"],
    "age_group": df.iloc[:, 2].astype("string"),
    "cyber_knowledge": df.iloc[:, 3].astype("string"),
    "phishing_experience": df.iloc[:, 4].astype("string"),
    "first_indicator": df.iloc[:, 17].astype("string"),
})


# --------------------------------------------------
# CONVERT ANSWERS TO STANDARD LABELS
# --------------------------------------------------

def normalize_answer(value):
    if pd.isna(value):
        return pd.NA

    answer = str(value).strip().lower()

    if answer in ANSWER_MAP:
        return ANSWER_MAP[answer]

    if "фишинг" in answer:
        return "phishing"

    if "легитим" in answer or "не фиш" in answer:
        return "legitimate"

    return pd.NA


for column in email_data.columns:
    if column != "participant_id":
        email_data[column] = email_data[column].apply(
            normalize_answer
        )


# --------------------------------------------------
# CONVERT WIDE DATA TO LONG FORMAT
# --------------------------------------------------

long_data = email_data.melt(
    id_vars=["participant_id"],
    var_name="email_id",
    value_name="predicted_label"
)

long_data = long_data.merge(
    metadata,
    on="participant_id",
    how="left"
)

long_data["true_label"] = pd.NA
long_data["email_source"] = pd.NA
long_data["is_correct"] = pd.NA


# --------------------------------------------------
# CREATE OR LOAD ANSWER KEY
# --------------------------------------------------

if not ANSWER_KEY.exists():

    answer_key = pd.DataFrame({
        "email_id": [
            f"email_{i:02d}"
            for i in range(1, EXPECTED_EMAILS + 1)
        ],
        "true_label": [""] * EXPECTED_EMAILS,
        "email_source": [""] * EXPECTED_EMAILS,
    })

    answer_key.to_csv(
        ANSWER_KEY,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("Created answer-key template:", ANSWER_KEY)

else:

    answer_key = pd.read_csv(
        ANSWER_KEY,
        dtype=str
    )

    required_columns = {
        "email_id",
        "true_label",
        "email_source",
    }

    missing_columns = (
        required_columns - set(answer_key.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Answer key is missing columns: {missing_columns}"
        )

    expected_ids = {
        f"email_{i:02d}"
        for i in range(1, EXPECTED_EMAILS + 1)
    }

    actual_ids = set(answer_key["email_id"].dropna())

    if actual_ids != expected_ids:
        raise ValueError(
            "Answer key must contain exactly "
            "email_01 through email_12."
        )

    if answer_key["email_id"].duplicated().any():
        raise ValueError(
            "Duplicate email_id values in answer key."
        )


# --------------------------------------------------
# VALIDATE ANSWER KEY
# --------------------------------------------------

answer_key["true_label"] = (
    answer_key["true_label"]
    .fillna("")
    .str.strip()
    .str.lower()
)

answer_key["email_source"] = (
    answer_key["email_source"]
    .fillna("")
    .str.strip()
)

valid_labels = {"phishing", "legitimate"}

filled_key = answer_key[
    answer_key["true_label"] != ""
]

invalid_labels = set(
    filled_key["true_label"]
) - valid_labels

if invalid_labels:
    raise ValueError(
        f"Invalid true_label values: {invalid_labels}"
    )


# --------------------------------------------------
# MERGE GROUND TRUTH
# --------------------------------------------------

long_data = long_data.merge(
    answer_key,
    on="email_id",
    how="left",
    suffixes=("", "_key")
)

long_data["true_label"] = (
    long_data["true_label_key"]
    .replace("", pd.NA)
)

long_data["email_source"] = (
    long_data["email_source_key"]
    .replace("", pd.NA)
)

long_data.drop(
    columns=["true_label_key", "email_source_key"],
    inplace=True
)

if long_data["true_label"].notna().all():

    long_data["is_correct"] = (
        long_data["predicted_label"]
        == long_data["true_label"]
    )

else:

    print()
    print(
        "NOTE: Ground-truth labels are incomplete. "
        "Accuracy will not be calculated."
    )


# --------------------------------------------------
# EMAIL CLASSIFICATION SUMMARY
# --------------------------------------------------

email_summary = (
    long_data
    .groupby(
        ["email_id", "predicted_label"],
        dropna=False
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

for label in ["phishing", "legitimate"]:
    if label not in email_summary.columns:
        email_summary[label] = 0

email_summary["total_responses"] = (
    email_summary["phishing"]
    + email_summary["legitimate"]
)

email_summary["phishing_percentage"] = (
    email_summary["phishing"]
    / email_summary["total_responses"]
    * 100
)


# --------------------------------------------------
# DEMOGRAPHICS SUMMARY
# --------------------------------------------------

demographic_frames = []

for column in [
    "age_group",
    "cyber_knowledge",
    "phishing_experience",
    "first_indicator",
]:

    summary = (
        metadata[column]
        .value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="count")
    )

    summary.insert(0, "variable", column)

    demographic_frames.append(summary)

demographics_summary = pd.concat(
    demographic_frames,
    ignore_index=True
)


# --------------------------------------------------
# SURVEY METRICS
# --------------------------------------------------

metrics = {
    "participants": len(df),
    "email_questions": EXPECTED_EMAILS,
    "total_classifications": len(long_data),
    "missing_answers": int(
        long_data["predicted_label"].isna().sum()
    ),
    "unique_participants": int(
        long_data["participant_id"].nunique()
    ),
    "unique_emails": int(
        long_data["email_id"].nunique()
    ),
    "ground_truth_complete": bool(
        long_data["true_label"].notna().all()
    ),
}

if metrics["ground_truth_complete"]:

    metrics["accuracy"] = float(
        long_data["is_correct"].mean()
    )

else:

    metrics["accuracy"] = None


# --------------------------------------------------
# SAVE OUTPUT FILES
# --------------------------------------------------

long_data.to_csv(
    OUTPUT_DIR / "student_responses_long.csv",
    index=False,
    encoding="utf-8-sig"
)

email_summary.to_csv(
    OUTPUT_DIR / "email_classification_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

demographics_summary.to_csv(
    OUTPUT_DIR / "survey_demographics_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(
    [metrics]
).to_csv(
    OUTPUT_DIR / "survey_metrics_summary.csv",
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# FINISH
# --------------------------------------------------

print()
print("SURVEY PROCESSING COMPLETED")
print("---------------------------")
print("Participants:", metrics["participants"])
print("Email questions:", EXPECTED_EMAILS)
print("Classifications:", metrics["total_classifications"])
print("Missing answers:", metrics["missing_answers"])
print("Ground truth complete:", metrics["ground_truth_complete"])
print("Accuracy:", metrics["accuracy"])

print()
print("FILES CREATED:")
print("- student_responses_long.csv")
print("- email_classification_summary.csv")
print("- survey_demographics_summary.csv")
print("- survey_metrics_summary.csv")

print()
print("Original survey CSV was not modified.")
