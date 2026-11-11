# Human Ability to Detect AI-Generated Phishing Emails: A Review of Existing Research and Student Survey

**Zhadyra Kurmanova and Meirim Yersultan**

Narxoz University  
Email: zhadyra.kurmanova@narxoz.kz; meirim.yersultan@narxoz.kz

GitHub: https://github.com/zhadritto/ai-phishing-literature-review

## Abstract

The increasing availability of generative artificial intelligence has created new challenges for email security. This study examines students' ability to distinguish AI-generated phishing emails from AI-generated legitimate-style emails. Twenty-seven participants completed an anonymous Google Forms survey containing 12 email classification tasks: six phishing messages and six legitimate-style messages, all generated using artificial intelligence. In total, 324 classifications were analyzed using a documented stimulus answer key. Overall classification accuracy was 79.3% (257/324), phishing recall was 85.2% (138/162), and the false positive rate was 26.5% (43/162). Detection recall varied across the six phishing examples, ranging from 77.8% to 92.6%. The findings suggest that participants were generally able to identify phishing messages but also incorrectly classified some legitimate-style messages as phishing. The study combines these descriptive survey findings with a review of existing research and discusses limitations related to sample size, stimulus selection, and self-reported cybersecurity knowledge.

**Keywords:** AI-generated phishing, human detection, cybersecurity, large language models, phishing awareness, email security.

## I. INTRODUCTION

### A. Background

Phishing remains an important cybersecurity threat because attackers use deceptive messages to manipulate individuals into disclosing sensitive information, opening malicious links, or performing unauthorized actions.

The development of large language models has introduced new possibilities for generating convincing email content. AI-generated messages can be grammatically correct, professionally structured, and adapted to specific communication contexts.

Traditional phishing awareness often emphasizes warning signs such as spelling mistakes, suspicious links, unusual sender addresses, and urgent requests. However, the increasing fluency of AI-generated messages makes it important to examine how people evaluate email authenticity.

### B. Research Problem

Although phishing awareness has received considerable attention, users continue to face difficulties identifying deceptive messages. AI-generated phishing introduces additional challenges because messages may appear natural and professionally written.

The central research question is:

**How accurately do students distinguish AI-generated phishing emails from AI-generated legitimate-style emails, and how does detection performance vary across individual phishing examples?**

### C. Research Objectives

The objectives of this study are:

1. To examine existing research on human phishing detection.
2. To measure how accurately students classify phishing and legitimate-style email examples.
3. To compare detection recall across six AI-generated phishing examples.
4. To explore the relationship between self-reported cybersecurity knowledge and email classification performance.
5. To identify challenges associated with evaluating AI-generated email communication.

## II. LITERATURE REVIEW

### A. Human Phishing Detection

Human phishing detection depends on the ability to recognize suspicious characteristics and evaluate the context of an email.

Steves, Greene, and Theofanos introduced the Phish Scale, which considers message characteristics and contextual relevance when assessing phishing difficulty.

Research indicates that users may overlook suspicious characteristics when messages appear relevant, familiar, or professionally written.

### B. The Role of Context and Decision-Making

Sturman et al. examined the relationship between phishing knowledge, cue utilization, and decision-making styles. Their research highlights the importance of recognizing and interpreting relevant indicators when distinguishing phishing from legitimate messages.

This demonstrates that cybersecurity knowledge alone is not necessarily sufficient. Users must also apply that knowledge when evaluating individual messages.

### C. Artificial Intelligence and Phishing

Generative AI has made it possible to create convincing phishing messages with fewer obvious grammatical and structural errors.

Heiding et al. investigated the use of large language models in generating and detecting phishing emails. Their research demonstrates the relevance of generative AI to modern phishing threats.

These developments highlight the importance of studying human detection capabilities in environments where malicious messages may appear increasingly authentic.

### D. Research Relevance

Existing research provides an important foundation for understanding phishing detection, human decision-making, and AI-generated malicious communication.

This project contributes a student-survey perspective by examining how participants classify a collection of AI-generated email examples. Unlike studies comparing human-written and AI-written messages, this survey focuses on classification performance within an entirely AI-generated stimulus set.

## III. METHODOLOGY

### A. Research Design

The project combines a literature-based review with a descriptive survey analysis.

Participants were presented with email examples and asked to classify each message using two response categories:

- Phishing
- Legitimate

The survey also included demographic and cybersecurity-related questions.

### B. Participants and Dataset

The Google Forms export contains 27 participant records. Each participant classified 12 email examples, yielding 324 non-missing classification responses.

All 12 email examples were generated using ChatGPT. The stimulus set consisted of:

- Six AI-generated phishing emails: 01, 03, 05, 07, 09, and 11.
- Six AI-generated legitimate-style emails: 02, 04, 06, 08, 10, and 12.

The correct classification labels and stimulus provenance are documented in `data/metadata/email_answer_key.csv` and `docs/email_stimuli.md`.

The analysis uses anonymous participant-level responses. Because no independently human-written stimuli were included, the study does not compare detection performance between human-written and AI-generated emails.

### C. Data Processing

Responses were read from the Google Forms CSV export. The twelve classification columns (questions 4–15) were mapped in order to `email_01` through `email_12`.

The Russian response choices “Фишинговое письмо” and “Настоящее письмо” were mapped to phishing and legitimate, respectively, and compared against the documented answer key.

All 27 participants provided answers to all 12 classification questions. Python and Pandas were used to compute classification counts and descriptive metrics.

### D. Evaluation Measures

Accuracy is the proportion of all correct classifications. Phishing recall is the proportion of phishing examples correctly identified as phishing. False positive rate (FPR) is the proportion of legitimate-style examples incorrectly identified as phishing. Precision is the proportion of phishing predictions that are actually phishing, and F1-score is the harmonic mean of precision and recall.

Detection recall was also calculated separately for each of the six AI-generated phishing examples.

Percentages are based on pooled email classifications. Because each participant evaluated 12 messages, repeated responses from the same participant are not independent observations.

Participant-level bootstrap confidence intervals were calculated using 5,000 resamples of the 27 participants with replacement (seed 42), retaining all twelve responses for each sampled participant.

The confidence question was not analyzed at group level because only one participant provided a non-missing confidence response.

## IV. RESULTS

### A. Overall Classification Performance

All 27 participants classified all 12 emails, producing 324 classifications. Of these, 257 were correct and 67 incorrect.

Participants selected “phishing” 181 times (55.9%) and “legitimate” 143 times (44.1%).

| Measure | Value | Numerator / Denominator |
|---|---:|---:|
| Overall accuracy | 79.3% | 257 / 324 |
| Phishing recall | 85.2% | 138 / 162 |
| Phishing precision | 76.2% | 138 / 181 |
| False positive rate | 26.5% | 43 / 162 |
| Specificity | 73.5% | 119 / 162 |
| F1-score | 80.5% | Calculated from precision and recall |

The previously calculated participant-level bootstrap 95% confidence interval for overall accuracy was 68.8%–88.9%. The corresponding interval for the false positive rate was 14.2%–39.5%.

The confusion matrix is provided in `reports/figures/survey_confusion_matrix.png`.

### B. Detection of Individual AI-Generated Phishing Emails

The survey included six AI-generated phishing messages. Detection recall was calculated separately for each example.

| Phishing email | Correct detections | Total classifications | Recall |
|---|---:|---:|---:|
| Email 01 | 24 | 27 | 88.9% |
| Email 03 | 23 | 27 | 85.2% |
| Email 05 | 24 | 27 | 88.9% |
| Email 07 | 25 | 27 | 92.6% |
| Email 09 | 21 | 27 | 77.8% |
| Email 11 | 21 | 27 | 77.8% |
| **Overall** | **138** | **162** | **85.2%** |

Email 07 achieved the highest detection recall (92.6%), while Emails 09 and 11 had the lowest recall (77.8% each).

The observed difference between the highest and lowest per-email recall was 14.8 percentage points. This is a descriptive difference across selected stimuli, not evidence that one type of phishing is generally easier to detect.

Participant-bootstrap confidence intervals for the individual phishing examples are presented in `reports/figures/survey_phishing_email_recall.png` and `data/processed/phishing_email_metrics.csv`.

### C. Results by Email Example

| Email | Classified phishing | Classified legitimate | Correct category |
|---|---:|---:|---|
| Email 01 | 24 (88.9%) | 3 (11.1%) | AI phishing |
| Email 02 | 5 (18.5%) | 22 (81.5%) | AI legitimate-style |
| Email 03 | 23 (85.2%) | 4 (14.8%) | AI phishing |
| Email 04 | 7 (25.9%) | 20 (74.1%) | AI legitimate-style |
| Email 05 | 24 (88.9%) | 3 (11.1%) | AI phishing |
| Email 06 | 6 (22.2%) | 21 (77.8%) | AI legitimate-style |
| Email 07 | 25 (92.6%) | 2 (7.4%) | AI phishing |
| Email 08 | 6 (22.2%) | 21 (77.8%) | AI legitimate-style |
| Email 09 | 21 (77.8%) | 6 (22.2%) | AI phishing |
| Email 10 | 10 (37.0%) | 17 (63.0%) | AI legitimate-style |
| Email 11 | 21 (77.8%) | 6 (22.2%) | AI phishing |
| Email 12 | 9 (33.3%) | 18 (66.7%) | AI legitimate-style |

Email 07 was most often classified as phishing (25/27, 92.6%), while Email 02 was most often classified as legitimate (22/27, 81.5%).

Email 10 had the highest false positive rate among legitimate-style messages (37.0%), followed by Email 12 (33.3%).

The results indicate that individual email examples varied in difficulty, even though all messages were AI-generated.

Additional classification results are presented in `reports/figures/survey_accuracy_by_email.png`.

## V. DISCUSSION

Participants correctly classified 79.3% of all email examples, with higher phishing recall (85.2%) than legitimate-style email specificity (73.5%).

The 26.5% false positive rate indicates that a substantial proportion of legitimate-style messages were incorrectly flagged as phishing.

Detection recall varied across the six AI-generated phishing examples. Email 07 was recognized by 92.6% of participants, whereas Emails 09 and 11 were recognized by 77.8%. These differences may reflect variations in the wording, context, or warning signs of individual messages, although the present analysis does not identify their causes.

Because all messages were AI-generated, these findings cannot establish whether AI-generated phishing is easier or harder to detect than human-written phishing.

Prior research on the Phish Scale and cue utilization emphasizes the role of context and warning signs in phishing detection. The present study adds descriptive survey evidence but does not establish causal effects of AI authorship or cybersecurity knowledge.

The technical performance benchmark in this repository evaluates software execution time and is separate from the human-detection findings.

## VI. LIMITATIONS

First, the survey included only 27 participants, limiting the generalizability of the results.

Second, each participant judged 12 messages, so the 324 classifications are repeated observations rather than 324 independent participants. Participant-level resampling partly addresses within-person dependence but does not account for uncertainty associated with selecting only 12 stimuli.

Third, all messages were generated using ChatGPT. The survey therefore cannot compare AI-generated messages with independently human-written messages.

Fourth, the legitimate-style examples were simulated rather than collected from real-world correspondence. Their characteristics may differ from those of authentic emails.

Fifth, cybersecurity knowledge and prior experience were self-reported, so causal conclusions are not warranted.

Finally, confidence was available for only one participant, preventing a meaningful group-level confidence analysis.

Future research should recruit a larger and more diverse sample, include independently validated human-written and AI-generated stimuli, and examine the relationship between cybersecurity experience and classification performance using methods appropriate for repeated observations.

## VII. CONCLUSION

In this student survey, 27 participants classified 12 AI-generated email examples each, yielding 324 responses. Six examples were phishing messages, and six were legitimate-style messages.

Overall classification accuracy was 79.3%, phishing recall was 85.2%, and the false positive rate was 26.5%.

Detection recall across individual phishing examples ranged from 77.8% to 92.6%, demonstrating variation in participants' ability to identify the selected messages.

These findings describe performance on the specific survey stimuli and do not establish how AI-generated phishing compares with human-written phishing.

The results reinforce the importance of careful email evaluation and support further research with larger participant samples and more diverse email stimuli.

## ACKNOWLEDGMENT

The authors would like to thank all participants who contributed to the survey and supported this research project.

## REFERENCES

[1] F. Heiding, B. Schneier, A. Vishwanath, J. Bernstein, and P. S. Park, “Devising and Detecting Phishing Emails Using Large Language Models,” IEEE Access, 2024. doi: 10.1109/ACCESS.2024.3375882.

[2] M. Steves, K. Greene, and M. Theofanos, “Categorizing Human Phishing Difficulty: A Phish Scale,” Journal of Cybersecurity, vol. 6, no. 1, 2020. doi: 10.1093/cybsec/tyaa009.

[3] D. Sturman et al., “The Roles of Phishing Knowledge, Cue Utilization, and Decision Styles in Phishing Email Detection,” Applied Ergonomics, vol. 119, 2024. doi: 10.1016/j.apergo.2024.104309.

[4] M. Butavicius, R. Taib, and S. J. Han, “Why People Keep Falling for Phishing Scams: The Effects of Time Pressure and Deception Cues on the Detection of Phishing Emails,” Computers & Security, vol. 123, 2022. doi: 10.1016/j.cose.2022.102937.

## PROJECT REPOSITORY

GitHub: https://github.com/zhadritto/ai-phishing-literature-review

**Authors:** Zhadyra Kurmanova and Meirim Yersultan.
