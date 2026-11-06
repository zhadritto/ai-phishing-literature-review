
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "config" / "benchmark_config.yaml"

EXPECTED_METHODS = ["baseline", "proposed"]

REQUIRED_COLUMNS = {
    "run_id",
    "method",
    "load_size",
    "phase",
    "repetition",
    "duration_ms",
    "success",
    "error",
    "input_records",
    "missing_predictions",
    "invalid_predictions",
}


# ==========================================================
# LOAD CONFIGURATION
# ==========================================================

def load_config():
    """Load benchmark settings from YAML."""

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    benchmark = config.get("benchmark", {})
    output = config.get("output", {})

    methods = benchmark.get("methods", [])

    if set(methods) != set(EXPECTED_METHODS):
        raise ValueError(
            "Configuration must define baseline and proposed methods."
        )

    load_sizes = benchmark.get("load_sizes", [])

    if not load_sizes:
        raise ValueError("No benchmark load sizes configured.")

    iterations = int(
        benchmark.get("bootstrap_iterations", 5000)
    )

    confidence_level = float(
        benchmark.get("confidence_level", 0.95)
    )

    if iterations < 100:
        raise ValueError(
            "At least 100 bootstrap iterations are recommended."
        )

    if not 0 < confidence_level < 1:
        raise ValueError("Invalid confidence level.")

    return {
        "methods": methods,
        "load_sizes": load_sizes,
        "expected_evaluation_runs": int(
            benchmark["evaluation_runs"]
        ),
        "bootstrap_iterations": iterations,
        "confidence_level": confidence_level,
        "random_seed": int(
            config.get("project", {}).get(
                "random_seed", 42
            )
        ),
        "raw_file": ROOT / output["raw_logs"],
        "summary_file": ROOT / output["processed_metrics"],
        "bootstrap_file": (
            ROOT / "data" / "processed"
            / "bootstrap_summary.csv"
        ),
        "speedup_file": (
            ROOT / "data" / "processed"
            / "speedup_summary.csv"
        ),
        "error_file": (
            ROOT / "data" / "processed"
            / "benchmark_error_summary.csv"
        ),
    }


# ==========================================================
# LOAD JSONL DATA
# ==========================================================

def load_jsonl(file_path: Path) -> pd.DataFrame:
    """
    Read JSONL logs.

    Every non-empty line must contain one valid JSON object.
    Malformed lines stop processing instead of being silently dropped.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Benchmark log not found: {file_path}"
        )

    records = []

    with file_path.open(encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON at line {line_number}: {error}"
                ) from error

            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} must contain a JSON object."
                )

            records.append(record)

    if not records:
        raise ValueError("JSONL file contains no records.")

    return pd.DataFrame(records)


# ==========================================================
# VALIDATE DATA
# ==========================================================

def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate benchmark log structure and values."""

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = data.copy()

    for column in ["method", "phase"]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    invalid_methods = (
        ~df["method"].isin(EXPECTED_METHODS)
    )

    if invalid_methods.any():
        raise ValueError("Unexpected benchmark method found.")

    invalid_phases = (
        ~df["phase"].isin(["warmup", "benchmark"])
    )

    if invalid_phases.any():
        raise ValueError("Unexpected benchmark phase found.")

    df["load_size"] = pd.to_numeric(
        df["load_size"],
        errors="coerce"
    )

    df["repetition"] = pd.to_numeric(
        df["repetition"],
        errors="coerce"
    )

    df["duration_ms"] = pd.to_numeric(
        df["duration_ms"],
        errors="coerce"
    )

    if df[
        ["load_size", "repetition", "duration_ms"]
    ].isna().any().any():
        raise ValueError(
            "Missing or invalid numeric benchmark values."
        )

    if (
        ~np.isfinite(df["duration_ms"])
    ).any():
        raise ValueError(
            "Non-finite duration values detected."
        )

    if (df["duration_ms"] < 0).any():
        raise ValueError(
            "Negative execution duration detected."
        )

    for column in [
        "success",
        "input_records",
        "missing_predictions",
        "invalid_predictions"
    ]:

        if column not in df.columns:
            raise ValueError(
                f"Missing field: {column}"
            )

    if df["success"].isna().any():
        raise ValueError(
            "Missing success status."
        )

    if not df["success"].map(
        lambda value: isinstance(value, (bool, np.bool_))
    ).all():
        raise ValueError(
            "The success field must contain Boolean values."
        )

    for column in [
        "input_records",
        "missing_predictions",
        "invalid_predictions"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if df[column].isna().any():
            raise ValueError(
                f"Invalid numeric values in {column}."
            )

    if (
        df["missing_predictions"]
        + df["invalid_predictions"]
        > df["input_records"]
    ).any():
        raise ValueError(
            "Missing and invalid records exceed input size."
        )

    if df.duplicated(
        [
            "run_id",
            "method",
            "load_size",
            "phase",
            "repetition"
        ]
    ).any():
        raise ValueError(
            "Duplicate benchmark measurements detected."
        )

    return df


# ==========================================================
# BOOTSTRAP CONFIDENCE INTERVAL
# ==========================================================

def bootstrap_ci(
    values,
    iterations=5000,
    confidence_level=0.95,
    seed=42,
    statistic="mean"
):
    """
    Calculate a percentile bootstrap confidence interval.

    Resampling unit: individual benchmark run.
    """

    values = np.asarray(
        values,
        dtype=float
    )

    values = values[
        np.isfinite(values)
    ]

    if len(values) < 2:
        return np.nan, np.nan

    rng = np.random.default_rng(seed)

    samples = rng.choice(
        values,
        size=(iterations, len(values)),
        replace=True
    )

    if statistic == "mean":
        estimates = samples.mean(axis=1)

    elif statistic == "median":
        estimates = np.median(samples, axis=1)

    else:
        raise ValueError(
            "Statistic must be mean or median."
        )

    alpha = 1 - confidence_level

    lower, upper = np.quantile(
        estimates,
        [
            alpha / 2,
            1 - alpha / 2
        ]
    )

    return float(lower), float(upper)


# ==========================================================
# SUMMARIZE ONE BENCHMARK GROUP
# ==========================================================

def summarize_group(
    group,
    method,
    load_size,
    config,
    seed
):
    """Calculate latency and quality metrics for one group."""

    total_attempts = len(group)

    successful = group[
        group["success"]
    ]

    failed = group[
        ~group["success"]
    ]

    successful_count = len(successful)
    failed_count = len(failed)

    durations = successful[
        "duration_ms"
    ].to_numpy(dtype=float)

    if successful_count:

        mean_ms = float(np.mean(durations))
        std_ms = float(
            np.std(durations, ddof=1)
        ) if successful_count > 1 else np.nan

        median_ms = float(np.median(durations))

        p25 = float(
            np.percentile(durations, 25)
        )

        p75 = float(
            np.percentile(durations, 75)
        )

        p95 = float(
            np.percentile(durations, 95)
        )

        p99 = float(
            np.percentile(durations, 99)
        )

        mean_ci_lower, mean_ci_upper = bootstrap_ci(
            durations,
            iterations=config["bootstrap_iterations"],
            confidence_level=config["confidence_level"],
            seed=seed,
            statistic="mean"
        )

        median_ci_lower, median_ci_upper = bootstrap_ci(
            durations,
            iterations=config["bootstrap_iterations"],
            confidence_level=config["confidence_level"],
            seed=seed + 1,
            statistic="median"
        )

    else:

        mean_ms = np.nan
        std_ms = np.nan
        median_ms = np.nan
        p25 = np.nan
        p75 = np.nan
        p95 = np.nan
        p99 = np.nan
        mean_ci_lower = np.nan
        mean_ci_upper = np.nan
        median_ci_lower = np.nan
        median_ci_upper = np.nan

    if total_attempts:

        error_rate = (
            failed_count / total_attempts
        )

        success_rate = (
            successful_count / total_attempts
        )

        expected_runs = config["expected_evaluation_runs"]

        missing_input_rate = (
            group["missing_predictions"].sum()
            / group["input_records"].sum()
            if group["input_records"].sum() else np.nan
        )

        invalid_input_rate = (
            group["invalid_predictions"].sum()
            / group["input_records"].sum()
            if group["input_records"].sum() else np.nan
        )

    else:

        error_rate = np.nan
        success_rate = np.nan
        expected_runs = config["expected_evaluation_runs"]
        missing_input_rate = np.nan
        invalid_input_rate = np.nan

    return {
        "method": method,
        "load_size": load_size,
        "evaluation_attempts": total_attempts,
        "expected_evaluation_runs": expected_runs,
        "successful_runs": successful_count,
        "failed_runs": failed_count,
        "run_count_complete": (
            total_attempts == expected_runs
        ),
        "success_rate": success_rate,
        "error_rate": error_rate,
        "missing_input_rate": missing_input_rate,
        "invalid_input_rate": invalid_input_rate,
        "mean_ms": mean_ms,
        "std_ms": std_ms,
        "median_ms": median_ms,
        "p25_ms": p25,
        "p75_ms": p75,
        "p95_ms": p95,
        "p99_ms": p99,
        "mean_ci_lower_ms": mean_ci_lower,
        "mean_ci_upper_ms": mean_ci_upper,
        "median_ci_lower_ms": median_ci_lower,
        "median_ci_upper_ms": median_ci_upper
    }


# ==========================================================
# CALCULATE SUMMARY TABLE
# ==========================================================

def calculate_summary(data, config):
    """
    Filter warm-up runs and calculate evaluation statistics.

    Failed evaluation attempts remain included in the error-rate
    denominator. Only successful runs contribute to latency
    distribution statistics.
    """

    evaluation = data[
        data["phase"] == "benchmark"
    ].copy()

    warmup = data[
        data["phase"] == "warmup"
    ].copy()

    if evaluation.empty:
        raise ValueError(
            "No evaluation runs found."
        )

    rows = []

    for method, load_size in product(
        config["methods"],
        config["load_sizes"]
    ):

        group = evaluation[
            (evaluation["method"] == method)
            & (evaluation["load_size"] == load_size)
        ].copy()

        rows.append(
            summarize_group(
                group=group,
                method=method,
                load_size=load_size,
                config=config,
                seed=config["random_seed"] + int(load_size)
            )
        )

    summary = pd.DataFrame(rows)

    # Warm-up counts are reported separately and
    # never enter latency summary calculations.
    warmup_summary = (
        warmup.groupby(
            ["method", "load_size"]
        )
        .size()
        .rename("warmup_runs_excluded")
        .reset_index()
    )

    summary = summary.merge(
        warmup_summary,
        on=["method", "load_size"],
        how="left"
    )

    summary["warmup_runs_excluded"] = (
        summary["warmup_runs_excluded"]
        .fillna(0)
        .astype(int)
    )

    return summary


# ==========================================================
# COMPARE BASELINE AND PROPOSED
# ==========================================================

def calculate_speedup(data, config):
    """
    Calculate paired speedup.

    Speedup > 1 means proposed is faster than baseline.
    """

    evaluation = data[
        (data["phase"] == "benchmark")
        & data["success"]
    ].copy()

    results = []

    for load_size in config["load_sizes"]:

        group = evaluation[
            evaluation["load_size"] == load_size
        ]

        durations = group.pivot(
            index="repetition",
            columns="method",
            values="duration_ms"
        )

        if not {
            "baseline",
            "proposed"
        }.issubset(durations.columns):

            ratios = np.array([])

        else:

            valid = durations.dropna(
                subset=["baseline", "proposed"]
            )

            ratios = (
                valid["baseline"]
                / valid["proposed"]
            ).to_numpy(dtype=float)

        if len(ratios) >= 2:

            median_speedup = float(
                np.median(ratios)
            )

            lower, upper = bootstrap_ci(
                ratios,
                iterations=config["bootstrap_iterations"],
                confidence_level=config["confidence_level"],
                seed=config["random_seed"] + load_size + 100,
                statistic="median"
            )

        elif len(ratios) == 1:

            median_speedup = float(ratios[0])
            lower = np.nan
            upper = np.nan

        else:

            median_speedup = np.nan
            lower = np.nan
            upper = np.nan

        results.append({
            "load_size": load_size,
            "paired_successful_runs": len(ratios),
            "median_speedup": median_speedup,
            "ci_lower": lower,
            "ci_upper": upper
        })

    return pd.DataFrame(results)


# ==========================================================
# ERROR SUMMARY
# ==========================================================

def create_error_summary(data):
    """
    Keep failed attempts visible as a separate guardrail report.
    """

    failed = data[
        (data["phase"] == "benchmark")
        & (~data["success"])
    ].copy()

    if failed.empty:

        return pd.DataFrame(
            columns=[
                "method",
                "load_size",
                "error",
                "failed_runs"
            ]
        )

    failed["error"] = (
        failed["error"]
        .fillna("Unspecified error")
        .astype(str)
    )

    return (
        failed.groupby(
            ["method", "load_size", "error"]
        )
        .size()
        .reset_index(name="failed_runs")
    )


# ==========================================================
# SAVE OUTPUT FILES
# ==========================================================

def save_outputs(
    summary,
    speedup,
    errors,
    config
):

    output_file = config["summary_file"]

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    speedup.to_csv(
        config["speedup_file"],
        index=False,
        encoding="utf-8-sig"
    )

    errors.to_csv(
        config["error_file"],
        index=False,
        encoding="utf-8-sig"
    )

    print("\nOUTPUT FILES")
    print(output_file)
    print(config["speedup_file"])
    print(config["error_file"])


# ==========================================================
# MAIN
# ==========================================================

def main():

    config = load_config()

    print("=" * 65)
    print("BENCHMARK DATA PROCESSING")
    print("=" * 65)

    print("\nLoading JSONL logs...")

    data = load_jsonl(
        config["raw_file"]
    )

    print("Raw measurements:", len(data))

    data = validate_data(data)

    print("\nPhase distribution:")
    print(
        data["phase"].value_counts().to_string()
    )

    print("\nMethod distribution:")
    print(
        data["method"].value_counts().to_string()
    )

    print("\nFiltering warm-up runs...")

    evaluation = data[
        data["phase"] == "benchmark"
    ]

    excluded = len(data) - len(evaluation)

    print("Warm-up records excluded:", excluded)
    print("Evaluation records retained:", len(evaluation))

    print("\nCalculating statistical metrics...")

    summary = calculate_summary(
        data,
        config
    )

    speedup = calculate_speedup(
        data,
        config
    )

    errors = create_error_summary(
        data
    )

    print("\nBENCHMARK SUMMARY")

    print(
        summary.to_string(index=False)
    )

    print("\nPAIRED SPEEDUP")

    print(
        speedup.to_string(index=False)
    )

    print("\nERROR SUMMARY")

    if errors.empty:
        print("No failed evaluation runs.")
    else:
        print(errors.to_string(index=False))

    save_outputs(
        summary,
        speedup,
        errors,
        config
    )

    print("\nPROCESSING COMPLETED")


if __name__ == "__main__":
    main()
