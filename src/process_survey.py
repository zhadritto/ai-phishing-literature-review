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

# IMPORTANT: Confirm these positional indices match the exact column headers 
# of the original private survey export before running against real data.
EMAIL_COLUMNS = list(range(5, 17))


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

if len(df.columns) < 18:
    raise ValueError(
        "The CSV must contain at least 18 columns."
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

# IMPORTANT: Confirm these positional indices match the exact column headers 
# of the original private survey export before running against real data.
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

    answer = str(value).strip().casefold()

    exact_map = {
        "настоящее письмо": "legitimate",
        "легитимное": "legitimate",
        "легитимное письмо": "legitimate",
        "не фишинговое": "legitimate",
        "нефишинговое": "legitimate",
        "нет": "legitimate",
        "фишинговое": "phishing",
        "фишинговое письмо": "phishing",
        "фишинг": "phishing",
        "да": "phishing",
    }

    if answer in exact_map:
        return exact_map[answer]

    # Check negative wording before the substring "фишинг".
    if "не" in answer and "фишинг" in answer:
        return "legitimate"

    if "легитим" in answer or "настоящее" in answer:
        return "legitimate"

    if "фишинг" in answer:
        return "phishing"

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

ground_truth_complete = bool(
    long_data["true_label"].notna().all()
    and long_data["email_source"].notna().all()
    and long_data["email_source"].astype("string").str.strip().ne("").all()
)

predictions_complete = bool(
    long_data["predicted_label"].notna().all()
)

if ground_truth_complete and predictions_complete:
    long_data["is_correct"] = (
        long_data["predicted_label"] == long_data["true_label"]
    )
else:
    print()
    print(
        "NOTE: A complete verified answer key, source mapping, and response set "
        "are required. Accuracy will not be calculated."
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
