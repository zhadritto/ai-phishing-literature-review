
from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "benchmark_config.yaml"

EXPECTED_METHODS = ["baseline", "proposed"]
VALID_PHASES = {"warmup", "benchmark"}

REQUIRED_COLUMNS = {
    "run_id", "method", "load_size", "phase", "repetition",
    "duration_ms", "success", "error", "input_records",
    "missing_predictions", "invalid_predictions",
}


# ==========================================================
# LOAD CONFIGURATION
# ==========================================================

def load_config() -> dict[str, Any]:
    """Load and validate benchmark settings from YAML."""

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    benchmark = raw_config.get("benchmark", {})
    output = raw_config.get("output", {})

    methods = benchmark.get("methods", [])

    if set(methods) != set(EXPECTED_METHODS):
        raise ValueError(
            "Configuration must define exactly baseline and proposed methods."
        )

    load_sizes = benchmark.get("load_sizes", [])

    if (
        not load_sizes
        or any(
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 1
            for size in load_sizes
        )
        or len(load_sizes) != len(set(load_sizes))
    ):
        raise ValueError(
            "load_sizes must contain unique positive integers."
        )

    evaluation_runs = benchmark.get("evaluation_runs")

    if (
        not isinstance(evaluation_runs, int)
        or isinstance(evaluation_runs, bool)
        or evaluation_runs < 2
    ):
        raise ValueError(
            "evaluation_runs must be an integer of at least 2."
        )

    iterations = int(
        benchmark.get("bootstrap_iterations", 5000)
    )

    if iterations < 100:
        raise ValueError(
            "At least 100 bootstrap iterations are required."
        )

    confidence_level = float(
        benchmark.get("confidence_level", 0.95)
    )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if not {
        "raw_logs",
        "processed_metrics"
    }.issubset(output):
        raise ValueError(
            "Output configuration must define raw_logs and processed_metrics."
        )

    return {
        "methods": EXPECTED_METHODS.copy(),
        "load_sizes": load_sizes,
        "expected_evaluation_runs": evaluation_runs,
        "bootstrap_iterations": iterations,
        "confidence_level": confidence_level,
        "random_seed": int(
            raw_config.get("project", {}).get(
                "random_seed", 42
            )
        ),
        "raw_file": ROOT / output["raw_logs"],
        "summary_file": ROOT / output["processed_metrics"],
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
    """Read JSONL records without silently dropping malformed lines."""

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
                    f"JSONL line {line_number} must contain an object."
                )

            records.append(record)

    if not records:
        raise ValueError(
            "JSONL file contains no measurement records."
        )

    return pd.DataFrame(records)


# ==========================================================
# VALIDATE DATA
# ==========================================================

def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Validate logs.

    Counters may be null on failed runs if execution
    failed before the processing result was returned.
    """

    missing_columns = REQUIRED_COLUMNS - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df = data.copy()

    for column in ["run_id", "method", "phase"]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    if (
        df["run_id"].isna().any()
        or df["run_id"].eq("").any()
    ):
        raise ValueError("run_id cannot be empty.")

    df["method"] = df["method"].str.lower()
    df["phase"] = df["phase"].str.lower()

    if not df["method"].isin(EXPECTED_METHODS).all():
        raise ValueError(
            "Unexpected benchmark method found."
        )

    if not df["phase"].isin(VALID_PHASES).all():
        raise ValueError(
            "Unexpected benchmark phase found."
        )

    # Validate numeric measurement fields.
    for column in [
        "load_size",
        "repetition",
        "duration_ms",
        "input_records",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if (
            df[column].isna().any()
            or not np.isfinite(df[column]).all()
        ):
            raise ValueError(
                f"Missing or invalid numeric values in {column}."
            )

    # Integer-only fields.
    for column in [
        "load_size",
        "repetition",
        "input_records",
    ]:

        values = df[column].to_numpy()

        if (
            (values < 0).any()
            or not np.equal(
                values,
                np.floor(values)
            ).all()
        ):
            raise ValueError(
                f"{column} must contain non-negative integers."
            )

    if (df["load_size"] < 1).any():
        raise ValueError(
            "load_size must be positive."
        )

    if (df["repetition"] < 1).any():
        raise ValueError(
            "repetition must be positive."
        )

    if (
        df["input_records"] != df["load_size"]
    ).any():
        raise ValueError(
            "input_records must match load_size for every run."
        )

    if (df["duration_ms"] < 0).any():
        raise ValueError(
            "duration_ms cannot be negative."
        )

    # Validate Boolean success field.
    if (
        df["success"].isna().any()
        or not df["success"].map(
            lambda value: isinstance(
                value,
                (bool, np.bool_)
            )
        ).all()
    ):
        raise ValueError(
            "success must contain Boolean values."
        )

    df["success"] = df["success"].astype(bool)

    # Counters are mandatory for successful runs.
    # Failed runs may have unavailable counters.
    counter_columns = [
        "missing_predictions",
        "invalid_predictions",
    ]

    for column in counter_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        successful_missing = (
            df["success"] & df[column].isna()
        )

        if successful_missing.any():
            raise ValueError(
                f"{column} cannot be missing for successful runs."
            )

        known = df[column].dropna()

        if (
            not np.isfinite(known).all()
            or (known < 0).any()
        ):
            raise ValueError(
                f"{column} must be non-negative and finite when present."
            )

        if not np.equal(
            known.to_numpy(),
            np.floor(known.to_numpy())
        ).all():
            raise ValueError(
                f"{column} must contain integer counts."
            )

    known_counters = (
        df[counter_columns].notna().all(axis=1)
    )

    counter_total = (
        df[counter_columns]
        .fillna(0)
        .sum(axis=1)
    )

    if (
        known_counters
        & (counter_total > df["input_records"])
    ).any():
        raise ValueError(
            "Missing and invalid counts exceed input_records."
        )

    # Failed runs must have error descriptions.
    error_text = (
        df["error"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    if (
        (~df["success"])
        & error_text.eq("")
    ).any():
        raise ValueError(
            "Every failed run must include an error description."
        )

    if (
        df["success"]
        & error_text.ne("")
    ).any():
        raise ValueError(
            "Successful runs must not contain an error description."
        )

    duplicate_key = [
        "run_id",
        "method",
        "load_size",
        "phase",
        "repetition",
    ]

    if df.duplicated(duplicate_key).any():
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
    statistic="mean",
):
    """Calculate a percentile bootstrap confidence interval."""

    values = np.asarray(
        values,
        dtype=float
    )

    values = values[
        np.isfinite(values)
    ]

    if len(values) < 2:
        return np.nan, np.nan

    if iterations < 1:
        raise ValueError(
            "iterations must be positive."
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    rng = np.random.default_rng(seed)

    samples = rng.choice(
        values,
        size=(iterations, len(values)),
        replace=True,
    )

    if statistic == "mean":
        estimates = samples.mean(axis=1)

    elif statistic == "median":
        estimates = np.median(samples, axis=1)

    else:
        raise ValueError(
            "statistic must be 'mean' or 'median'."
        )

    alpha = 1 - confidence_level

    lower, upper = np.quantile(
        estimates,
        [
            alpha / 2,
            1 - alpha / 2,
        ],
    )

    return float(lower), float(upper)


# ==========================================================
# SUMMARIZE ONE METHOD / LOAD GROUP
# ==========================================================

def summarize_group(
    group,
    method,
    load_size,
    config,
    seed,
):
    """
    Successful runs contribute to latency statistics.

    All evaluation attempts contribute to the error-rate
    denominator.
    """

    total_attempts = len(group)

    successful = group[
        group["success"]
    ].copy()

    failed = group[
        ~group["success"]
    ].copy()

    successful_count = len(successful)
    failed_count = len(failed)

    durations = successful[
        "duration_ms"
    ].to_numpy(dtype=float)

    if successful_count:

        mean_ms = float(
            np.mean(durations)
        )

        std_ms = (
            float(np.std(durations, ddof=1))
            if successful_count > 1
            else np.nan
        )

        median_ms = float(
            np.median(durations)
        )

        p25, p75, p95, p99 = [
            float(value)
            for value in np.percentile(
                durations,
                [25, 75, 95, 99]
            )
        ]

        mean_ci_lower, mean_ci_upper = bootstrap_ci(
            durations,
            config["bootstrap_iterations"],
            config["confidence_level"],
            seed,
            "mean",
        )

        median_ci_lower, median_ci_upper = bootstrap_ci(
            durations,
            config["bootstrap_iterations"],
            config["confidence_level"],
            seed + 1,
            "median",
        )

        # Data quality counts are calculated only from
        # successful runs because failed runs may not
        # have returned the corresponding counters.
        successful_input_total = float(
            successful["input_records"].sum()
        )

        missing_total = float(
            successful["missing_predictions"].sum()
        )

        invalid_total = float(
            successful["invalid_predictions"].sum()
        )

        missing_input_rate = (
            missing_total / successful_input_total
            if successful_input_total
            else np.nan
        )

        invalid_input_rate = (
            invalid_total / successful_input_total
            if successful_input_total
            else np.nan
        )

    else:

        mean_ms = std_ms = median_ms = np.nan
        p25 = p75 = p95 = p99 = np.nan

        mean_ci_lower = mean_ci_upper = np.nan
        median_ci_lower = median_ci_upper = np.nan

        successful_input_total = 0.0
        missing_total = invalid_total = 0.0

        missing_input_rate = np.nan
        invalid_input_rate = np.nan

    return {
        "method": method,
        "load_size": int(load_size),

        "evaluation_attempts": total_attempts,
        "expected_evaluation_runs": (
            config["expected_evaluation_runs"]
        ),

        "successful_runs": successful_count,
        "failed_runs": failed_count,

        "run_count_complete": (
            total_attempts
            == config["expected_evaluation_runs"]
        ),

        "success_rate": (
            successful_count / total_attempts
            if total_attempts else np.nan
        ),

        "error_rate": (
            failed_count / total_attempts
            if total_attempts else np.nan
        ),

        "missing_input_rate": missing_input_rate,
        "invalid_input_rate": invalid_input_rate,

        "successful_input_records": int(
            successful_input_total
        ),

        "missing_predictions": int(missing_total),
        "invalid_predictions": int(invalid_total),

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
        "median_ci_upper_ms": median_ci_upper,

        "latency_sample_count": successful_count,
    }


# ==========================================================
# CALCULATE SUMMARY TABLE
# ==========================================================

def calculate_summary(data, config):
    """Exclude warm-up from latency calculations."""

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
        config["load_sizes"],
    ):

        group = evaluation[
            (evaluation["method"] == method)
            & (evaluation["load_size"] == load_size)
        ].copy()

        rows.append(
            summarize_group(
                group,
                method,
                load_size,
                config,
                config["random_seed"] + int(load_size),
            )
        )

    summary = pd.DataFrame(rows)

    warmup_counts = (
        warmup.groupby(
            ["method", "load_size"]
        )
        .size()
        .rename("warmup_runs_excluded")
        .reset_index()
    )

    summary = summary.merge(
        warmup_counts,
        on=["method", "load_size"],
        how="left",
    )

    summary["warmup_runs_excluded"] = (
        summary["warmup_runs_excluded"]
        .fillna(0)
        .astype(int)
    )

    return summary


# ==========================================================
# BASELINE / PROPOSED SPEEDUP
# ==========================================================

def calculate_speedup(data, config):
    """
    Calculate paired speedup:

    Baseline latency / Proposed latency.

    A value greater than 1 means Proposed is faster.
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

        paired = group.pivot(
            index="repetition",
            columns="method",
            values="duration_ms",
        )

        if {
            "baseline",
            "proposed",
        }.issubset(paired.columns):

            paired = paired.dropna(
                subset=["baseline", "proposed"]
            )

            ratios = (
                paired["baseline"]
                / paired["proposed"]
            ).to_numpy(dtype=float)

        else:
            ratios = np.array([], dtype=float)

        if len(ratios) >= 2:

            median_speedup = float(
                np.median(ratios)
            )

            lower, upper = bootstrap_ci(
                ratios,
                config["bootstrap_iterations"],
                config["confidence_level"],
                config["random_seed"] + int(load_size) + 100,
                "median",
            )

        elif len(ratios) == 1:

            median_speedup = float(ratios[0])
            lower = upper = np.nan

        else:

            median_speedup = np.nan
            lower = np.nan
            upper = np.nan

        results.append({
            "load_size": int(load_size),
            "paired_successful_runs": len(ratios),
            "median_speedup": median_speedup,
            "ci_lower": lower,
            "ci_upper": upper,
        })

    return pd.DataFrame(results)


# ==========================================================
# ERROR SUMMARY
# ==========================================================

def create_error_summary(data):
    """Summarize failed evaluation attempts separately."""

    failed = data[
        (data["phase"] == "benchmark")
        & (~data["success"])
    ].copy()

    columns = [
        "method",
        "load_size",
        "error",
        "failed_runs",
    ]

    if failed.empty:
        return pd.DataFrame(columns=columns)

    failed["error"] = (
        failed["error"]
        .fillna("Unspecified error")
        .astype(str)
        .str.strip()
        .replace("", "Unspecified error")
    )

    return (
        failed.groupby(
            ["method", "load_size", "error"]
        )
        .size()
        .reset_index(name="failed_runs")
        .sort_values(
            ["method", "load_size", "failed_runs"]
        )
        .reset_index(drop=True)
    )


# ==========================================================
# SAVE OUTPUT FILES
# ==========================================================

def save_outputs(
    summary,
    speedup,
    errors,
    config,
):
    """Save benchmark summaries."""

    output_files = [
        config["summary_file"],
        config["speedup_file"],
        config["error_file"],
    ]

    for output_file in output_files:
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    summary.to_csv(
        config["summary_file"],
        index=False,
        encoding="utf-8-sig",
    )

    speedup.to_csv(
        config["speedup_file"],
        index=False,
        encoding="utf-8-sig",
    )

    errors.to_csv(
        config["error_file"],
        index=False,
        encoding="utf-8-sig",
    )

    print("\nOUTPUT FILES")

    for output_file in output_files:
        print(output_file)


# ==========================================================
# MAIN
# ==========================================================

def main():

    config = load_config()

    print("=" * 65)
    print("BENCHMARK DATA PROCESSING")
    print("=" * 65)

    data = validate_data(
        load_jsonl(config["raw_file"])
    )

    print("Raw measurements:", len(data))

    print("\nPhase distribution:")
    print(
        data["phase"]
        .value_counts()
        .to_string()
    )

    warmup_count = int(
        (data["phase"] == "warmup").sum()
    )

    evaluation_count = int(
        (data["phase"] == "benchmark").sum()
    )

    print(
        "\nWarm-up records excluded from latency statistics:",
        warmup_count,
    )

    print(
        "Evaluation attempts retained for guardrail analysis:",
        evaluation_count,
    )

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
    print(summary.to_string(index=False))

    print("\nPAIRED SPEEDUP")
    print(
        "Baseline / Proposed; values above 1 mean Proposed is faster."
    )
    print(speedup.to_string(index=False))

    print("\nERROR SUMMARY")

    if errors.empty:
        print("No failed evaluation runs.")
    else:
        print(errors.to_string(index=False))

    save_outputs(
        summary,
        speedup,
        errors,
        config,
    )

    print("\nPROCESSING COMPLETED")


if __name__ == "__main__":
    main()
