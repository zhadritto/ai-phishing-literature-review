
from pathlib import Path

import pandas as pd


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "responses.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

EXPECTED_EMAILS = 12
MIN_COLUMNS = 19

EMAIL_START = 5
EMAIL_END = 17

METADATA_COLUMNS = {
    "age_group": 2,
    "cyber_knowledge": 3,
    "phishing_experience": 4,
    "first_indicator": 17,
    "confidence": 18,
}


# ==========================================================
# ALLOWED ANSWER OPTIONS
# ==========================================================

VALID_EMAIL_ANSWERS = {
    "фишинговое письмо",
    "настоящее письмо",
}

VALID_AGE_GROUPS = {
    "до 18 лет",
    "18-20 лет",
    "21-23 года",
    "24 года и старше",
}

VALID_KNOWLEDGE = {
    "низкие",
    "средние",
    "высокие",
}

VALID_EXPERIENCE = {
    "да, и я сразу распознал(а) их",
    "да, но распознал(а) не сразу",
    "нет",
    "не уверен(а)",
}

VALID_INDICATORS = {
    "адрес отправителя",
    "ссылки и вложения",
    "срочность и угрозы",
    "запрос личных или банковских данных",
    "грамматические ошибки и стиль текста",
    "другой признак",
}


# ==========================================================
# TEXT NORMALIZATION
# ==========================================================

def normalize_text(value):
    """Normalize text without changing its meaning."""

    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .casefold()
        .replace("ё", "е")
        .replace("–", "-")
        .replace("—", "-")
        .replace("\u00a0", " ")
    )


# ==========================================================
# REPORT HELPER
# ==========================================================

def add_check(report, name, value, status="PASS", details=""):
    """Add one validation result to the quality report."""

    report.append({
        "check": name,
        "value": value,
        "status": status,
        "details": details,
    })


# ==========================================================
# LOAD SURVEY DATA
# ==========================================================

def load_survey():
    """Load the original Google Forms CSV export."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Survey file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig",
    )

    if df.empty:
        raise ValueError(
            "The survey file contains no participant records."
        )

    if len(df.columns) < MIN_COLUMNS:
        raise ValueError(
            f"Expected at least {MIN_COLUMNS} columns, "
            f"found {len(df.columns)}."
        )

    if EMAIL_END > len(df.columns):
        raise ValueError(
            "The 12 email-question columns are missing."
        )

    return df


# ==========================================================
# INSPECT EMAIL CLASSIFICATION ANSWERS
# ==========================================================

def inspect_email_answers(df):
    """Validate all 12 email classification columns."""

    email_data = df.iloc[
        :, EMAIL_START:EMAIL_END
    ].copy()

    if email_data.shape[1] != EXPECTED_EMAILS:
        raise ValueError(
            f"Expected {EXPECTED_EMAILS} email questions, "
            f"found {email_data.shape[1]}."
        )

    results = []

    total_missing = 0
    total_invalid = 0

    for index, column in enumerate(email_data.columns):

        values = email_data[column].apply(normalize_text)

        missing = int(values.eq("").sum())

        invalid = int(
            (
                values.ne("")
                & ~values.isin(VALID_EMAIL_ANSWERS)
            ).sum()
        )

        phishing = int(
            values.eq("фишинговое письмо").sum()
        )

        legitimate = int(
            values.eq("настоящее письмо").sum()
        )

        valid_count = phishing + legitimate

        total_missing += missing
        total_invalid += invalid

        results.append({
            "email_id": f"email_{index + 1:02d}",
            "phishing_selections": phishing,
            "legitimate_selections": legitimate,
            "valid_answers": valid_count,
            "missing_answers": missing,
            "invalid_answers": invalid,
        })

    return (
        pd.DataFrame(results),
        total_missing,
        total_invalid,
    )


# ==========================================================
# INSPECT CATEGORICAL METADATA
# ==========================================================

def inspect_category(
    series,
    column_name,
    allowed_values,
):
    """Check missing and invalid categorical values."""

    values = series.apply(normalize_text)

    missing = int(values.eq("").sum())

    invalid_values = values[
        values.ne("")
        & ~values.isin(allowed_values)
    ]

    invalid = len(invalid_values)

    return {
        "variable": column_name,
        "total_records": len(values),
        "valid_values": len(values) - missing - invalid,
        "missing_values": missing,
        "invalid_values": invalid,
        "invalid_examples": "; ".join(
            invalid_values.unique().tolist()
        ),
    }


# ==========================================================
# METADATA VALIDATION
# ==========================================================

def inspect_metadata(df):
    """Inspect demographic and additional survey variables."""

    report = []

    age = df.iloc[:, METADATA_COLUMNS["age_group"]]

    knowledge = df.iloc[
        :, METADATA_COLUMNS["cyber_knowledge"]
    ]

    experience = df.iloc[
        :, METADATA_COLUMNS["phishing_experience"]
    ]

    indicator = df.iloc[
        :, METADATA_COLUMNS["first_indicator"]
    ]

    # Age validation
    age_result = inspect_category(
        age,
        "age_group",
        VALID_AGE_GROUPS,
    )

    report.append(age_result)

    # Cybersecurity knowledge validation
    knowledge_result = inspect_category(
        knowledge,
        "cyber_knowledge",
        VALID_KNOWLEDGE,
    )

    report.append(knowledge_result)

    # Previous phishing experience validation
    experience_result = inspect_category(
        experience,
        "phishing_experience",
        VALID_EXPERIENCE,
    )

    report.append(experience_result)

    # First detection indicator validation
    indicator_result = inspect_category(
        indicator,
        "first_indicator",
        VALID_INDICATORS,
    )

    report.append(indicator_result)

    # Confidence validation
    confidence_raw = df.iloc[
        :, METADATA_COLUMNS["confidence"]
    ]

    confidence_text = confidence_raw.apply(normalize_text)

    confidence_numeric = pd.to_numeric(
        confidence_raw.where(confidence_text.ne("")),
        errors="coerce",
    )

    confidence_missing = int(
        confidence_text.eq("").sum()
    )

    confidence_invalid_format = int(
        (
            confidence_text.ne("")
            & confidence_numeric.isna()
        ).sum()
    )

    confidence_out_of_range = int(
        (
            confidence_numeric.notna()
            & ~confidence_numeric.between(1, 5)
        ).sum()
    )

    report.append({
        "variable": "confidence",
        "total_records": len(df),
        "valid_values": int(
            confidence_numeric.between(1, 5).sum()
        ),
        "missing_values": confidence_missing,
        "invalid_values": (
            confidence_invalid_format
            + confidence_out_of_range
        ),
        "invalid_examples": "Values outside 1-5 or non-numeric",
    })

    category_report = pd.DataFrame(report)

    return category_report, confidence_numeric


# ==========================================================
# CREATE AGGREGATED CATEGORY SUMMARY
# ==========================================================

def create_category_summary(df):
    """Create anonymous frequency tables for survey categories."""

    categories = {
        "age_group": (
            METADATA_COLUMNS["age_group"],
            VALID_AGE_GROUPS,
        ),
        "cyber_knowledge": (
            METADATA_COLUMNS["cyber_knowledge"],
            VALID_KNOWLEDGE,
        ),
        "phishing_experience": (
            METADATA_COLUMNS["phishing_experience"],
            VALID_EXPERIENCE,
        ),
        "first_indicator": (
            METADATA_COLUMNS["first_indicator"],
            VALID_INDICATORS,
        ),
    }

    results = []

    for variable, (column_index, allowed) in categories.items():

        values = df.iloc[:, column_index].apply(normalize_text)

        values = values.replace("", "missing")

        for category, count in values.value_counts().items():

            results.append({
                "variable": variable,
                "category": category,
                "participants": int(count),
                "percentage": round(
                    count / len(df) * 100,
                    2,
                ),
                "category_is_valid": (
                    category == "missing"
                    or category in allowed
                ),
            })

    return pd.DataFrame(results)


# ==========================================================
# MAIN QUALITY INSPECTION
# ==========================================================

def main():

    print("=" * 60)
    print("SURVEY DATA QUALITY INSPECTION")
    print("=" * 60)

    df = load_survey()

    report = []

    # ------------------------------------------------------
    # General dataset information
    # ------------------------------------------------------

    add_check(
        report,
        "Number of participant records",
        len(df),
    )

    add_check(
        report,
        "Number of dataset columns",
        len(df.columns),
    )

    add_check(
        report,
        "Number of email questions",
        EXPECTED_EMAILS,
    )

    duplicate_rows = int(df.duplicated().sum())

    add_check(
        report,
        "Exact duplicate rows",
        duplicate_rows,
        "WARNING" if duplicate_rows else "PASS",
    )

    # Timestamps are checked but are never printed or exported.
    timestamps = df.iloc[:, 0]

    missing_timestamps = int(timestamps.isna().sum())

    duplicate_timestamps = int(
        timestamps.duplicated(keep=False).sum()
    )

    add_check(
        report,
        "Missing timestamps",
        missing_timestamps,
    )

    add_check(
        report,
        "Rows with duplicated timestamps",
        duplicate_timestamps,
        "WARNING" if duplicate_timestamps else "PASS",
        "Timestamp duplicates require manual review; "
        "they are not automatically treated as duplicate participants.",
    )

    # ------------------------------------------------------
    # Email answer inspection
    # ------------------------------------------------------

    email_summary, missing, invalid = inspect_email_answers(df)

    add_check(
        report,
        "Total possible classifications",
        len(df) * EXPECTED_EMAILS,
    )

    add_check(
        report,
        "Missing email answers",
        missing,
        "WARNING" if missing else "PASS",
    )

    add_check(
        report,
        "Invalid email answers",
        invalid,
        "FAIL" if invalid else "PASS",
    )

    # ------------------------------------------------------
    # Metadata inspection
    # ------------------------------------------------------

    metadata_report, confidence = inspect_metadata(df)

    for _, row in metadata_report.iterrows():

        add_check(
            report,
            f"Missing values: {row['variable']}",
            int(row["missing_values"]),
            (
                "WARNING"
                if row["missing_values"] > 0
                else "PASS"
            ),
        )

        add_check(
            report,
            f"Invalid values: {row['variable']}",
            int(row["invalid_values"]),
            (
                "FAIL"
                if row["invalid_values"] > 0
                else "PASS"
            ),
            str(row["invalid_examples"]),
        )

    # ------------------------------------------------------
    # Final report generation
    # ------------------------------------------------------

    quality_report = pd.DataFrame(report)

    category_summary = create_category_summary(df)

    confidence_summary = pd.DataFrame([{
        "total_participants": len(df),
        "completed_confidence": int(confidence.notna().sum()),
        "missing_confidence": int(confidence.isna().sum()),
        "mean_confidence": (
            round(confidence.mean(), 2)
            if confidence.notna().any()
            else None
        ),
    }])

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    quality_report.to_csv(
        OUTPUT_DIR / "data_quality_report.csv",
        index=False,
        encoding="utf-8-sig",
    )

    email_summary.to_csv(
        OUTPUT_DIR / "email_response_quality.csv",
        index=False,
        encoding="utf-8-sig",
    )

    metadata_report.to_csv(
        OUTPUT_DIR / "metadata_quality_report.csv",
        index=False,
        encoding="utf-8-sig",
    )

    category_summary.to_csv(
        OUTPUT_DIR / "metadata_category_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    confidence_summary.to_csv(
        OUTPUT_DIR / "confidence_quality_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # ------------------------------------------------------
    # Display anonymous results only
    # ------------------------------------------------------

    print("\nGENERAL DATA QUALITY")
    print(quality_report.to_string(index=False))

    print("\nEMAIL RESPONSE QUALITY")
    print(email_summary.to_string(index=False))

    print("\nMETADATA QUALITY")
    print(metadata_report.to_string(index=False))

    print("\nCONFIDENCE SUMMARY")
    print(confidence_summary.to_string(index=False))

    failed = (
        quality_report["status"] == "FAIL"
    ).any()

    print("\nFINAL STATUS")

    if failed:
        print("WARNING: Data validation issues were detected.")
        print("Review the reports before proceeding.")
    else:
        print("No invalid values detected by the current checks.")

    print("\nInspection reports saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
