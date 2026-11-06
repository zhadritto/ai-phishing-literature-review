# AI-Generated vs Human-Written Phishing Emails: A User Detection Study

**Zhadyra Kurmanova and Meirim Yersultan**

Narxoz University  
Email: zhadyra.kurmanova@narxoz.kz; meirim.yersultan@narxoz.kz

GitHub: https://github.com/zhadritto/ai-phishing-literature-review

## Abstract

The increasing availability of generative artificial intelligence has created new challenges for email security. Large Language Models (LLMs) can generate fluent and convincing phishing messages, potentially making fraudulent emails more difficult for users to identify. This study examines human responses to phishing and legitimate email examples through a student survey.

The survey included 27 participants who classified 12 email examples, resulting in 324 recorded classifications. Participants selected “phishing” in 181 cases (55.9%) and “legitimate” in 143 cases (44.1%). The results demonstrate variation in how participants judged individual email examples. However, these response frequencies do not represent detection accuracy because verified ground-truth labels and the source classification of each email were not available in the response export.

The study combines empirical survey analysis with existing research on human phishing detection and AI-generated malicious communication. Data processing and visualization were conducted using Python and Pandas. The findings provide descriptive insight into student judgements and highlight the importance of contextual awareness and careful email evaluation.

**Keywords:** AI-generated phishing, human detection, cybersecurity, large language models, phishing awareness, email security.

## I. INTRODUCTION

### A. Background

Phishing remains an important cybersecurity threat because attackers use deceptive messages to manipulate individuals into disclosing sensitive information, opening malicious links, or performing unauthorized actions.

The development of Large Language Models has introduced new possibilities for generating convincing email content. AI-generated messages can be grammatically correct, professionally structured, and adapted to specific communication contexts.

Traditional phishing awareness often emphasizes warning signs such as spelling mistakes, suspicious links, unusual sender addresses, and urgent requests. However, the increasing fluency of AI-generated messages makes it important to examine how people evaluate email authenticity.

### B. Research Problem

Although phishing awareness has received considerable attention, users continue to face difficulties identifying deceptive messages. AI-generated phishing introduces additional challenges because messages may appear more natural and professionally written.

The central research question is:

**How do people identify phishing emails in a selection of AI-generated phishing and legitimate email examples?**

### C. Research Objectives

The objectives of this study are:

1. To examine existing research on human phishing detection.
2. To investigate how students classify phishing and legitimate email examples.
3. To analyze response patterns across 12 email examples.
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

The available survey export contains:

- 27 participant records.
- 12 email-classification questions.
- 324 recorded classifications.

The analysis uses anonymized response data and summarizes participant choices across the email examples.

### C. Data Processing

Python and Pandas were used for data inspection, processing, and statistical summaries.

The analysis included:

- Dataset structure inspection.
- Column identification.
- Missing-value assessment.
- Duplicate-record inspection.
- Response-frequency calculation.
- Summary-table generation.
- Data visualization.

### D. Evaluation Measures

The descriptive analysis reports the number and percentage of participants selecting each response category.

Formal classification metrics, including Accuracy, Precision, Recall, Specificity, and F1-score, require verified ground-truth labels for every email stimulus.

These metrics are not reported in the current analysis because the available response export does not contain a verified answer key.

The confidence question was also excluded from group-level statistical analysis because most participant records did not contain a confidence response.

## IV. RESULTS

### A. Overall Classification Results

A total of 324 email classifications were recorded.

| Response category | Responses | Percentage |
|---|---:|---:|
| Phishing | 181 | 55.9% |
| Legitimate | 143 | 44.1% |
| Total | 324 | 100% |

The results indicate that participants selected the phishing option more frequently than the legitimate option.

These figures represent response choices rather than objectively verified correct classifications.

### B. Results by Email Example

| Email | Phishing | Legitimate |
|---|---:|---:|
| Email 01 | 24 (88.9%) | 3 (11.1%) |
| Email 02 | 5 (18.5%) | 22 (81.5%) |
| Email 03 | 23 (85.2%) | 4 (14.8%) |
| Email 04 | 7 (25.9%) | 20 (74.1%) |
| Email 05 | 24 (88.9%) | 3 (11.1%) |
| Email 06 | 6 (22.2%) | 21 (77.8%) |
| Email 07 | 25 (92.6%) | 2 (7.4%) |
| Email 08 | 6 (22.2%) | 21 (77.8%) |
| Email 09 | 21 (77.8%) | 6 (22.2%) |
| Email 10 | 10 (37.0%) | 17 (63.0%) |
| Email 11 | 21 (77.8%) | 6 (22.2%) |
| Email 12 | 9 (33.3%) | 18 (66.7%) |

### C. Main Observations

Email 07 received the highest number of phishing classifications, with 25 out of 27 participants selecting this response.

Email 02 received the highest number of legitimate classifications, with 22 out of 27 participants selecting this response.

These differences demonstrate that participants responded differently to the individual email examples.

However, without verified message labels, these patterns cannot establish which examples were correctly or incorrectly classified.

## V. DISCUSSION

The survey provides descriptive insight into how students evaluate different email examples.

The overall response distribution shows that participants selected phishing more frequently than legitimate. The differences between individual email examples also demonstrate variation in participant judgement.

These observations are relevant to existing research on human phishing detection.

The Phish Scale emphasizes the importance of contextual relevance and message characteristics. Research by Sturman et al. similarly highlights the importance of recognizing and interpreting phishing indicators.

The development of generative AI makes this topic particularly relevant because professional language and natural sentence structure can make suspicious messages appear more authentic.

The findings should nevertheless be interpreted within the limitations of the available dataset. Response frequencies cannot establish detection accuracy without verified labels.

## VI. LIMITATIONS

Several limitations should be considered when interpreting the results.

First, the survey included 27 participants, and the findings should not be generalized to the entire population.

Second, each participant classified multiple email examples, meaning that the observations are repeated classifications rather than independent participants.

Third, the available response export does not contain verified ground-truth labels or source-provenance information for all 12 email examples.

Fourth, confidence responses were incomplete, preventing meaningful group-level confidence analysis.

Finally, the available dataset does not document an automated-system comparison or a verifiable warm-up exclusion procedure.

Future research should include a verified answer key, documented email-generation procedures, and a larger participant sample.

## VII. CONCLUSION

This study examined human responses to phishing and legitimate email examples through a student survey and a review of existing cybersecurity research.

The survey included 27 participants and 12 email examples, producing 324 recorded classifications. Participants selected phishing in 55.9% of cases and legitimate in 44.1% of cases.

The results demonstrate variation in how participants evaluate different email examples and provide a descriptive foundation for understanding human responses to potentially deceptive email communication.

Combined with existing research, the project highlights the importance of cybersecurity awareness, contextual evaluation, and careful inspection of email characteristics in an environment increasingly influenced by generative AI.

Further research using verified email labels, documented source conditions, and a larger sample would allow more detailed evaluation of human detection performance.

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
