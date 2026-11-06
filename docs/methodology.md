# Research Methodology

## 1. Project information

**Project:** Student Responses to Phishing and Legitimate Email Examples in the Context of AI-Generated Phishing  
**Authors:** Zhadyra Kurmanova and Meirim Yersultan  
**Repository:** https://github.com/zhadritto/ai-phishing-literature-review  
**Study component:** Descriptive analysis of a student email-classification survey.

This document describes the survey analysis reported in `paper_draft.md`. The repository also contains a separate synthetic benchmark used to demonstrate a Python measurement pipeline. Synthetic benchmark outputs are not survey findings and must not be combined with the survey results.

## 2. Research question and scope

**RQ1:** What response patterns are observed when participants classify the 12 email examples as phishing or legitimate?

The current survey supports descriptive summaries of the selected response categories. It does not support a verified comparison of AI-generated phishing with human-written phishing because the public project archive does not contain a complete, independently verifiable source mapping for every email example.

The study does not test the performance of an automated phishing detector. It does not estimate objective detection accuracy unless a verified answer key and the original participant-level response file are available and validated.

## 3. Research design

The survey uses a quantitative, descriptive design. Participants classify email examples into two response categories:

- `phishing`
- `legitimate`

The supplied survey export contains 27 participant records and 12 email-classification questions, producing 324 possible classifications. The unit of analysis for the published response-frequency tables is the classification, aggregated by email example.

The exact recruitment method, eligibility criteria, survey presentation order, randomization procedure, and participant instructions should be described from the original survey protocol. Do not infer or invent these details.

## 4. Dataset and variables

### 4.1 Available survey data

The local original survey export is processed into a long-format dataset with one record per participant and email example. The public aggregate file `data/processed/email_classification_summary.csv` contains one row per email example and response counts.

The observed aggregate results in the supplied export are:

- Participants: 27.
- Email examples: 12.
- Total classifications: 324.
- Phishing selections: 181 (55.9%).
- Legitimate selections: 143 (44.1%).
- Missing or unrecognized email classifications: 0 in the supplied export.

These are response frequencies, not measures of accuracy.

### 4.2 Variables

| Variable | Role | Definition |
|---|---|---|
| `participant_id` | Identifier | Pseudonymous identifier generated during local processing |
| `email_id` | Grouping variable | Identifier of an email example |
| `predicted_label` | Observed response | Participant selection: `phishing` or `legitimate` |
| `true_label` | Ground truth | Independently verified correct class of an email |
| `email_source` | Stimulus provenance | Documented origin or generation method of an email |
| `age_group` | Descriptive variable | Participant's age category as collected in the survey |
| `cyber_knowledge` | Descriptive variable | Self-reported cybersecurity knowledge |
| `phishing_experience` | Descriptive variable | Self-reported previous phishing experience |
| `first_indicator` | Descriptive variable | First indicator noticed by the participant |
| `confidence` | Secondary measure | Self-reported confidence, if collected and complete |

Confidence responses are incomplete in the supplied export and must not be treated as a complete group-level measure.

## 5. Data collection and privacy

The survey export supplied for this analysis contains 27 records dated November 5, 2026. The actual recruitment method, eligibility criteria, presentation order, and consent procedure must be documented from the original survey materials; this methodology does not invent them.

Raw survey exports must be stored in restricted local storage and must not be committed to the public repository. Before publication, direct identifiers and indirect identifiers that could reveal a participant must be removed or appropriately protected. Only reviewed aggregate outputs should be published.

Because the supplied responses include participants under 18, the authors must verify institutional requirements for research involving minors, including the required participant assent and parent/guardian permission where applicable. Do not claim approval or consent unless supported by the actual records.

## 6. Data processing

Python and Pandas are used to inspect and summarize survey responses.

The processing sequence is:

1. Load the original survey export from restricted local storage.
2. Inspect column names, data types, missing values, and duplicate records.
3. Map the 12 email-question columns explicitly and verify the mapping against the questionnaire.
4. Normalize participant selections to `phishing` and `legitimate`; ambiguous answers remain unclassified.
5. Reshape the responses into one record per participant and email example.
6. Generate aggregate response counts and percentages.
7. Save participant-level intermediate files locally and publish only approved aggregate outputs.

The raw CSV is not modified by the processing script.

## 7. Analysis plan

### 7.1 Descriptive measures

For each email example:

\[
\text{Phishing selection percentage} = \frac{n_{phishing}}{n_{phishing}+n_{legitimate}} \times 100.
\]

The overall response distribution is calculated by summing selections across all 12 examples:

\[
\text{Overall category percentage} = \frac{N_{category}}{N_{valid\ classifications}} \times 100.
\]

These values describe participants' choices only.

### 7.2 Classification performance measures

Accuracy, precision, recall, specificity, F1-score, and a confusion matrix require participant predictions and a verified answer key for all email examples. A complete key must include a correct class and documented source for each email, and the labels must be checked against the original stimuli.

The processing script keeps accuracy disabled by default. Enable it only after independent verification of all 12 email labels and sources and after reproducing the results from the original response export. Never use an old summary CSV or a chart as a substitute for source data and a verified answer key.

### 7.3 Confidence and response time

Confidence and response-time analyses are not included unless the original data contain complete, valid measurements and the survey protocol confirms how these variables were collected.

## 8. Repeated observations

Each participant evaluates multiple email examples. Therefore, individual email classifications from one participant are repeated observations and should not be treated as 324 independent participants in inferential statistical tests. The current report uses descriptive frequencies only.

## 9. Validity and limitations

The study includes 27 participant records and 12 email examples. The findings should not be generalized to a wider population without further sampling. The public aggregate file does not permit an independent participant-level reanalysis. The source and correct label of every email example must be documented before objective detection performance or AI-authorship claims can be made. Confidence responses are incomplete. These limitations must remain visible in the paper.

## 10. Ethics

The authors must verify the institution's requirements and document the actual consent process. Because the supplied survey export includes participants under 18, the authors must confirm the applicable assent and parent/guardian permission requirements with the institution before external publication. This document does not claim an ethics approval identifier that is not documented in project records.

## 11. Separate synthetic benchmark

The files `src/benchmark.py`, `config.json`, and `data/sample/responses.csv` form a separate synthetic demonstration pipeline. The sample is constructed test data used to demonstrate metric calculation for hypothetical email categories. It is not part of the 27-participant survey and must never be used to populate the survey paper's Results section.

## 12. Reproducibility

The public repository supports the synthetic benchmark and regeneration of descriptive response-frequency charts from the committed aggregate CSV. Processing the original participant-level survey requires the private local CSV. The raw file and any identifying fields must not be uploaded to public CI.
