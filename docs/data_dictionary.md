
# Data Dictionary

## 1. Overview

This document describes the variables used in the research survey and the technical benchmark.

## 2. Survey Variables

| Variable | Type | Description |
|---|---|---|
| participant_id | String | Pseudonymous participant identifier |
| age_group | Categorical | Participant age category |
| cyber_knowledge | Categorical | Self-reported cybersecurity knowledge |
| phishing_experience | Categorical | Previous phishing experience |
| email_id | String | Unique email example identifier |
| predicted_label | Categorical | Participant classification |
| true_label | Categorical | Verified email classification |
| email_source | Categorical | Email authorship category |
| is_correct | Boolean | Whether the classification is correct |
| first_indicator | Categorical | First indicator checked |
| confidence | Numeric | Self-reported confidence, when provided |


## 3. Email Categories

| Category | Email IDs | Count |
|---|---|---:|
| AI-generated phishing | email_01, email_03, email_05, email_07, email_09, email_11 | 6 |
| AI-generated legitimate examples | email_02, email_04, email_06, email_08, email_10, email_12 | 6 |
| **Total** | **email_01–email_12** | **12** |

All 12 email examples were drafted using ChatGPT. The study does not include a verified human-written email group.

The `true_label` variable identifies whether an email is phishing or legitimate. The `email_source` variable identifies its authorship. These variables are treated separately.


## 4. Benchmark Variables

| Variable | Type | Description |
|---|---|---|
| run_id | String | Unique benchmark execution identifier |
| method | Categorical | Baseline or proposed implementation |
| load_size | Integer | Number of synthetic records |
| phase | Categorical | Warm-up or benchmark |
| repetition | Integer | Run number |
| duration_ms | Float | Execution duration in milliseconds |
| success | Boolean | Execution success status |
| error | String | Error details when execution fails |
| input_records | Integer | Number of input records |
| missing_predictions | Integer | Missing synthetic predictions |
| invalid_predictions | Integer | Invalid synthetic predictions |

## 5. Statistical Metrics

| Metric | Description |
|---|---|
| Mean | Arithmetic mean of execution times |
| SD | Standard deviation |
| Median | 50th percentile |
| p25 | 25th percentile |
| p75 | 75th percentile |
| p95 | 95th percentile |
| p99 | 99th percentile |
| 95% CI | Bootstrap confidence interval |
| Error Rate | Failed executions divided by total evaluation attempts |

## 6. Data Privacy

Original participant-level survey responses are maintained in restricted local storage.

The public repository contains only approved aggregate outputs and technical benchmark artifacts.
