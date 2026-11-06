# Human Ability to Detect AI-Generated Phishing Emails: A Review of Existing Research

## 1. Project Overview

This research examines human ability to identify phishing emails in the context of generative artificial intelligence.

The project combines a review of existing cybersecurity research with a quantitative student survey and a separate technical performance benchmark of the Python data-processing pipeline.

The empirical survey focuses on how students classify AI-generated phishing emails, human-written phishing emails, and legitimate email examples.

The technical benchmark evaluates the execution performance of two data-processing implementations under different synthetic workloads.

**Authors:** Zhadyra Kurmanova and Meirim Yersultan  
**Institution:** Narxoz University  
**Research Area:** Cybersecurity

## 2. Research Objectives

1. Review existing research on human phishing detection.
2. Examine how accurately students identify AI-generated phishing emails.
3. Compare participant responses to selected AI-generated and human-written phishing examples.
4. Explore the relationship between self-reported cybersecurity knowledge and phishing detection performance.
5. Identify the indicators participants primarily use when evaluating suspicious emails.
6. Evaluate the performance of the research data-processing pipeline.

## 3. Research Questions

- **RQ1:** How accurately can university students identify AI-generated phishing emails?
- **RQ2:** Is there a difference in participants' ability to detect AI-generated and human-written phishing emails?
- **RQ3:** How are self-reported cybersecurity knowledge and previous phishing experience related to phishing detection performance?
- **RQ4:** Which indicators do participants primarily rely on when identifying phishing emails?

See [Research Questions](docs/research_questions.md).

## 4. Survey Design

The questionnaire contains 12 email examples:

| Email category | Number of examples |
|---|---:|
| AI-generated phishing | 3 |
| Human-written phishing | 3 |
| Legitimate emails | 6 |
| **Total** | **12** |

The survey collects age group, self-reported cybersecurity knowledge, previous phishing experience, email classifications, first detection indicator, and confidence.

The authorship of legitimate email examples is recorded as unknown.

The original participant-level survey export is kept private. Only approved aggregate research results may be published.

See:
- [Research Methodology](docs/methodology.md)
- [Email Stimuli](docs/email_stimuli.md)
- [Data Dictionary](docs/data_dictionary.md)

## 5. Technical Performance Benchmark

A separate benchmark evaluates two implementations of the same data-processing task:

- **Baseline:** Python loop-based implementation.
- **Proposed:** Pandas vectorized implementation.

Both implementations process the same synthetic classification workload and must produce identical analytical results.

### 5.1. Experimental Configuration

| Parameter | Value |
|---|---:|
| Methods | 2 |
| Input sizes | 100, 1,000, 5,000, 10,000 records |
| Warm-up runs per method and load | 5 |
| Evaluation runs per method and load | 30 |
| Total warm-up runs | 40 |
| Total evaluation runs | 240 |
| Total measurements | 280 |
| Bootstrap iterations | 5,000 |
| Confidence level | 95% |
| Random seed | 42 |

### 5.2. Results & Discussion

The benchmark compares processing latency under four input sizes.

Mean and standard deviation are reported alongside median and interquartile range.

All latency measurements are expressed in milliseconds.

| Method | Load (records) | Mean ± SD (ms) | Median (p25–p75) (ms) |
|---|---:|---:|---:|
| Baseline | 100 | 0.760 ± 0.202 | 0.670 (0.593–0.998) |
| Proposed | 100 | 5.785 ± 2.743 | 4.558 (4.441–7.011) |
| Baseline | 1,000 | 4.265 ± 1.010 | 4.360 (4.210–4.600) |
| Proposed | 1,000 | 10.878 ± 1.982 | 11.237 (10.840–11.549) |
| Baseline | 5,000 | 29.410 ± 11.237 | 25.346 (19.735–35.234) |
| Proposed | 5,000 | 36.888 ± 11.437 | 34.835 (26.083–44.826) |
| Baseline | 10,000 | 28.002 ± 11.853 | 20.899 (20.360–36.473) |
| Proposed | 10,000 | 32.777 ± 16.544 | 25.167 (22.518–39.635) |

#### 5.3. Percentile Analysis

| Load | Method | p95 (ms) | p99 (ms) |
|---:|---|---:|---:|
| 100 | Baseline | 1.094 | 1.125 |
| 100 | Proposed | 8.002 | 15.434 |
| 1,000 | Baseline | 5.666 | 6.295 |
| 1,000 | Proposed | 13.556 | 13.619 |
| 5,000 | Baseline | 50.892 | 58.696 |
| 5,000 | Proposed | 54.684 | 60.453 |
| 10,000 | Baseline | 50.440 | 63.470 |
| 10,000 | Proposed | 62.046 | 88.813 |

#### 5.4. Confidence Intervals

A 95% percentile-bootstrap confidence interval was calculated for the median of successful evaluation runs.

| Load | Method | Median 95% CI (ms) |
|---:|---|---:|
| 100 | Baseline | 0.636–0.735 |
| 100 | Proposed | 4.471–5.209 |
| 1,000 | Baseline | 4.275–4.529 |
| 1,000 | Proposed | 10.883–11.480 |
| 5,000 | Baseline | 21.226–32.865 |
| 5,000 | Proposed | 28.548–42.132 |
| 10,000 | Baseline | 20.505–30.778 |
| 10,000 | Proposed | 22.864–34.803 |

#### 5.5. Error Rate and Data Quality

All 240 evaluation executions completed successfully.

| Metric | Result |
|---|---:|
| Successful evaluation runs | 240 |
| Failed evaluation runs | 0 |
| Execution error rate | 0% |

Synthetic missing and invalid prediction records were deliberately included as input edge cases. Their proportions were tracked separately from execution failures.

#### 5.6. Discussion

The experimental results show that the baseline implementation achieved lower median processing latency than the proposed Pandas implementation across all four tested input sizes.

The proposed implementation was approximately 6.80 times slower at 100 records, 2.58 times slower at 1,000 records, 1.37 times slower at 5,000 records, and 1.20 times slower at 10,000 records, based on the ratio of observed medians.

This result suggests that vectorized processing does not automatically improve performance for every workload. Additional implementation overhead may outweigh the benefits of vectorization for the tested task.

The performance difference becomes smaller at larger input sizes. However, this experiment does not demonstrate a performance improvement of the proposed implementation.

Further investigation is needed to identify the sources of overhead and evaluate alternative optimizations.

The benchmark uses synthetic data for a local processing task. Its results must not be interpreted as measurements of phishing detection effectiveness or student behavior.

## 6. Scientific Visualizations

### Figure 1. Processing Latency vs Input Load

The figure compares median processing latency for the baseline and proposed implementations. Shaded regions represent 95% bootstrap confidence intervals.

![Processing Latency vs Input Load](reports/figures/fig1_latency_vs_load.png)

[Download vector PDF](reports/figures/fig1_latency_vs_load.pdf)

### Figure 2. Processing Time Distribution

The boxplot compares execution-time distributions for both implementations at different input sizes. Boxes represent the interquartile range, center lines show medians, and diamond markers represent means with 95% bootstrap confidence intervals.

![Processing Time Distribution](reports/figures/fig2_distribution_boxplot.png)

[Download vector PDF](reports/figures/fig2_distribution_boxplot.pdf)

## 7. Domain Model and Security Analysis

The project includes a STRIDE threat model covering:

- Spoofing
- Tampering
- Repudiation
- Information Disclosure
- Denial of Service
- Elevation of Privilege

The threat model identifies risks to survey collection, raw research data, processing components, and the public repository.

See [Domain Model and STRIDE Threat Analysis](docs/domain_model.md).

## 8. Repository Structure

```text
ai-phishing-literature-review/
│
├── config/
│   └── benchmark_config.yaml
│
├── data/
│   ├── raw/
│   │   ├── responses.csv        # Private; not committed
│   │   └── test_run.jsonl
│   ├── metadata/
│   │   └── email_answer_key.csv
│   └── processed/
│       ├── metrics_summary.csv
│       ├── speedup_summary.csv
│       └── benchmark_error_summary.csv
│
├── docs/
│   ├── domain_model.md
│   ├── methodology.md
│   ├── research_questions.md
│   ├── email_stimuli.md
│   └── data_dictionary.md
│
├── notebooks/
│   └── 01_data_analysis.ipynb
│
├── reports/
│   └── figures/
│       ├── fig1_latency_vs_load.png
│       ├── fig1_latency_vs_load.pdf
│       ├── fig2_distribution_boxplot.png
│       └── fig2_distribution_boxplot.pdf
│
├── src/
│   ├── benchmark.py
│   ├── process_data.py
│   ├── visualize.py
│   ├── process_survey.py
│   ├── calculate_metrics.py
│   ├── inspect_survey.py
│   └── visualize_survey.py
│
├── tests/
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## 9. Reproducibility

### Requirements

- Python 3.11
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SciPy
- PyYAML
- JupyterLab

### Installation

```bash
git clone https://github.com/zhadritto/ai-phishing-literature-review.git

cd ai-phishing-literature-review

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Run the technical benchmark

```bash
python src/benchmark.py
python src/process_data.py
python src/visualize.py
```

### Run the student survey analysis

The original Google Forms export must be available locally at:

```text
data/raw/responses.csv
```

Then run:

```bash
python src/inspect_survey.py
python src/process_survey.py
python src/calculate_metrics.py
python src/visualize_survey.py
```

The raw survey export and participant-level processed data must not be committed to the public repository.

## 10. Research Limitations

The project has several limitations:

1. The survey contains a limited number of participants.
2. Only three AI-generated and three human-written phishing examples are included.
3. The authorship of legitimate email examples is unknown.
4. Cybersecurity knowledge is self-reported.
5. Confidence responses are incomplete.
6. Response time was not measured in the survey.
7. The performance benchmark uses synthetic workloads and evaluates a local data-processing task.
8. The benchmark does not demonstrate that the proposed implementation is faster than the baseline.

These limitations should be considered when interpreting the findings.

## 11. Authors

**Zhadyra Kurmanova**  
**Meirim Yersultan**

Narxoz University

## 12. Repository

[GitHub Repository](https://github.com/zhadritto/ai-phishing-literature-review)
