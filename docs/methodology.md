
# Research Methodology

## 1. Project Information

**Research title:** Human Ability to Detect AI-Generated Phishing Emails: A Review of Existing Research

**Authors:** Zhadyra Kurmanova and Meirim Yersultan

**Institution:** Narxoz University

**Research approach:** Literature review and quantitative student survey.

## 2. Research Design

The project combines a review of existing academic research with a quantitative survey of university students.

The empirical component examines how participants classify email examples as either phishing or legitimate.

The study includes three categories of email stimuli:

- AI-generated phishing emails.
- Human-written phishing emails.
- Legitimate emails.

The survey also collects demographic information, self-reported cybersecurity knowledge, previous phishing experience, the first indicator checked by participants, and self-reported confidence.

The study focuses on human email classification. It does not evaluate an automated phishing-detection model.

## 3. Research Questions

The research is guided by four questions:

- RQ1: How accurately can university students identify AI-generated phishing emails?
- RQ2: Is there a difference in participants' ability to detect AI-generated and human-written phishing emails?
- RQ3: How are self-reported cybersecurity knowledge and previous phishing experience related to phishing detection performance?
- RQ4: Which indicators do participants primarily rely on when identifying phishing emails?

Detailed questions and hypotheses are documented in `research_questions.md`.

## 4. Participants and Sampling

The latest response table supplied for analysis contains 30 participant records.

Each participant was asked to classify 12 email examples.

The final participant count and the completeness of all responses must be confirmed against the original Google Forms export before publication.

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
| Q4-Q15 | Email classification | Classification of 12 email examples |
| Q16 | First detection indicator | First characteristic checked by the participant |
| Additional question | Confidence | Self-reported confidence in answers |

For each email, participants selected one of two options:

- Phishing email.
- Legitimate email.

The questionnaire also included a confidence question. However, the latest supplied response table contains only one completed confidence value. Therefore, confidence is not used for group-level statistical conclusions.

## 6. Email Stimuli and Ground Truth

The survey contains 12 email examples.

| Email ID | Correct class | Authorship |
|---|---|---|
| email_01 | Phishing | AI-generated |
| email_02 | Legitimate | Unknown |
| email_03 | Phishing | Human-written |
| email_04 | Legitimate | Unknown |
| email_05 | Phishing | AI-generated |
| email_06 | Legitimate | Unknown |
| email_07 | Phishing | Human-written |
| email_08 | Legitimate | Unknown |
| email_09 | Phishing | AI-generated |
| email_10 | Legitimate | Unknown |
| email_11 | Phishing | Human-written |
| email_12 | Legitimate | Unknown |

The phishing examples are divided into two authorship groups:

- Three AI-generated phishing examples.
- Three human-written phishing examples.

The authorship of the legitimate examples has not been established and is therefore recorded as unknown.

The ground-truth labels and authorship categories are maintained separately in `data/metadata/email_answer_key.csv`.

The labels must be checked against the original questionnaire and stimulus records before final publication.

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
8. Add the email authorship category.
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

The proportion of legitimate emails correctly identified as legitimate.

### 10.5. False Positive Rate

The proportion of legitimate emails incorrectly classified as phishing.

### 10.6. F1-score

The harmonic mean of precision and recall.

### 10.7. Source-specific Recall

Detection recall is calculated separately for:

- AI-generated phishing.
- Human-written phishing.

All metrics are calculated from participant predictions and verified ground-truth labels.

Results are reported with the corresponding number of valid classifications and denominators.

## 11. Statistical Analysis

Each participant evaluates multiple email examples.

Therefore, individual classifications from the same participant are treated as repeated observations rather than independent participants.

For the comparison between AI-generated and human-written phishing:

1. Calculate one detection-recall value per participant for each authorship group.
2. Compare the two participant-level results using a paired approach.
3. Report group estimates and uncertainty intervals.
4. Interpret statistical significance and effect size cautiously.

Bootstrap confidence intervals use participant-level resampling.

A fixed random seed is used to improve reproducibility.

The small number of email stimuli in each phishing group limits the generalizability of the comparison.

## 12. Missing Data

Missing classifications are not automatically treated as correct or incorrect.

The number of missing responses is reported separately.

Confidence responses are incomplete in the latest supplied response table. Therefore, confidence is excluded from inferential group comparisons.

Response time was not collected as part of the survey and is not included in survey performance metrics.

## 13. Ethical Considerations

The questionnaire includes an age category for participants under 18.

The researchers must verify the university's requirements for participation by minors, including any required assent and parent or guardian permission.

The study must not claim ethics approval or consent procedures unless they are supported by the relevant institutional records.

Participant data must be handled confidentially and in accordance with the university's research requirements.

## 14. Limitations

The study has several limitations:

1. The participant sample is limited and should not be treated as representative of all users.
2. Only three AI-generated phishing examples are included.
3. Only three human-written phishing examples are included.
4. The findings concern the selected email examples and cannot establish universal differences between AI-generated and human-written phishing.
5. The authorship of the legitimate email examples is unknown.
6. Cybersecurity knowledge is self-reported rather than objectively tested.
7. Confidence responses are incomplete.
8. Response time was not collected.
9. The survey's recruitment and presentation procedures require documentation from the original study records.

These limitations are considered when interpreting the findings.

## 15. Separate Technical Benchmark

The repository may include a separate technical benchmark of the Python data-processing pipeline.

This benchmark measures software execution performance, such as processing latency, percentiles, confidence intervals, and error rates.

Technical benchmark measurements are not survey results and are not combined with human phishing-detection metrics.

## 16. Reproducibility

The repository contains the processing scripts, analysis notebook, answer-key metadata, documentation, and approved aggregate outputs.

The original participant-level export remains private.

The analysis can be reproduced by placing the authorized survey export in the local `data/raw/` directory and executing the documented processing workflow.

## 17. Authors

Zhadyra Kurmanova  
Meirim Yersultan
