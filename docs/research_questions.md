# Research Questions and Hypotheses

## 1. Research Title

Human Ability to Detect AI-Generated Phishing Emails: A Review of Existing Research

## 2. Research Aim

The aim of this study is to examine how university students identify phishing emails in the context of generative artificial intelligence.

The study combines a review of existing research with an empirical survey. It focuses on participants' ability to distinguish AI-generated phishing emails from AI-generated legitimate-style email examples.

All 12 email examples were generated using ChatGPT. The study does not compare AI-generated emails with independently human-written emails.

## 3. Research Objectives

The study has the following objectives:

1. To review existing research on human phishing detection.
2. To examine how accurately students identify AI-generated phishing emails.
3. To compare detection recall across six AI-generated phishing email examples.
4. To explore the relationship between self-reported cybersecurity knowledge and phishing detection performance.
5. To examine the relationship between previous phishing experience and detection performance.
6. To identify the indicators participants primarily use when evaluating email messages.

## 4. Research Questions

**RQ1.** How accurately can university students identify AI-generated phishing emails?

**RQ2.** How does students' detection performance vary across different AI-generated phishing email examples?

**RQ3.** How are self-reported cybersecurity knowledge and previous phishing experience related to phishing detection performance?

**RQ4.** Which indicators do participants primarily rely on when identifying phishing emails?

## 5. Research Hypotheses

### Hypothesis 1: Cybersecurity Knowledge

**H0₁:** There is no association between self-reported cybersecurity knowledge and phishing detection performance.

**H1₁:** Participants with higher self-reported cybersecurity knowledge demonstrate higher phishing detection performance.

### Hypothesis 2: Previous Phishing Experience

**H0₂:** There is no difference in phishing detection performance between participants with and without previous phishing experience.

**H1₂:** Participants with previous phishing experience demonstrate higher phishing detection performance than participants without such experience.

### Hypothesis 3: Detection Across Email Examples

**H0₃:** Detection recall is equal across the six selected AI-generated phishing email examples.

**H1₃:** Detection recall differs across at least two of the six selected AI-generated phishing email examples.

These hypotheses are exploratory. The available results primarily support descriptive analysis, and differences should not be presented as statistically significant without appropriate hypothesis testing.

## 6. Operational Definitions

| Concept | Operational Definition |
|---|---|
| AI-generated phishing | A phishing email created using ChatGPT and labeled as phishing in the verified answer key |
| AI-generated legitimate-style email | A non-phishing email example created using ChatGPT and labeled as legitimate in the verified answer key |
| Detection accuracy | Proportion of participant classifications matching the verified email labels |
| Phishing recall | Proportion of phishing classifications correctly identified by participants |
| Per-email recall | Proportion of participants who correctly identify a particular phishing email |
| Precision | Proportion of predicted phishing classifications that are actually phishing |
| Specificity | Proportion of legitimate-style emails correctly identified |
| False positive rate | Proportion of legitimate-style emails incorrectly classified as phishing |
| Cybersecurity knowledge | Participant's self-reported cybersecurity knowledge level |
| Previous phishing experience | Participant's self-reported experience with phishing messages |
| First detection indicator | The characteristic participants report checking first when evaluating an email |

## 7. Scope and Limitations

The empirical survey contains 12 email examples:

- 6 AI-generated phishing emails.
- 6 AI-generated legitimate-style emails.

All examples were generated using ChatGPT.

The survey included 27 participants and 324 email classifications.

The study evaluates the selected examples rather than all possible phishing messages.

There is no independently human-written comparison group. Therefore, the study cannot determine whether AI-generated phishing emails are more or less difficult to detect than human-written phishing emails.

The number of participants and email stimuli is limited. Comparisons across individual phishing examples are exploratory and should be interpreted cautiously.

Self-reported cybersecurity knowledge does not represent an objective cybersecurity knowledge test.

The legitimate-style emails are simulated rather than independently collected real-world correspondence.

## 8. Relationship Between Research Questions and Analysis

| Research Question | Data | Analysis |
|---|---|---|
| RQ1 | Six AI-generated phishing examples | Overall phishing recall and classification accuracy |
| RQ2 | Classifications of six AI-generated phishing examples | Per-email detection recall, descriptive comparison, and bootstrap confidence intervals |
| RQ3 | Cybersecurity knowledge, previous experience, and classification results | Descriptive and exploratory group comparisons |
| RQ4 | First detection indicator | Frequency and percentage distribution |

The analysis uses verified ground-truth labels and participant responses from 27 participants, covering 324 email classifications.

The main observed results are:

| Metric | Result |
|---|---:|
| Participants | 27 |
| Total classifications | 324 |
| Overall accuracy | 79.3% |
| Phishing recall | 85.2% |
| Precision | 76.2% |
| False positive rate | 26.5% |
| F1-score | 80.5% |

Per-email phishing recall ranges from 77.8% to 92.6%.

These results are descriptive. The observed differences across phishing examples do not, by themselves, establish statistical significance.

Detailed results are presented in `docs/paper_draft.md`, the accompanying PDF research paper, and `README.md`.
