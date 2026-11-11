# AI-Generated vs Human-Written Phishing Emails: A User Detection Study

**Zhadyra Kurmanova and Meirim Yersultan**

Narxoz University  
Email: zhadyra.kurmanova@narxoz.kz; meirim.yersultan@narxoz.kz

GitHub: https://github.com/zhadritto/ai-phishing-literature-review

## Abstract

The increasing availability of generative artificial intelligence has created new challenges for email security. This study investigates students' ability to identify AI-generated phishing, human-written phishing, and legitimate email messages. Twenty-seven participants completed an anonymous Google Forms survey containing 12 email classification tasks: three AI-generated phishing emails, three human-written phishing emails, and six legitimate emails. In total, 324 classifications were analyzed using a documented stimulus answer key. Overall classification accuracy was 79.3% (257/324), phishing recall was 85.2% (138/162), and the false positive rate for legitimate messages was 26.5% (43/162). Detection recall was 85.2% for both AI-generated and human-written phishing (69/81 each). These results show similar aggregate detection rates for the two phishing sources in this small survey; they do not establish equivalence between the sources. The study combines survey findings with a review of prior phishing-detection research and identifies limitations related to sample size, stimulus selection, and self-reported background variables.

**Keywords:** AI-generated phishing, human detection, cybersecurity, large language models, phishing awareness, email security.

## I. INTRODUCTION

### A. Background

Phishing remains an important cybersecurity threat because attackers use deceptive messages to manipulate individuals into disclosing sensitive information, opening malicious links, or performing unauthorized actions.

The development of Large Language Models has introduced new possibilities for generating convincing email content. AI-generated messages can be grammatically correct, professionally structured, and adapted to specific communication contexts.

Traditional phishing awareness often emphasizes warning signs such as spelling mistakes, suspicious links, unusual sender addresses, and urgent requests. However, the increasing fluency of AI-generated messages makes it important to examine how people evaluate email authenticity.

### B. Research Problem

Although phishing awareness has received considerable attention, users continue to face difficulties identifying deceptive messages. AI-generated phishing introduces additional challenges because messages may appear more natural and professionally written.

The central research question is:

**How accurately do students identify AI-generated phishing, human-written phishing, and legitimate emails, and does detection differ by phishing source?**

### C. Research Objectives

The objectives of this study are:

1. To examine existing research on human phishing detection.
2. To measure how accurately students classify phishing and legitimate email examples.
3. To compare detection of AI-generated and human-written phishing emails.
4. To examine the role of cybersecurity awareness in email evaluation.
5. To identify challenges associated with AI-generated phishing communication.

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

This project contributes a student-survey perspective by examining how participants classify a collection of email examples.

## III. METHODOLOGY

### A. Research Design

The project combines a literature-based review with a descriptive survey analysis.

Participants were presented with email examples and asked to classify each message using two response categories:

- Phishing
- Legitimate

The survey also included demographic and cybersecurity-related questions.

### B. Participants and Dataset

The Google Forms export contains 27 participant records. Each participant classified 12 email examples, yielding 324 non-missing classification responses. The stimulus set consisted of three AI-generated phishing emails (01, 05, 09), three human-written phishing emails (03, 07, 11), and six legitimate emails (02, 04, 06, 08, 10, 12), as recorded in `data/metadata/email_answer_key.csv`. The analysis uses anonymous participant-level responses. The accuracy of source attribution depends on the correctness of this answer key.

### C. Data Processing

Responses were read from the Google Forms CSV export. The twelve classification columns (questions 4–15) were mapped in order to email_01 through email_12. The Russian response choices “Фишинговое письмо” and “Настоящее письмо” were mapped to phishing and legitimate, respectively, and compared against the documented answer key. All 27 participants provided answers to all 12 classification questions. Python and Pandas were used to compute classification counts and descriptive metrics.

### D. Evaluation Measures

Accuracy is the proportion of all correct classifications. Phishing recall is the proportion of phishing examples correctly identified as phishing. False positive rate (FPR) is the proportion of legitimate examples incorrectly identified as phishing. Precision is the proportion of phishing predictions that are actually phishing, and F1-score is the harmonic mean of precision and recall. For the source comparison, recall was computed separately for AI-generated and human-written phishing examples. Percentages are based on pooled email classifications; repeated responses from the same participant are not independent observations. Participant-level bootstrap confidence intervals were calculated using 5,000 resamples of the 27 participants with replacement (seed 42), retaining all twelve responses for each sampled participant.

The confidence question was not analyzed at group level because only one participant provided a non-missing confidence response.

## IV. RESULTS

### A. Overall Classification Performance

All 27 participants classified all 12 emails, producing 324 classifications. Of these, 257 were correct and 67 incorrect. Participants selected “phishing” 181 times (55.9%) and “legitimate” 143 times (44.1%). Unlike response frequency alone, the following performance metrics use the documented email answer key.

| Measure | Value | Numerator / Denominator |
|---|---:|---:|
| Overall accuracy | 79.3% | 257 / 324 |
| Phishing recall | 85.2% | 138 / 162 |
| Phishing precision | 76.2% | 138 / 181 |
| False positive rate | 26.5% | 43 / 162 |
| Specificity | 73.5% | 119 / 162 |
| F1-score | 80.5% | Calculated from precision and recall |

The participant-level bootstrap 95% confidence interval for overall accuracy was 68.8%–88.9%. The 95% confidence interval for the false positive rate was 14.2%–39.5%.

### B. AI-Generated vs Human-Written Phishing

| Phishing source | Correct phishing detections | Total classifications | Recall | Participant-bootstrap 95% CI |
|---|---:|---:|---:|---:|
| AI-generated | 69 | 81 | 85.2% | 74.1%–95.1% |
| Human-written | 69 | 81 | 85.2% | 75.3%–93.8% |

Both phishing sources had the same pooled recall (85.2%). The observed difference in recall (AI minus human-written) was 0.0 percentage points, with a participant-bootstrap 95% confidence interval of -6.2%–7.4%. This sample does not show an aggregate difference in recall, but the limited sample and small number of distinct phishing stimuli do not support a conclusion of equivalence.

### C. Results by Email Example

| Email | Classified phishing | Classified legitimate | Answer-key category |
|---|---:|---:|---|
| Email 01 | 24 (88.9%) | 3 (11.1%) | AI phishing |
| Email 02 | 5 (18.5%) | 22 (81.5%) | Legitimate |
| Email 03 | 23 (85.2%) | 4 (14.8%) | Human phishing |
| Email 04 | 7 (25.9%) | 20 (74.1%) | Legitimate |
| Email 05 | 24 (88.9%) | 3 (11.1%) | AI phishing |
| Email 06 | 6 (22.2%) | 21 (77.8%) | Legitimate |
| Email 07 | 25 (92.6%) | 2 (7.4%) | Human phishing |
| Email 08 | 6 (22.2%) | 21 (77.8%) | Legitimate |
| Email 09 | 21 (77.8%) | 6 (22.2%) | AI phishing |
| Email 10 | 10 (37.0%) | 17 (63.0%) | Legitimate |
| Email 11 | 21 (77.8%) | 6 (22.2%) | Human phishing |
| Email 12 | 9 (33.3%) | 18 (66.7%) | Legitimate |

Email 07 was most often classified as phishing (25/27, 92.6%), while Email 02 was most often classified as legitimate (22/27, 81.5%). Individual stimuli varied in difficulty, including among messages with the same source category.

## V. DISCUSSION

Participants correctly classified 79.3% of all email examples, with higher phishing recall (85.2%) than legitimate-email specificity (73.5%). The 26.5% false positive rate indicates that a substantial proportion of legitimate messages were incorrectly flagged as phishing. AI-generated and human-written phishing messages had identical pooled recall in this sample. This does not demonstrate that AI-generated phishing is generally no harder to detect: there were only three distinct examples from each phishing source, and the result may depend on the selected messages and participants.

Prior research on the Phish Scale and cue utilization emphasizes the role of context and warning signs in phishing detection. The present study adds descriptive survey evidence, but its design does not establish causal effects of AI authorship or cybersecurity knowledge. The technical performance benchmark in this repository evaluates software execution time and is separate from these human-detection findings.

## VI. LIMITATIONS

First, the survey included only 27 participants, limiting generalizability. Second, each participant judged 12 messages, so the 324 classifications are repeated observations rather than 324 independent participants; participant-level resampling partly addresses within-person dependence but does not account for uncertainty from selecting only 12 stimuli. Third, only three AI-generated and three human-written phishing emails were tested. Fourth, the validity of source-specific findings depends on the documented answer key and its underlying provenance. Fifth, cybersecurity knowledge and prior experience were self-reported; no causal conclusions are warranted. Finally, confidence was available for only one participant, preventing a meaningful confidence analysis.

Future research should recruit a larger and more diverse sample, use more independently validated email stimuli, document their provenance, and assess associations with cybersecurity experience using an analysis appropriate for repeated observations.

## VII. CONCLUSION

In this student survey, 27 participants classified 12 email examples each, yielding 324 responses. Overall classification accuracy was 79.3%, phishing recall was 85.2%, and the false positive rate was 26.5%. AI-generated and human-written phishing messages were each detected in 69 of 81 classifications (85.2%). These findings describe performance on the specific survey stimuli; they do not establish that the two phishing sources are equally difficult in general. The results reinforce the need for careful evaluation of suspicious messages and further research with larger participant and stimulus samples.

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
