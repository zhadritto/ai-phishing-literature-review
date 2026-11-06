
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

from matplotlib.lines import Line2D
from matplotlib.patches import Patch


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "config" / "benchmark_config.yaml"

RANDOM_SEED = 42
BOOTSTRAP_ITERATIONS = 5000
CONFIDENCE_LEVEL = 0.95

sns.set_theme(
    style="whitegrid",
    palette="colorblind",
    font_scale=1.1
)

COLORS = sns.color_palette("colorblind", 2)

METHOD_STYLES = {
    "baseline": {
        "color": COLORS[0],
        "linestyle": "--",
        "marker": "o",
        "label": "Baseline"
    },
    "proposed": {
        "color": COLORS[1],
        "linestyle": "-",
        "marker": "s",
        "label": "Proposed"
    }
}


# ==========================================================
# LOAD CONFIGURATION
# ==========================================================

def load_config():

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    output = config.get("output", {})

    return {
        "summary_file": (
            ROOT / output["processed_metrics"]
        ),
        "raw_file": (
            ROOT / output["raw_logs"]
        ),
        "figures_dir": (
            ROOT / output["figures_directory"]
        )
    }


# ==========================================================
# LOAD PROCESSED METRICS
# ==========================================================

def load_metrics(config):

    file = config["summary_file"]

    if not file.exists():
        raise FileNotFoundError(
            f"Metrics summary not found: {file}"
        )

    df = pd.read_csv(file)

    required = {
        "method",
        "load_size",
        "median_ms",
        "median_ci_lower_ms",
        "median_ci_upper_ms"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing metric columns: {sorted(missing)}"
        )

    df["method"] = (
        df["method"].astype(str).str.lower()
    )

    df["load_size"] = pd.to_numeric(
        df["load_size"],
        errors="raise"
    )

    return df.sort_values(
        ["load_size", "method"]
    )


# ==========================================================
# LOAD RAW JSONL
# ==========================================================

def load_raw_logs(config):

    file = config["raw_file"]

    if not file.exists():
        raise FileNotFoundError(
            f"Raw benchmark logs not found: {file}"
        )

    records = []

    with file.open(encoding="utf-8") as source:

        for line_number, line in enumerate(source, start=1):

            if not line.strip():
                continue

            try:
                records.append(json.loads(line))

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON at line {line_number}"
                ) from error

    df = pd.DataFrame(records)

    required = {
        "method",
        "load_size",
        "phase",
        "duration_ms",
        "success"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing raw log columns: {sorted(missing)}"
        )

    # Only successful evaluation measurements
    # are included in latency distribution plots.
    df = df[
        (df["phase"] == "benchmark")
        & (df["success"] == True)
    ].copy()

    df["duration_ms"] = pd.to_numeric(
        df["duration_ms"],
        errors="raise"
    )

    return df


# ==========================================================
# BOOTSTRAP CONFIDENCE INTERVAL
# ==========================================================

def bootstrap_mean_ci(
    values,
    iterations=BOOTSTRAP_ITERATIONS,
    seed=RANDOM_SEED
):

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

    means = samples.mean(axis=1)

    lower, upper = np.percentile(
        means,
        [
            (1 - CONFIDENCE_LEVEL) * 50,
            100 - (1 - CONFIDENCE_LEVEL) * 50
        ]
    )

    return float(lower), float(upper)


# ==========================================================
# SAVE FIGURES
# ==========================================================

def save_figure(fig, name, output_dir):

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        output_dir / f"{name}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)


# ==========================================================
# FIGURE 1: LATENCY VS LOAD
# ==========================================================

def plot_latency_vs_load(metrics, output_dir):

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    all_values = []

    for method, style in METHOD_STYLES.items():

        group = metrics[
            metrics["method"] == method
        ].sort_values("load_size")

        if group.empty:
            continue

        x = group["load_size"].to_numpy()
        y = group["median_ms"].to_numpy()

        lower = group["median_ci_lower_ms"].to_numpy()
        upper = group["median_ci_upper_ms"].to_numpy()

        if not np.isfinite(y).all():
            raise ValueError(
                f"Missing median values for {method}."
            )

        ax.plot(
            x,
            y,
            color=style["color"],
            linestyle=style["linestyle"],
            marker=style["marker"],
            markersize=7,
            linewidth=2,
            label=style["label"]
        )

        valid_ci = (
            np.isfinite(lower)
            & np.isfinite(upper)
        )

        if valid_ci.any():

            ax.fill_between(
                x[valid_ci],
                lower[valid_ci],
                upper[valid_ci],
                color=style["color"],
                alpha=0.16
            )

        all_values.extend(y.tolist())

    if not all_values:
        raise ValueError(
            "No successful latency measurements available."
        )

    # Use a log scale only when data span
    # approximately two or more orders of magnitude.
    positive_values = [
        value for value in all_values if value > 0
    ]

    if positive_values:

        scale_ratio = (
            max(positive_values)
            / min(positive_values)
        )

        if scale_ratio >= 100:
            ax.set_yscale("log")

    ax.set_xlabel(
        "Input Load (records)",
        fontsize=12
    )

    ax.set_ylabel(
        "Median Processing Latency (ms)",
        fontsize=12
    )

    ax.set_title(
        "Processing Latency vs Input Load",
        fontsize=14,
        weight="bold"
    )

    ax.legend(
        title="Implementation",
        frameon=True
    )

    ax.grid(
        True,
        linestyle=":",
        alpha=0.6
    )

    fig.tight_layout()

    save_figure(
        fig,
        "fig1_latency_vs_load",
        output_dir
    )


# ==========================================================
# FIGURE 2: DISTRIBUTION BOXPLOT
# ==========================================================

def plot_distribution_boxplot(raw_data, output_dir):

    methods = [
        "baseline",
        "proposed"
    ]

    load_sizes = sorted(
        raw_data["load_size"].unique()
    )

    if not load_sizes:
        raise ValueError(
            "No successful evaluation records available."
        )

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )

    group_positions = np.arange(
        len(load_sizes)
    )

    offset = 0.20
    width = 0.32

    legend_handles = [
        Patch(
            facecolor=COLORS[0],
            label="Baseline"
        ),
        Patch(
            facecolor=COLORS[1],
            label="Proposed"
        ),
        Line2D(
            [0],
            [0],
            color="black",
            marker="D",
            linestyle="none",
            label="Mean with 95% CI"
        )
    ]

    for method_index, method in enumerate(methods):

        style = METHOD_STYLES[method]

        positions = (
            group_positions
            + (
                -offset
                if method_index == 0
                else offset
            )
        )

        for position, load_size in zip(
            positions,
            load_sizes
        ):

            group = raw_data[
                (raw_data["method"] == method)
                & (raw_data["load_size"] == load_size)
            ]

            values = group[
                "duration_ms"
            ].dropna().to_numpy(dtype=float)

            if len(values) < 2:
                continue

            # Distribution and interquartile range
            ax.boxplot(
                [values],
                positions=[position],
                widths=width,
                patch_artist=True,
                showfliers=True,
                boxprops={
                    "facecolor": style["color"],
                    "alpha": 0.55
                },
                medianprops={
                    "color": "black",
                    "linewidth": 2
                },
                whiskerprops={
                    "color": "black"
                },
                capprops={
                    "color": "black"
                },
                flierprops={
                    "marker": "o",
                    "markersize": 4,
                    "alpha": 0.5
                }
            )

            # Bootstrap CI around the mean
            lower, upper = bootstrap_mean_ci(
                values,
                seed=RANDOM_SEED + int(load_size) + method_index
            )

            mean_value = float(
                np.mean(values)
            )

            if np.isfinite(lower) and np.isfinite(upper):

                ax.errorbar(
                    position,
                    mean_value,
                    yerr=[
                        [max(0, mean_value - lower)],
                        [max(0, upper - mean_value)]
                    ],
                    fmt="D",
                    color="black",
                    markersize=5,
                    capsize=4,
                    zorder=5
                )

    ax.set_xticks(group_positions)

    ax.set_xticklabels(
        [f"{size:,}" for size in load_sizes]
    )

    ax.set_xlabel(
        "Input Load (records)",
        fontsize=12
    )

    ax.set_ylabel(
        "Processing Time (ms)",
        fontsize=12
    )

    ax.set_title(
        "Processing Time Distribution by Method",
        fontsize=14,
        weight="bold"
    )

    ax.legend(
        handles=legend_handles,
        title="Legend"
    )

    ax.grid(
        axis="y",
        linestyle=":",
        alpha=0.6
    )

    fig.tight_layout()

    save_figure(
        fig,
        "fig2_distribution_boxplot",
        output_dir
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("SCIENTIFIC VISUALIZATION")
    print("=" * 60)

    config = load_config()

    metrics = load_metrics(config)

    raw_data = load_raw_logs(config)

    # Keep only methods and loads in summary.
    metrics = metrics[
        metrics["method"].isin(
            METHOD_STYLES.keys()
        )
    ].copy()

    print("\nGenerating Figure 1...")

    plot_latency_vs_load(
        metrics,
        config["figures_dir"]
    )

    print("Figure 1 exported.")

    print("\nGenerating Figure 2...")

    plot_distribution_boxplot(
        raw_data,
        config["figures_dir"]
    )

    print("Figure 2 exported.")

    print("\nAll figures successfully generated.")

    print("Output directory:")
    print(config["figures_dir"])


if __name__ == "__main__":
    main()
