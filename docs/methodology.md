# Methodology Passport Card

## 1. Project Information

Title: Human Ability to Detect AI-Generated Phishing Emails:
A Review of Existing Research

Authors:
- Zhadyra Kurmanova
- Meirim Yersultan

Repository:
https://github.com/zhadritto/ai-phishing-literature-review

Status: Research planning and measurement pipeline development.
No participant data have been collected.

The literature review will inform the proposed experiment.
For Task 2, we prepare its methodology and a measurement script
using synthetic sample data.

## 2. Research Questions

The research questions are inherited from Task 1.

**RQ1:** What levels of human detection accuracy for AI-generated phishing emails are reported in existing research?

**RQ2:** Does the use of generative AI in phishing emails affect people's ability to identify phishing compared with traditional human-written phishing emails?

**RQ3:** What factors influence people's ability to identify AI-generated phishing emails?

RQ2 is the primary focus of the Task 2 measurement pipeline.

## 3. Research Type

The proposed experiment uses mixed methods.

The quantitative component measures phishing detection recall,
false positive rate, response time, and confidence.

The qualitative component examines participants' explanations
of the features they used to classify emails.

This combination allows us to examine both detection performance
and the reasons behind classification decisions.

The current script implements the quantitative measurement
component only.

## 4. Hypotheses and Variables

The hypotheses are inherited from Task 1 and organized around three research questions.

### RQ1: Reported Detection Accuracy

**H0:** Reported human detection accuracy for AI-generated phishing emails does not differ from chance-level performance and does not vary meaningfully across study conditions.

**H1:** Reported human detection accuracy for AI-generated phishing emails differs from chance-level performance and varies across study conditions.

- Independent variables: Study and email conditions, including AI-generation method, personalization, styling, training, and study design.
- Dependent variable: Reported human detection accuracy.
- Potential confounders: Cybersecurity knowledge, previous experience, age, education, email quality, and measurement method.

RQ1 is primarily descriptive and will be addressed through synthesis of published research. The current benchmark does not compare multiple published studies or directly test chance-level performance.

### RQ2: Comparison of AI-Generated and Human-Written Phishing

**H0:** There is no significant difference between people's ability to identify AI-generated phishing emails and traditional human-written phishing emails.

**H1:** People are less able to identify AI-generated phishing emails than traditional human-written phishing emails.

- Independent variable: Email authorship (AI-generated or human-written).
- Dependent variable: Human phishing-detection accuracy.
- Potential confounders: Cybersecurity knowledge, previous experience, training, age, education, email quality, grammatical errors, personalization, and study design.

RQ2 is the primary focus of the Task 2 measurement plan.

The benchmark calculates detection recall for each phishing category:

- Recall_AI = TP_AI / (TP_AI + FN_AI)
- Recall_Human = TP_Human / (TP_Human + FN_Human)

The primary descriptive comparison is:

Difference = Recall_AI − Recall_Human

A negative difference is consistent with the direction of H1. However, statistical inference using real participant data would be required to evaluate whether the observed difference is statistically significant.

### RQ3: Human Factors Influencing Detection Accuracy

**H0:** Cybersecurity awareness, previous phishing experience, and security-awareness training are not significantly associated with detection accuracy.

**H1:** Higher cybersecurity awareness, previous phishing experience, and security-awareness training are associated with higher accuracy in detecting AI-generated phishing emails.

- Independent variables: Cybersecurity awareness, previous phishing experience, and security-awareness training.
- Dependent variable: Human phishing-detection accuracy.
- Potential confounders: Age, education, technical experience, occupation, email complexity, personalization, AI model, and experimental design.

RQ3 will be addressed through published literature and may be examined empirically in future research if the required participant-level variables are collected.

### Scope and Limitations

The current Task 2 benchmark operationalizes RQ2 using a reproducible Python measurement pipeline.

RQ1 and RQ3 are retained to maintain consistency with Task 1, but the present implementation does not independently test all three research questions.

The included synthetic dataset is used only for demonstrating and validating the calculation pipeline. No conclusions about real human phishing-detection ability are drawn from synthetic results.

## 5. Variable Matrix

| Type | Variable | Definition |
|---|---|---|
| Independent | Source of phishing email | AI-generated or human-written |
| Dependent | Correct detection | Phishing correctly identified: 1; missed: 0 |
| Dependent | Response time | Seconds taken to classify an email |
| Dependent | Confidence | Participant rating from 1 to 5 |
| Controlled | Instructions | Identical instructions for all participants |
| Controlled | Interface | Identical display and response options |
| Controlled | Test set | Fixed, versioned set of safe email mockups |
| Controlled | Category counts | Equal numbers of AI and human phishing emails |
| Controlled | Email characteristics | Matched topics, approximate length, and difficulty |
| Controlled | Analysis environment | Specified Python runtime and versioned script |

Presentation order will be randomised and recorded.
Randomisation is a procedural control, not a fixed presentation order.

Cybersecurity experience will be recorded as a participant
characteristic. It is not a randomly assigned variable.

## 6. Primary Metric

Phishing detection recall:

Recall = TP / (TP + FN)

TP: A phishing email correctly classified as phishing.
FN: A phishing email incorrectly classified as legitimate.

Recall is calculated separately for AI-generated phishing
and human-written phishing.

Primary comparison:

Recall_AI - Recall_Human

A negative difference indicates lower detection recall for AI
phishing. A positive difference indicates higher recall for AI
phishing.

The main study will calculate recall per participant and account
for repeated measurements when comparing conditions.

## 7. Guardrail Metrics

### False Positive Rate

FPR = FP / (FP + TN)

FP: A legitimate email incorrectly classified as phishing.
TN: A legitimate email correctly classified as legitimate.

The provisional threshold is FPR <= 0.20. This represents a
project-defined tolerance of no more than one false alarm per
five legitimate-email classifications.

We use this threshold to identify excessive false alarms that
could make a detection strategy impractical. It is a planning
criterion, not a published standard or an empirically validated
cut-off.

During the pilot, we will assess whether this tolerance is
appropriate. Any revision will be documented and fixed before
main data collection. We will report the observed FPR regardless
of whether it passes the threshold.

### Data Validity

Target: zero invalid records in an accepted input dataset.

The script rejects:
- Missing required values.
- Unknown email categories or response labels.
- Duplicate participant-email responses.
- Non-positive or non-finite response times.
- Confidence ratings outside the integer range 1 to 5.
- Inconsistent categories for the same email identifier.

## 8. Secondary Metrics

- False negative rate: FN / (TP + FN).
- Mean response time in seconds.
- Mean confidence rating from 1 to 5.

False negative rate equals 1 minus recall. It is reported for
interpretation rather than treated as an independent outcome.

## 9. Baseline

Baseline condition: Human-written phishing emails.

Experimental condition: AI-generated phishing emails.

Legitimate emails are a separate category used to measure
false alarms.

The same participants will assess both phishing conditions.
The email sets must be comparable in topic, length, and difficulty.

## 10. Planned Procedure

1. Obtain informed consent.
2. Record relevant cybersecurity experience.
3. Present identical instructions.
4. Show safe email mockups in randomised order.
5. Ask participants to select phishing or legitimate.
6. Record response time and confidence.
7. Collect short explanations of classification decisions.
8. Calculate detection metrics.
9. Compare phishing conditions using paired participant data.

The classification interface and participant recruitment are
planned work. The current script processes recorded responses.

## 11. Analysis Plan

The Task 2 script calculates descriptive metrics from a sample.

For the main study, recall will be calculated for each participant
in both phishing conditions.

The statistical test and sample size justification will be specified
before main data collection. Effect estimates and confidence
intervals will be reported.

Repeated answers from one participant will not be treated as
independent participants. A fuller analysis may also account
for differences between individual emails.

Qualitative explanations will be coded into categories such as
sender information, urgency, links, and language cues.

## 12. Threats to Validity

| Threat | Planned mitigation |
|---|---|
| Unequal email difficulty | Match scenarios and pilot the email set |
| Learning and order effects | Randomise and record presentation order |
| Limited participant diversity | Recruit participants with different experience levels |
| Increased suspicion during testing | Use consistent instructions and acknowledge the limitation |
| Prior exposure to messages | Separate training and test examples |
| Laboratory conditions | Acknowledge limits when generalising to real email use |

Randomisation reduces systematic order bias but does not remove
all learning effects.

## 13. Ethics

Only safe email mockups will be used, without harmful links
or attachments.

Participation will be voluntary, with informed consent.

Public data will use anonymous participant identifiers.
Personal information and consent records will not be published.

## 14. Reproducibility

The repository includes:
- A README with launch instructions.
- This methodology card.
- A Dockerfile specifying the Python image version.
- A configuration file.
- An executable measurement script.
- Eight synthetic sample records.
- A .gitignore file.
- An MIT license.

The script prints calculated metrics and saves a JSON output file.

The Docker base image is pinned by version and SHA-256 digest.
The script uses only the Python standard library, so no external Python packages are required.

## 15. Expected Outcome at This Stage

A successful sample run will demonstrate that the measurement
pipeline reads valid input and calculates the expected metrics.

Synthetic sample results are not research findings and cannot
support accepting or rejecting the research hypotheses.

The literature review, participant recruitment, data collection,
and inferential analysis remain future work.
