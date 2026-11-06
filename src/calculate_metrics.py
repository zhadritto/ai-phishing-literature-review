
from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "processed" / "student_responses_long.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"

POSITIVE_LABEL = "phishing"
NEGATIVE_LABEL = "legitimate"

PHISHING_SOURCES = [
    "ai_generated",
    "human_written",
]

BOOTSTRAP_ITERATIONS = 5000
RANDOM_SEED = 42
CONFIDENCE_LEVEL = 0.95


# ==========================================================
# DATA VALIDATION
# ==========================================================

def validate_classification_data(data):
    """
    Validate participant predictions and email ground truth.

    Missing predictions are retained in the dataset
    but excluded from classification metrics.
    """

    required = {
        "participant_id",
        "email_id",
        "true_label",
        "predicted_label",
        "email_source",
    }

    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = data.copy()

    for column in [
        "participant_id",
        "email_id",
        "true_label",
        "predicted_label",
        "email_source",
    ]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    if df["participant_id"].isna().any():
        raise ValueError("Missing participant identifiers.")

    if df["true_label"].isna().any():
        raise ValueError("Missing ground-truth labels.")

    if df["email_source"].isna().any():
        raise ValueError("Missing email source metadata.")

    invalid_truth = (
        ~df["true_label"].isin(
            [POSITIVE_LABEL, NEGATIVE_LABEL]
        )
    )

    if invalid_truth.any():
        raise ValueError("Invalid ground-truth labels detected.")

    invalid_source = (
        ~df["email_source"].isin(
            PHISHING_SOURCES + ["unknown"]
        )
    )

    if invalid_source.any():
        raise ValueError("Invalid email source categories.")

    invalid_predictions = (
        df["predicted_label"].notna()
        & ~df["predicted_label"].isin(
            [POSITIVE_LABEL, NEGATIVE_LABEL]
        )
    )

    if invalid_predictions.any():
        raise ValueError("Invalid participant predictions detected.")

    if df.duplicated(
        ["participant_id", "email_id"]
    ).any():
        raise ValueError(
            "Duplicate participant-email observations detected."
        )

    # Recalculate correctness instead of trusting a stored column.
    df["is_correct"] = (
        df["predicted_label"] == df["true_label"]
    ).astype("boolean")

    return df


# ==========================================================
# CONFUSION MATRIX
# ==========================================================

def calculate_confusion_matrix(data):
    """
    Calculate TP, TN, FP and FN.

    Positive class: phishing.
    Negative class: legitimate.
    """

    df = validate_classification_data(data)

    valid = df.dropna(
        subset=["predicted_label"]
    )

    actual = valid["true_label"]
    predicted = valid["predicted_label"]

    tp = int(
        (
            (actual == POSITIVE_LABEL)
            & (predicted == POSITIVE_LABEL)
        ).sum()
    )

    tn = int(
        (
            (actual == NEGATIVE_LABEL)
            & (predicted == NEGATIVE_LABEL)
        ).sum()
    )

    fp = int(
        (
            (actual == NEGATIVE_LABEL)
            & (predicted == POSITIVE_LABEL)
        ).sum()
    )

    fn = int(
        (
            (actual == POSITIVE_LABEL)
            & (predicted == NEGATIVE_LABEL)
        ).sum()
    )

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Valid_Classifications": tp + tn + fp + fn,
        "Missing_Predictions": int(
            df["predicted_label"].isna().sum()
        ),
    }


# ==========================================================
# SAFE DIVISION
# ==========================================================

def safe_divide(numerator, denominator):

    if denominator == 0:
        return np.nan

    return numerator / denominator


# ==========================================================
# CLASSIFICATION METRICS
# ==========================================================

def calculate_classification_metrics(data):
    """
    Calculate overall classification metrics.
    """

    cm = calculate_confusion_matrix(data)

    tp = cm["TP"]
    tn = cm["TN"]
    fp = cm["FP"]
    fn = cm["FN"]

    accuracy = safe_divide(
        tp + tn,
        tp + tn + fp + fn
    )

    precision = safe_divide(
        tp,
        tp + fp
    )

    recall = safe_divide(
        tp,
        tp + fn
    )

    specificity = safe_divide(
        tn,
        tn + fp
    )

    false_positive_rate = safe_divide(
        fp,
        fp + tn
    )

    f1_score = safe_divide(
        2 * precision * recall,
        precision + recall
    ) if pd.notna(precision) and pd.notna(recall) else np.nan

    return {
        **cm,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "Specificity": specificity,
        "False_Positive_Rate": false_positive_rate,
        "F1_Score": f1_score,
    }


# ==========================================================
# METRIC CALCULATION FOR BOOTSTRAP
# ==========================================================

def get_metric_value(data, metric):
    """
    Calculate one metric from a participant-resampled dataset.
    """

    df = data.dropna(
        subset=["predicted_label"]
    )

    if df.empty:
        return np.nan

    actual = df["true_label"]
    predicted = df["predicted_label"]

    tp = int(
        (
            (actual == POSITIVE_LABEL)
            & (predicted == POSITIVE_LABEL)
        ).sum()
    )

    tn = int(
        (
            (actual == NEGATIVE_LABEL)
            & (predicted == NEGATIVE_LABEL)
        ).sum()
    )

    fp = int(
        (
            (actual == NEGATIVE_LABEL)
            & (predicted == POSITIVE_LABEL)
        ).sum()
    )

    fn = int(
        (
            (actual == POSITIVE_LABEL)
            & (predicted == NEGATIVE_LABEL)
        ).sum()
    )

    metrics = {
        "accuracy": safe_divide(
            tp + tn,
            tp + tn + fp + fn
        ),
        "precision": safe_divide(
            tp,
            tp + fp
        ),
        "recall": safe_divide(
            tp,
            tp + fn
        ),
        "specificity": safe_divide(
            tn,
            tn + fp
        ),
        "f1": safe_divide(
            2 * tp,
            2 * tp + fp + fn
        ),
    }

    if metric not in metrics:
        raise ValueError(
            f"Unsupported bootstrap metric: {metric}"
        )

    return metrics[metric]


# ==========================================================
# PARTICIPANT-LEVEL BOOTSTRAP CI
# ==========================================================

def bootstrap_participant_ci(
    data,
    metric,
    iterations=BOOTSTRAP_ITERATIONS,
    seed=RANDOM_SEED,
):
    """
    Calculate a percentile 95% bootstrap confidence interval.

    Entire participants are sampled with replacement.
    All responses belonging to each selected participant
    remain together in each bootstrap sample.
    """

    df = validate_classification_data(data)

    participants = df[
        "participant_id"
    ].dropna().unique()

    if len(participants) < 2:
        raise ValueError(
            "At least two participants are required."
        )

    participant_groups = {
        participant: group
        for participant, group in df.groupby(
            "participant_id"
        )
    }

    rng = np.random.default_rng(seed)

    estimates = []

    for _ in range(iterations):

        selected = rng.choice(
            participants,
            size=len(participants),
            replace=True,
        )

        sampled_data = pd.concat(
            [
                participant_groups[participant]
                for participant in selected
            ],
            ignore_index=True,
        )

        value = get_metric_value(
            sampled_data,
            metric,
        )

        if pd.notna(value):
            estimates.append(value)

    if len(estimates) < iterations * 0.90:
        raise ValueError(
            "Too many invalid bootstrap estimates."
        )

    alpha = 1 - CONFIDENCE_LEVEL

    lower, upper = np.quantile(
        estimates,
        [
            alpha / 2,
            1 - alpha / 2,
        ],
    )

    estimate = get_metric_value(
        df,
        metric,
    )

    return {
        "metric": metric,
        "estimate": estimate,
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "confidence_level": CONFIDENCE_LEVEL,
        "participants": len(participants),
        "bootstrap_iterations": len(estimates),
    }


# ==========================================================
# SOURCE-SPECIFIC PHISHING RECALL
# ==========================================================

def calculate_source_recall(data):
    """
    Compare recall for AI-generated and human-written phishing.

    Only verified phishing examples are included.
    Each participant contributes a group-level recall.
    """

    df = validate_classification_data(data)

    phishing = df[
        (df["true_label"] == POSITIVE_LABEL)
        & (df["email_source"].isin(PHISHING_SOURCES))
        & df["predicted_label"].notna()
    ].copy()

    phishing["detected_correctly"] = (
        phishing["predicted_label"] == POSITIVE_LABEL
    ).astype(int)

    results = []

    for source in PHISHING_SOURCES:

        subset = phishing[
            phishing["email_source"] == source
        ].copy()

        if subset.empty:

            results.append({
                "email_source": source,
                "participants": 0,
                "valid_classifications": 0,
                "correct_detections": 0,
                "recall": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan,
            })

            continue

        # Pooled recall for descriptive reporting.
        correct = int(
            subset["detected_correctly"].sum()
        )

        total = len(subset)

        pooled_recall = correct / total

        # Each participant's recall is calculated separately.
        participant_recall = (
            subset.groupby("participant_id")
            ["detected_correctly"]
            .mean()
        )

        values = participant_recall.to_numpy(
            dtype=float
        )

        rng = np.random.default_rng(RANDOM_SEED)

        if len(values) >= 2:

            samples = rng.choice(
                values,
                size=(BOOTSTRAP_ITERATIONS, len(values)),
                replace=True,
            )

            bootstrap_means = samples.mean(axis=1)

            lower, upper = np.quantile(
                bootstrap_means,
                [0.025, 0.975],
            )

        else:
            lower = np.nan
            upper = np.nan

        results.append({
            "email_source": source,
            "participants": len(values),
            "valid_classifications": total,
            "correct_detections": correct,
            "recall": pooled_recall,
            "participant_mean_recall": float(values.mean()),
            "ci_lower": lower,
            "ci_upper": upper,
        })

    return pd.DataFrame(results)


# ==========================================================
# SAVE METRIC RESULTS
# ==========================================================

def save_results(
    metrics,
    confidence_intervals,
    source_results,
    confusion_matrix,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame([metrics]).to_csv(
        OUTPUT_DIR / "classification_metrics.csv",
        index=False,
    )

    pd.DataFrame(
        confidence_intervals
    ).to_csv(
        OUTPUT_DIR / "classification_confidence_intervals.csv",
        index=False,
    )

    source_results.to_csv(
        OUTPUT_DIR / "phishing_source_metrics.csv",
        index=False,
    )

    pd.DataFrame([
        confusion_matrix
    ]).to_csv(
        OUTPUT_DIR / "confusion_matrix.csv",
        index=False,
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed survey data not found: {INPUT_FILE}"
        )

    print("=" * 60)
    print("CLASSIFICATION METRICS ANALYSIS")
    print("=" * 60)

    data = pd.read_csv(INPUT_FILE)

    data = validate_classification_data(data)

    print(
        "Participants:",
        data["participant_id"].nunique()
    )

    print(
        "Total records:",
        len(data)
    )

    print(
        "Valid predictions:",
        data["predicted_label"].notna().sum()
    )

    print(
        "Missing predictions:",
        data["predicted_label"].isna().sum()
    )

    # Overall metrics
    confusion_matrix = calculate_confusion_matrix(data)

    metrics = calculate_classification_metrics(data)

    # Overall participant-level bootstrap intervals
    confidence_intervals = []

    for metric in [
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
    ]:

        ci = bootstrap_participant_ci(
            data,
            metric=metric,
        )

        confidence_intervals.append(ci)

    # AI vs Human phishing comparison
    source_results = calculate_source_recall(data)

    # Save outputs
    save_results(
        metrics,
        confidence_intervals,
        source_results,
        confusion_matrix,
    )

    print("\nCONFUSION MATRIX")

    for key, value in confusion_matrix.items():
        print(f"{key}: {value}")

    print("\nCLASSIFICATION METRICS")

    for key, value in metrics.items():

        if isinstance(value, (float, np.floating)):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    print("\n95% CONFIDENCE INTERVALS")

    print(
        pd.DataFrame(
            confidence_intervals
        ).to_string(index=False)
    )

    print("\nAI VS HUMAN PHISHING")

    print(
        source_results.to_string(index=False)
    )

    print("\nResults saved in:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
