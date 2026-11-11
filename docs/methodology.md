# Research Methodology

## 1. Project Information

**Research title:** Human Ability to Detect AI-Generated Phishing Emails: A Review of Existing Research

**Authors:** Zhadyra Kurmanova and Meirim Yersultan

**Institution:** Narxoz University

**Research approach:** Literature review and quantitative student survey.

## 2. Research Design

The project combines a review of existing academic research with a quantitative survey of university students.

The empirical component examines how participants classify AI-generated email examples as either phishing or legitimate.

The study includes two categories of email stimuli:

- AI-generated phishing emails.
- AI-generated legitimate-style emails.

All 12 email examples were generated using ChatGPT. The study does not include a human-written comparison group.

The survey also collects demographic information, self-reported cybersecurity knowledge, previous phishing experience, the first indicator checked by participants, and self-reported confidence.

The study focuses on human email classification. It does not evaluate an automated phishing-detection model.

## 3. Research Questions

The research is guided by four questions:

- **RQ1:** How accurately can university students identify AI-generated phishing emails?
- **RQ2:** How does detection recall vary across the six AI-generated phishing examples?
- **RQ3:** How are self-reported cybersecurity knowledge and previous phishing experience related to phishing detection performance?
- **RQ4:** Which indicators do participants primarily rely on when identifying phishing emails?

Detailed questions and hypotheses are documented in `research_questions.md`.

## 4. Participants and Sampling

The study included 27 participants who completed the Google Forms questionnaire.

Each participant classified 12 email examples, resulting in 324 recorded email classifications.

The final participant count was confirmed using the Google Forms response summary.

The survey includes the following demographic and background variables:

- Age group.
- Self-reported cybersecurity knowledge.
- Previous phishing experience.

The recruitment procedure and sampling method must be described using the actual study records. No recruitment method is assumed in this document.

## 5. Survey Instrument

The questionnaire contains the following questions:

| Question | Variable | Description |
|---|---|---|
| Q1 | Age group | Participant age category |
| Q2 | Cybersecurity knowledge | Self-reported knowledge level |
| Q3 | Phishing experience | Previous experience with phishing |
| Q4–Q15 | Email classification | Classification of 12 email examples |
| Q16 | First detection indicator | First characteristic checked by the participant |
| Additional question | Confidence | Self-reported confidence in answers |

For each email, participants selected one of two options:

- Phishing email.
- Legitimate email.

The questionnaire also included a confidence question. However, the supplied response table contains only one completed confidence value. Therefore, confidence is not used for group-level statistical conclusions.

## 6. Email Stimuli and Ground Truth

The survey contains 12 email examples. All were generated using ChatGPT.

| Email ID | Correct class | Authorship |
|---|---|---|
| email_01 | Phishing | AI-generated |
| email_02 | Legitimate-style | AI-generated |
| email_03 | Phishing | AI-generated |
| email_04 | Legitimate-style | AI-generated |
| email_05 | Phishing | AI-generated |
| email_06 | Legitimate-style | AI-generated |
| email_07 | Phishing | AI-generated |
| email_08 | Legitimate-style | AI-generated |
| email_09 | Phishing | AI-generated |
| email_10 | Legitimate-style | AI-generated |
| email_11 | Phishing | AI-generated |
| email_12 | Legitimate-style | AI-generated |

The stimulus set contains:

- Six AI-generated phishing examples: 01, 03, 05, 07, 09, and 11.
- Six AI-generated legitimate-style examples: 02, 04, 06, 08, 10, and 12.

The legitimate-style examples are simulated emails rather than independently collected real correspondence.

The ground-truth labels and authorship categories are documented in `data/metadata/email_answer_key.csv`. In the answer key, legitimate-style messages use the classification label `legitimate`.

The stimulus descriptions are maintained in `docs/email_stimuli.md`.

## 7. Data Collection Procedure

The questionnaire was distributed using Google Forms.

The supplied response table contains records dated November 5, 2026.

Participants provided demographic information and classified the 12 email examples.

The original Google Forms export is maintained separately from the public repository.

The exact recruitment, consent, questionnaire presentation order, and randomization procedures must be documented only when confirmed by the researchers' records.

## 8. Data Storage and Privacy

The original participant-level survey export is stored locally.

The public repository does not contain:

- Original participant email addresses.
- Raw identifiable survey exports.
- Consent records.
- Other direct personal identifiers.

Participant records are assigned pseudonymous identifiers during local processing.

Only reviewed aggregate outputs are considered for publication.

The repository uses `.gitignore` rules to prevent accidental tracking of raw survey data.

## 9. Data Processing

Python and Pandas are used for data inspection, processing, and analysis.

The processing workflow consists of the following stages:

1. Load the original Google Forms CSV export.
2. Validate the number of columns and participant records.
3. Identify the 12 repeated email-question columns by their verified positions.
4. Normalize Russian response options into standard labels.
5. Reshape the survey from wide format to long format.
6. Assign pseudonymous participant identifiers.
7. Join the verified email answer key.
8. Add the email authorship category (`ai_generated` for all stimuli).
9. Calculate whether each participant classification matches the correct email label.
10. Report missing and unrecognized responses.
11. Generate aggregate statistical tables.
12. Produce scientific visualizations.

The original CSV is not modified during processing.

The Google Forms points column is not used as a measure of detection accuracy.

## 10. Evaluation Metrics

The positive classification is defined as `phishing`.

The negative classification is defined as `legitimate`.

The following metrics are calculated:

### 10.1. Accuracy

The proportion of all valid classifications that match the verified email labels.

### 10.2. Precision

The proportion of predicted phishing classifications that are actually phishing.

### 10.3. Recall

The proportion of actual phishing emails correctly identified as phishing.

### 10.4. Specificity

The proportion of legitimate-style emails correctly identified as legitimate.

### 10.5. False Positive Rate

The proportion of legitimate-style emails incorrectly classified as phishing.

### 10.6. F1-score

The harmonic mean of precision and recall.

### 10.7. Per-Email Phishing Recall

Detection recall is calculated separately for each of the six AI-generated phishing examples:

- email_01
- email_03
- email_05
- email_07
- email_09
- email_11

All metrics are calculated from participant predictions and verified ground-truth labels.

Results are reported with the corresponding number of valid classifications and denominators.

## 11. Statistical Analysis

Each participant evaluates multiple email examples.

Therefore, individual classifications from the same participant are treated as repeated observations rather than independent participants.

The statistical analysis includes:

1. Calculating overall accuracy, precision, recall, specificity, false positive rate, and F1-score.
2. Calculating detection recall separately for each of the six AI-generated phishing emails.
3. Estimating 95% confidence intervals using participant-level bootstrap resampling.
4. Comparing observed per-email detection rates descriptively.
5. Interpreting differences cautiously because the participant and stimulus samples are limited.

Bootstrap confidence intervals use 5,000 participant-level resamples with replacement and a fixed random seed of 42.

For overall metrics, all twelve responses from a sampled participant are retained together.

For individual phishing emails, each participant contributes one classification.

The study does not perform an AI-versus-human authorship comparison because all email stimuli were AI-generated.

The small number of email stimuli limits the generalizability of observed differences in detection recall.

## 12. Missing Data

Missing classifications are not automatically treated as correct or incorrect.

The number of missing responses is reported separately.

All 27 participants provided classifications for all 12 email examples, resulting in 324 non-missing email classifications.

Confidence responses are incomplete in the supplied response table. Therefore, confidence is excluded from inferential group comparisons.

Response time was not collected as part of the survey and is not included in survey performance metrics.

## 13. Ethical Considerations

The questionnaire includes an age category for participants under 18.

The researchers must verify the university's requirements for participation by minors, including any required assent and parent or guardian permission.

The study must not claim ethics approval or consent procedures unless they are supported by the relevant institutional records.

Participant data must be handled confidentially and in accordance with the university's research requirements.

## 14. Limitations

The study has several limitations:

1. The participant sample is limited to 27 people and should not be treated as representative of all users.
2. Only six AI-generated phishing examples and six AI-generated legitimate-style examples were included.
3. No independently human-written comparison group was included.
4. The legitimate-style emails were simulated rather than collected from real-world correspondence.
5. Cybersecurity knowledge is self-reported rather than objectively tested.
6. Confidence responses are incomplete.
7. Response time was not collected.
8. The survey's recruitment and presentation procedures require documentation from the original study records.
9. The 324 classifications represent repeated responses from 27 participants rather than 324 independent participants.
10. The limited stimulus set restricts conclusions about phishing detection beyond the selected examples.

These limitations are considered when interpreting the findings.

## 15. Separate Technical Benchmark

The repository includes a separate technical benchmark of the Python data-processing pipeline.

This benchmark measures software execution performance, including processing latency, percentiles, confidence intervals, and error rates.

The benchmark compares a Python loop-based baseline implementation with a Pandas vectorized implementation using synthetic workloads.

Technical benchmark measurements are not survey results and are not combined with human phishing-detection metrics.

## 16. Reproducibility

The repository contains the processing scripts, analysis notebook, answer-key metadata, documentation, and approved aggregate outputs.

The original participant-level export remains private.

The analysis can be reproduced by placing the authorized survey export at `data/raw/responses.csv` and executing the documented processing workflow.

The repository includes aggregate survey results and figures in `data/processed/` and `reports/figures/`.

## 17. Authors

Zhadyra Kurmanova  
Meirim Yersultan
