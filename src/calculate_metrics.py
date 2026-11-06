
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "student_responses_long.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

RANDOM_SEED = 42
BOOTSTRAP_ITERATIONS = 5000

POSITIVE_LABEL = "phishing"
NEGATIVE_LABEL = "legitimate"

PHISHING_SOURCES = [
    "ai_generated",
    "human_written"
]


def validate_classification_data(data):
    """
    Validate and normalize participant predictions
    and verified email labels.
    """

    required = {
        "participant_id",
        "email_id",
        "true_label",
        "predicted_label"
    }

    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = data.copy()

    for column in ["true_label", "predicted_label"]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # Exclude unanswered or unverified classifications.
    valid = df.dropna(
        subset=["true_label", "predicted_label"]
    ).copy()

    valid = valid[
        valid["true_label"].isin(
            [POSITIVE_LABEL, NEGATIVE_LABEL]
        )
        & valid["predicted_label"].isin(
            [POSITIVE_LABEL, NEGATIVE_LABEL]
        )
    ].copy()

    if valid.empty:
        raise ValueError(
            "No valid classifications available."
        )

    return valid


def calculate_confusion_matrix(data):
    """
    Calculate TP, TN, FP and FN.

    Positive class: phishing
    Negative class: legitimate
    """

    df = validate_classification_data(data)

    actual = df["true_label"]
    predicted = df["predicted_label"]

    tp = int(
        ((actual == POSITIVE_LABEL) &
         (predicted == POSITIVE_LABEL)).sum()
    )

    tn = int(
        ((actual == NEGATIVE_LABEL) &
         (predicted == NEGATIVE_LABEL)).sum()
    )

    fp = int(
        ((actual == NEGATIVE_LABEL) &
         (predicted == POSITIVE_LABEL)).sum()
    )

    fn = int(
        ((actual == POSITIVE_LABEL) &
         (predicted == NEGATIVE_LABEL)).sum()
    )

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Total": tp + tn + fp + fn
    }


def calculate_classification_metrics(data):
    """
    Calculate accuracy, precision, recall,
    specificity, false positive rate and F1-score.
    """

    cm = calculate_confusion_matrix(data)

    tp = cm["TP"]
    tn = cm["TN"]
    fp = cm["FP"]
    fn = cm["FN"]

    def safe_divide(numerator, denominator):
        if denominator == 0:
            return np.nan

        return numerator / denominator

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
    )

    return {
        "N_Classifications": cm["Total"],
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "Specificity": specificity,
        "False_Positive_Rate": false_positive_rate,
        "F1_Score": f1_score
    }


def bootstrap_participant_ci(
    data,
    metric,
    iterations=BOOTSTRAP_ITERATIONS,
    seed=RANDOM_SEED
):
    """
    Calculate a 95% bootstrap confidence interval.

    Resampling is performed at participant level,
    not at individual email-response level.

    metric must be the name of a numeric column.
    """

    required = {"participant_id", metric}

    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns for bootstrap: {sorted(missing)}"
        )

    if iterations < 1:
        raise ValueError(
            "Bootstrap iterations must be positive."
        )

    df = data[["participant_id", metric]].copy()

    df[metric] = pd.to_numeric(
        df[metric],
        errors="coerce"
    )

    # First calculate one metric value per participant.
    participant_values = (
        df.groupby("participant_id")[metric]
        .mean()
        .dropna()
        .to_numpy(dtype=float)
    )

    n = len(participant_values)

    if n == 0:
        raise ValueError(
            "No valid participant-level metric values."
        )

    estimate = float(participant_values.mean())

    # A confidence interval cannot be reliably estimated
    # from only one participant.
    if n < 2:
        return {
            "metric": metric,
            "n_participants": n,
            "estimate": estimate,
            "ci_lower": np.nan,
            "ci_upper": np.nan
        }

    rng = np.random.default_rng(seed)

    bootstrap_samples = rng.choice(
        participant_values,
        size=(iterations, n),
        replace=True
    )

    bootstrap_means = bootstrap_samples.mean(axis=1)

    ci_lower, ci_upper = np.percentile(
        bootstrap_means,
        [2.5, 97.5]
    )

    return {
        "metric": metric,
        "n_participants": n,
        "estimate": estimate,
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper)
    }


def calculate_source_recall(data):
    """
    Compare phishing detection recall for:

    1. AI-generated phishing
    2. Human-written phishing

    Each participant contributes one recall value
    per source group.
    """

    required = {
        "participant_id",
        "true_label",
        "predicted_label",
        "email_source"
    }

    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing source columns: {sorted(missing)}"
        )

    df = validate_classification_data(data)

    df["email_source"] = (
        data.loc[df.index, "email_source"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Select only verified phishing examples.
    phishing_data = df[
        (df["true_label"] == POSITIVE_LABEL)
        & (df["email_source"].isin(PHISHING_SOURCES))
    ].copy()

    phishing_data["detected_correctly"] = (
        phishing_data["predicted_label"] == POSITIVE_LABEL
    ).astype(float)

    results = []

    for source in PHISHING_SOURCES:

        subset = phishing_data[
            phishing_data["email_source"] == source
        ].copy()

        if subset.empty:
            results.append({
                "email_source": source,
                "participants": 0,
                "classifications": 0,
                "recall": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan
            })
            continue

        # Calculate recall separately for each participant.
        participant_recall = (
            subset.groupby("participant_id")
            ["detected_correctly"]
            .mean()
            .reset_index(name="recall")
        )

        ci = bootstrap_participant_ci(
            participant_recall,
            metric="recall",
            iterations=BOOTSTRAP_ITERATIONS,
            seed=RANDOM_SEED
        )

        results.append({
            "email_source": source,
            "participants": ci["n_participants"],
            "classifications": len(subset),
            "recall": ci["estimate"],
            "ci_lower": ci["ci_lower"],
            "ci_upper": ci["ci_upper"]
        })

    return pd.DataFrame(results)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed survey data not found: {INPUT_FILE}"
        )

    data = pd.read_csv(INPUT_FILE)

    print("=" * 55)
    print("PHISHING CLASSIFICATION ANALYSIS")
    print("=" * 55)

    confusion = calculate_confusion_matrix(data)

    metrics = calculate_classification_metrics(data)

    source_results = calculate_source_recall(data)

    print("\nCONFUSION MATRIX")
    print(pd.Series(confusion).to_string())

    print("\nCLASSIFICATION METRICS")

    for name, value in metrics.items():
        if isinstance(value, (float, np.floating)):
            print(f"{name}: {value:.4f}")
        else:
            print(f"{name}: {value}")

    print("\nAI VS HUMAN PHISHING")

    print(source_results.to_string(index=False))

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame([metrics]).to_csv(
        OUTPUT_DIR / "classification_metrics.csv",
        index=False
    )

    source_results.to_csv(
        OUTPUT_DIR / "phishing_source_metrics.csv",
        index=False
    )

    pd.DataFrame([confusion]).to_csv(
        OUTPUT_DIR / "confusion_matrix.csv",
        index=False
    )

    print("\nResults saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
