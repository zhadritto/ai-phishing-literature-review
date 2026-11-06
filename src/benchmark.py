
from __future__ import annotations

import json
import os
import platform
import sys
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "config" / "benchmark_config.yaml"

EXPECTED_METHODS = {"baseline", "proposed"}

VALID_LABELS = {"phishing", "legitimate"}

PHISHING_SOURCES = {
    "ai_generated",
    "human_written",
}


# ==========================================================
# LOAD CONFIGURATION
# ==========================================================

def load_config():

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Benchmark configuration not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("Invalid benchmark configuration.")

    project = config.get("project", {})
    benchmark = config.get("benchmark", {})
    workload = config.get("workload", {})
    output = config.get("output", {})

    methods = set(benchmark.get("methods", []))

    if methods != EXPECTED_METHODS:
        raise ValueError(
            "Methods must contain baseline and proposed."
        )

    load_sizes = benchmark.get("load_sizes", [])

    if not load_sizes or any(
        not isinstance(size, int) or size < 1
        for size in load_sizes
    ):
        raise ValueError("Invalid benchmark load sizes.")

    warmup_runs = benchmark.get("warmup_runs")
    evaluation_runs = benchmark.get("evaluation_runs")

    if not isinstance(warmup_runs, int) or warmup_runs < 1:
        raise ValueError("warmup_runs must be positive.")

    if (
        not isinstance(evaluation_runs, int)
        or evaluation_runs < 2
    ):
        raise ValueError("evaluation_runs must be at least 2.")

    confidence_level = benchmark.get(
        "confidence_level",
        0.95
    )

    if not 0 < confidence_level < 1:
        raise ValueError("Invalid confidence level.")

    phishing_probability = workload.get(
        "phishing_probability",
        0.5
    )

    legitimate_probability = workload.get(
        "legitimate_probability",
        0.5
    )

    if not np.isclose(
        phishing_probability + legitimate_probability,
        1.0
    ):
        raise ValueError(
            "Workload probabilities must sum to 1."
        )

    raw_output = ROOT / output.get(
        "raw_logs",
        "data/raw/test_run.jsonl"
    )

    return {
        "name": project.get("name", "Data Processing Benchmark"),
        "seed": int(project.get("random_seed", 42)),
        "methods": ["baseline", "proposed"],
        "load_sizes": load_sizes,
        "warmup_runs": warmup_runs,
        "evaluation_runs": evaluation_runs,
        "phishing_probability": phishing_probability,
        "legitimate_probability": legitimate_probability,
        "include_missing": workload.get(
            "include_missing_values", True
        ),
        "include_invalid": workload.get(
            "include_invalid_values", True
        ),
        "output_file": raw_output,
    }


# ==========================================================
# SYNTHETIC WORKLOAD GENERATION
# ==========================================================

def generate_workload(
    size: int,
    rng: np.random.Generator,
    config: dict
) -> pd.DataFrame:
    """
    Generate synthetic classification records.

    These records are used only for benchmarking
    the data-processing implementations.

    They are not survey responses or research findings.
    """

    phishing_mask = (
        rng.random(size)
        < config["phishing_probability"]
    )

    true_labels = np.where(
        phishing_mask,
        "phishing",
        "legitimate"
    )

    email_sources = np.full(
        size,
        "unknown",
        dtype=object
    )

    ai_ids = ["email_01", "email_05", "email_09"]
    human_ids = ["email_03", "email_07", "email_11"]
    legitimate_ids = [
        "email_02",
        "email_04",
        "email_06",
        "email_08",
        "email_10",
        "email_12",
    ]

    email_ids = []

    for index in range(size):

        if true_labels[index] == "phishing":

            if rng.random() < 0.5:
                email_sources[index] = "ai_generated"
                email_ids.append(
                    rng.choice(ai_ids)
                )
            else:
                email_sources[index] = "human_written"
                email_ids.append(
                    rng.choice(human_ids)
                )

        else:
            email_ids.append(
                rng.choice(legitimate_ids)
            )

    # Synthetic predictions:
    # These probabilities are workload-generation parameters,
    # not measurements of actual student performance.
    correct_mask = rng.random(size) < 0.80

    predicted_labels = np.where(
        correct_mask,
        true_labels,
        np.where(
            true_labels == "phishing",
            "legitimate",
            "phishing"
        )
    ).astype(object)

    # Include missing predictions as an edge case.
    if config["include_missing"] and size >= 100:
        missing_count = max(1, int(size * 0.01))

        missing_indices = rng.choice(
            size,
            size=missing_count,
            replace=False
        )

        predicted_labels[missing_indices] = None

    # Include malformed labels as another edge case.
    if config["include_invalid"] and size >= 100:
        available = np.array([
            index
            for index in range(size)
            if predicted_labels[index] is not None
        ])

        invalid_count = max(1, int(size * 0.005))

        invalid_indices = rng.choice(
            available,
            size=min(invalid_count, len(available)),
            replace=False
        )

        predicted_labels[invalid_indices] = "invalid_label"

    return pd.DataFrame({
        "participant_id": [
            f"P{i + 1:06d}" for i in range(size)
        ],
        "email_id": email_ids,
        "true_label": true_labels,
        "predicted_label": predicted_labels,
        "email_source": email_sources,
    })


# ==========================================================
# BASELINE IMPLEMENTATION
# ==========================================================

def aggregate_baseline(data: pd.DataFrame) -> dict:
    """
    Reference implementation using a Python loop.

    Missing and invalid predictions are counted separately.
    """

    result = {
        "TP": 0,
        "TN": 0,
        "FP": 0,
        "FN": 0,
        "missing_predictions": 0,
        "invalid_predictions": 0,
        "source_counts": {
            source: {"TP": 0, "FN": 0}
            for source in sorted(PHISHING_SOURCES)
        }
    }

    for row in data.itertuples(index=False):

        actual = row.true_label
        predicted = row.predicted_label
        source = row.email_source

        if predicted is None or pd.isna(predicted):
            result["missing_predictions"] += 1
            continue

        predicted = str(predicted).strip().lower()

        if predicted == "":
            result["missing_predictions"] += 1
            continue

        if predicted not in VALID_LABELS:
            result["invalid_predictions"] += 1
            continue

        if actual == "phishing":

            if predicted == "phishing":
                result["TP"] += 1

                if source in PHISHING_SOURCES:
                    result["source_counts"][source]["TP"] += 1

            else:
                result["FN"] += 1

                if source in PHISHING_SOURCES:
                    result["source_counts"][source]["FN"] += 1

        elif actual == "legitimate":

            if predicted == "legitimate":
                result["TN"] += 1

            else:
                result["FP"] += 1

        else:
            raise ValueError(
                f"Unexpected true label: {actual}"
            )

    result["valid_classifications"] = (
        result["TP"]
        + result["TN"]
        + result["FP"]
        + result["FN"]
    )

    return result


# ==========================================================
# PROPOSED IMPLEMENTATION
# ==========================================================

def aggregate_proposed(data: pd.DataFrame) -> dict:
    """
    Optimized implementation using Pandas vectorized operations.

    It performs the same task as the baseline implementation.
    """

    actual = (
        data["true_label"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    predicted = (
        data["predicted_label"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    source = (
        data["email_source"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    missing_mask = (
        predicted.isna()
        | predicted.eq("").fillna(False)
    )

    valid_mask = predicted.isin(
        VALID_LABELS
    ).fillna(False)

    invalid_mask = (
        ~missing_mask
        & ~valid_mask
    )

    evaluable = (
        valid_mask
        & actual.isin(VALID_LABELS).fillna(False)
    )

    actual_phishing = actual.eq("phishing")
    actual_legitimate = actual.eq("legitimate")

    predicted_phishing = predicted.eq("phishing")
    predicted_legitimate = predicted.eq("legitimate")

    tp = int(
        (
            evaluable
            & actual_phishing
            & predicted_phishing
        ).sum()
    )

    fn = int(
        (
            evaluable
            & actual_phishing
            & predicted_legitimate
        ).sum()
    )

    tn = int(
        (
            evaluable
            & actual_legitimate
            & predicted_legitimate
        ).sum()
    )

    fp = int(
        (
            evaluable
            & actual_legitimate
            & predicted_phishing
        ).sum()
    )

    source_counts = {}

    for email_source in sorted(PHISHING_SOURCES):

        source_mask = (
            evaluable
            & actual_phishing
            & source.eq(email_source)
        )

        source_counts[email_source] = {
            "TP": int(
                (source_mask & predicted_phishing).sum()
            ),
            "FN": int(
                (source_mask & predicted_legitimate).sum()
            )
        }

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "missing_predictions": int(missing_mask.sum()),
        "invalid_predictions": int(invalid_mask.sum()),
        "valid_classifications": tp + tn + fp + fn,
        "source_counts": source_counts,
    }


# ==========================================================
# OUTPUT VALIDATION
# ==========================================================

def validate_methods(data: pd.DataFrame):
    """
    Confirm that baseline and proposed implementations
    return exactly the same analytical results.
    """

    baseline_result = aggregate_baseline(data)
    proposed_result = aggregate_proposed(data)

    if baseline_result != proposed_result:
        raise ValueError(
            "Baseline and proposed implementations "
            "produced different results."
        )

    return baseline_result


# ==========================================================
# ENVIRONMENT METADATA
# ==========================================================

def get_environment_metadata():

    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
    }


# ==========================================================
# EXECUTION MEASUREMENT
# ==========================================================

def measure_execution(
    function,
    data: pd.DataFrame,
    method: str,
    load_size: int,
    phase: str,
    repetition: int,
    run_id: str,
    environment: dict,
) -> dict:
    """
    Measure only the target function execution.

    JSON serialization and file writing occur afterwards,
    outside the timed interval.
    """

    start_ns = time.perf_counter_ns()

    success = True
    error_message = None
    result = None

    try:
        result = function(data)

    except Exception as error:

        success = False

        error_message = (
            f"{type(error).__name__}: {str(error)[:400]}"
        )

    end_ns = time.perf_counter_ns()

    duration_ms = (
        end_ns - start_ns
    ) / 1_000_000

    record = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": method,
        "load_size": load_size,
        "phase": phase,
        "repetition": repetition,
        "duration_ms": round(duration_ms, 6),
        "success": success,
        "error": error_message,
        "input_records": len(data),
        "TP": None,
        "TN": None,
        "FP": None,
        "FN": None,
        "missing_predictions": None,
        "invalid_predictions": None,
        **environment,
    }

    if success:

        record.update({
            "TP": result["TP"],
            "TN": result["TN"],
            "FP": result["FP"],
            "FN": result["FN"],
            "missing_predictions": (
                result["missing_predictions"]
            ),
            "invalid_predictions": (
                result["invalid_predictions"]
            ),
        })

    return record


# ==========================================================
# BENCHMARK EXECUTION
# ==========================================================

def run_benchmark(config: dict):

    rng = np.random.default_rng(
        config["seed"]
    )

    environment = get_environment_metadata()

    run_id = uuid.uuid4().hex[:12]

    functions = {
        "baseline": aggregate_baseline,
        "proposed": aggregate_proposed,
    }

    records = []

    print("=" * 60)
    print("DATA PROCESSING PERFORMANCE BENCHMARK")
    print("=" * 60)

    print("Run ID:", run_id)
    print("Python:", environment["python_version"])
    print("Platform:", environment["platform"])
    print("CPU count:", environment["cpu_count"])

    print("\nValidating implementations...")

    for load_size in config["load_sizes"]:

        workload = generate_workload(
            load_size,
            rng,
            config
        )

        # Do not benchmark methods unless outputs match.
        validate_methods(workload)

    print("Baseline and proposed results match.")

    for load_size in config["load_sizes"]:

        print(f"\nProcessing load size: {load_size}")

        workload = generate_workload(
            load_size,
            rng,
            config
        )

        # --------------------------
        # Warm-up phase
        # --------------------------

        for method in config["methods"]:

            function = functions[method]

            for repetition in range(
                1,
                config["warmup_runs"] + 1
            ):

                record = measure_execution(
                    function=function,
                    data=workload,
                    method=method,
                    load_size=load_size,
                    phase="warmup",
                    repetition=repetition,
                    run_id=run_id,
                    environment=environment,
                )

                records.append(record)

        # --------------------------
        # Evaluation phase
        # --------------------------

        # Alternate execution order to reduce
        # systematic order-related bias.
        for repetition in range(
            1,
            config["evaluation_runs"] + 1
        ):

            order = list(config["methods"])

            if repetition % 2 == 0:
                order.reverse()

            for method in order:

                record = measure_execution(
                    function=functions[method],
                    data=workload,
                    method=method,
                    load_size=load_size,
                    phase="benchmark",
                    repetition=repetition,
                    run_id=run_id,
                    environment=environment,
                )

                records.append(record)

        print("Warm-up and evaluation completed.")

    return records


# ==========================================================
# SAVE JSONL LOGS
# ==========================================================

def save_logs(records, output_file: Path):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    allow_nan=False
                )
                + "\n"
            )

    print("\nJSONL logs saved to:")
    print(output_file)


# ==========================================================
# MAIN
# ==========================================================

def main():

    config = load_config()

    records = run_benchmark(config)

    save_logs(
        records,
        config["output_file"]
    )

    total_runs = len(records)

    failed_runs = sum(
        not record["success"]
        for record in records
    )

    successful_runs = (
        total_runs - failed_runs
    )

    warmup_count = sum(
        record["phase"] == "warmup"
        for record in records
    )

    benchmark_count = sum(
        record["phase"] == "benchmark"
        for record in records
    )

    print("\nFINAL BENCHMARK SUMMARY")

    print("Total runs:", total_runs)
    print("Warm-up runs:", warmup_count)
    print("Evaluation runs:", benchmark_count)
    print("Successful runs:", successful_runs)
    print("Failed runs:", failed_runs)

    error_rate = (
        failed_runs / total_runs * 100
        if total_runs else 0
    )

    print(f"Execution error rate: {error_rate:.2f}%")

    if failed_runs:
        print(
            "WARNING: Some benchmark executions failed. "
            "Review the JSONL error records."
        )
    else:
        print("All benchmark executions completed successfully.")


if __name__ == "__main__":
    main()
