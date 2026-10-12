import csv
import json
import math
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]


def main():
    config_path = ROOT / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    input_path = ROOT / config["input_path"]
    output_path = ROOT / config["output_path"]

    conditions = config["phishing_conditions"]
    expected_conditions = {"ai_phishing", "human_phishing"}

    if (
        not isinstance(conditions, list)
        or len(conditions) != 2
        or set(conditions) != expected_conditions
    ):
        raise ValueError("Expected AI and human phishing conditions.")

    threshold = float(config["max_false_positive_rate"])

    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("FPR threshold must be between 0 and 1.")

    required = {
        "participant_id",
        "email_id",
        "email_type",
        "predicted_label",
        "response_time_seconds",
        "confidence",
    }

    with input_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []

        if len(headers) != len(set(headers)):
            raise ValueError("Duplicate CSV column names.")

        if not required.issubset(set(headers)):
            raise ValueError("Missing required CSV columns.")

        rows = list(reader)

    if not rows:
        raise ValueError("The dataset is empty.")

    allowed_types = expected_conditions | {"legitimate"}
    seen_responses = set()
    email_categories = {}

    for line_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"Extra CSV values at line {line_number}.")

        for field in required:
            value = row.get(field)

            if value is None or not value.strip():
                raise ValueError(
                    f"Missing {field} at CSV line {line_number}."
                )

            row[field] = value.strip()

        response_id = (row["participant_id"], row["email_id"])

        if response_id in seen_responses:
            raise ValueError(
                f"Duplicate participant-email response at line {line_number}."
            )

        seen_responses.add(response_id)

        if row["email_type"] not in allowed_types:
            raise ValueError(
                f"Invalid email type at line {line_number}."
            )

        if row["predicted_label"] not in {"phishing", "legitimate"}:
            raise ValueError(
                f"Invalid prediction at line {line_number}."
            )

        email_id = row["email_id"]
        email_type = row["email_type"]

        if (
            email_id in email_categories
            and email_categories[email_id] != email_type
        ):
            raise ValueError(
                f"Inconsistent category for email {email_id}."
            )

        email_categories[email_id] = email_type

        try:
            seconds = float(row["response_time_seconds"])
            confidence = int(row["confidence"])
        except ValueError as error:
            raise ValueError(
                f"Invalid numeric value at line {line_number}."
            ) from error

        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError(
                f"Response time must be positive at line {line_number}."
            )

        if not 1 <= confidence <= 5:
            raise ValueError(
                f"Confidence must be from 1 to 5 at line {line_number}."
            )

        row["response_time_seconds"] = seconds
        row["confidence"] = confidence

    metrics = {}

    for condition in conditions:
        subset = [
            row for row in rows
            if row["email_type"] == condition
        ]

        if not subset:
            raise ValueError(f"No records for {condition}.")

        true_positives = sum(
            row["predicted_label"] == "phishing"
            for row in subset
        )

        false_negatives = len(subset) - true_positives
        recall = true_positives / len(subset)

        metrics[condition] = {
            "responses": len(subset),
            "true_positives": true_positives,
            "false_negatives": false_negatives,
            "recall": recall,
            "false_negative_rate": 1 - recall,
            "mean_response_time_seconds": mean(
                row["response_time_seconds"] for row in subset
            ),
            "mean_confidence": mean(
                row["confidence"] for row in subset
            ),
        }

    legitimate = [
        row for row in rows
        if row["email_type"] == "legitimate"
    ]

    if not legitimate:
        raise ValueError(
            "Legitimate records are required to calculate FPR."
        )

    false_positives = sum(
        row["predicted_label"] == "phishing"
        for row in legitimate
    )

    false_positive_rate = false_positives / len(legitimate)

    result = {
        "dataset_kind": config["dataset_kind"],
        "total_responses": len(rows),
        "participants": len({
            row["participant_id"] for row in rows
        }),
        "invalid_rows": 0,
        "metrics": metrics,
        "recall_difference_ai_minus_human": (
            metrics["ai_phishing"]["recall"]
            - metrics["human_phishing"]["recall"]
        ),
        "legitimate_responses": len(legitimate),
        "legitimate_false_positives": false_positives,
        "legitimate_false_positive_rate": false_positive_rate,
        "fpr_guardrail_threshold": threshold,
        "fpr_guardrail_passed": false_positive_rate <= threshold,
        "note": (
            "Descriptive response-level metrics only. "
            "No hypothesis test performed."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = json.dumps(result, indent=2, allow_nan=False)
    output_path.write_text(output + "\n", encoding="utf-8")

    print(output)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
