# Human Ability to Detect AI-Generated Phishing Emails: A Literature Review and Pilot Survey

## Abstract

The development of generative artificial intelligence has created new opportunities for cybercriminals to produce convincing phishing emails. As AI-generated messages become more sophisticated, identifying phishing attempts may become increasingly difficult for ordinary users.

This study reviews existing research on human phishing detection and examines participants' ability to distinguish AI-generated phishing emails from legitimate emails. An anonymous online survey was conducted using 12 email examples: six AI-generated phishing emails and six legitimate emails. Participants classified each email as phishing or legitimate. Detection recall, false positive rate, and the relationship between self-reported cybersecurity knowledge and detection performance were examined.

The survey included [N] participants. The average detection recall for AI-generated phishing emails was [X%], while the false positive rate for legitimate emails was [Y%]. These results provide preliminary evidence about human detection performance in the context of AI-generated phishing.

**Keywords:** phishing, artificial intelligence, generative AI, cybersecurity awareness, human behavior, phishing detection.

## 1. Introduction

Phishing is a form of cyberattack in which attackers use deceptive messages to manipulate individuals into revealing sensitive information, clicking malicious links, or performing harmful actions. Email remains one of the common channels used in phishing attacks.

The development of generative artificial intelligence, particularly large language models (LLMs), has changed the way phishing messages can be created. AI tools can generate grammatically correct, personalized, and persuasive messages, potentially reducing the effort required to prepare phishing campaigns.

Traditional phishing awareness often emphasizes suspicious links, spelling mistakes, unusual wording, and unexpected requests. However, AI-generated messages may contain fewer obvious linguistic errors, making these indicators less reliable.

Human judgment therefore remains an important part of cybersecurity. Understanding how accurately people identify suspicious emails can help improve cybersecurity awareness and training.

The main objective of this research is to examine existing findings on human phishing detection and conduct a small pilot survey assessing the ability of participants to identify AI-generated phishing emails.

The study addresses the following research questions:

- **RQ1:** What does existing research indicate about human ability to detect phishing emails and AI-enabled phishing threats?
- **RQ2:** How accurately can participants identify AI-generated phishing emails and distinguish them from legitimate emails?
- **RQ3:** Is self-reported cybersecurity knowledge associated with participants' ability to detect AI-generated phishing emails?

## 2. Related Work

Previous research has examined phishing attacks from both technological and human-centered perspectives. Existing studies show that phishing detection depends not only on the characteristics of an email but also on users' knowledge, attention, and decision-making processes.

Heiding et al. (2024) investigated how large language models can be used to generate phishing emails. Their research compared AI-generated phishing messages with manually designed phishing emails and examined how users responded to them. The findings demonstrated the potential of generative AI to produce effective phishing messages.

Eze and Shamir (2024) examined AI-based phishing email attacks and discussed methods for their detection and prevention. Their research highlights the importance of developing approaches that address phishing messages generated using modern AI technologies.

Human factors have also been widely investigated. Sturman et al. (2024) studied the role of phishing knowledge, cue utilization, and decision-making styles in email detection. Their findings suggest that the ability to recognize relevant indicators in an email is important for distinguishing phishing messages from legitimate communication.

Butavicius et al. (2022) conducted an online experiment involving 472 participants. Their results showed that time pressure reduced phishing detection accuracy. The study also found that commonly assumed indicators, such as poor grammar and lack of personalization, did not necessarily improve participants' ability to distinguish phishing emails.

Canfield et al. (2016) examined phishing susceptibility using signal detection theory. Their research demonstrated that phishing detection and decisions about how to respond to an email are related but distinct tasks.

More recent research by Madleňák and Hubočan (2026) investigated human ability to detect AI-generated content using a survey that included emails, SMS messages, portraits, and fictitious company logos. Their findings indicate that detection performance can differ depending on the type of content being evaluated.

Overall, previous studies demonstrate that phishing detection is influenced by multiple factors, including message characteristics, user knowledge, attention, and decision-making. However, continued research is needed to understand how people recognize AI-generated phishing emails.

## 3. Methodology

### 3.1 Research Design

This study combines a review of existing academic literature with a pilot survey. The literature review examines previous research on human phishing detection and AI-generated phishing threats. The survey provides preliminary empirical observations about participants' ability to identify AI-generated phishing emails.

### 3.2 Survey Design and Participants

An anonymous online questionnaire was used to collect participants' responses.

The questionnaire consisted of 12 email examples:
- Six AI-generated phishing emails.
- Six legitimate emails.

Participants were asked to classify each email as either phishing or legitimate.

The questionnaire also collected information about participants' self-reported cybersecurity knowledge and previous experience with phishing messages.

A total of [N] participants completed the survey.

### 3.3 Data Processing

The survey responses were exported from Google Forms in CSV format. A Python script was developed to convert the responses into JSONL format for further analysis.

Each response record contains:
- Participant identifier.
- Email identifier.
- True email category.
- Participant's predicted category.
- Correctness of the response.
- Self-reported cybersecurity knowledge.
- Previous phishing experience.

Participant identifiers were generated using pseudonymous labels. No personal identifying information is presented in the analysis.

### 3.4 Evaluation Metrics

Two main metrics were used to evaluate detection performance.

**Detection Recall**

Detection recall measures the proportion of AI-generated phishing emails correctly identified as phishing.

\[
Recall_{AI} = \frac{TP}{TP + FN}
\]

Where:
- TP represents AI-generated phishing emails correctly identified as phishing.
- FN represents AI-generated phishing emails incorrectly classified as legitimate.

**False Positive Rate (FPR)**

The false positive rate measures the proportion of legitimate emails incorrectly classified as phishing.

\[
FPR = \frac{FP}{FP + TN}
\]

Where:
- FP represents legitimate emails incorrectly classified as phishing.
- TN represents legitimate emails correctly classified as legitimate.

Metrics were first calculated at the participant level and then averaged across participants.

### 3.5 Statistical Analysis

Participant-level bootstrap confidence intervals were calculated using 5,000 resampling iterations. A fixed random seed was used to support reproducibility.

The analysis included:
1. Mean detection recall for AI-generated phishing emails.
2. Mean false positive rate for legitimate emails.
3. Visualization of participant detection performance according to self-reported cybersecurity knowledge.

The relationship between cybersecurity knowledge and detection performance was explored descriptively.

The survey did not include human-written phishing emails. Therefore, it does not support a direct empirical comparison between AI-generated and human-written phishing emails.

## 4. Results

### 4.1 Participant Overview

A total of [N] participants were included in the analysis. Each participant evaluated six AI-generated phishing emails and six legitimate emails.

### 4.2 AI-Generated Phishing Detection

The average detection recall for AI-generated phishing emails was [X%], with a 95% bootstrap confidence interval of [lower bound, upper bound].

This metric represents the proportion of AI-generated phishing emails that participants correctly identified as phishing.

![Figure 1. Detection Recall for AI-Generated Phishing Emails](../reports/figures/fig1_ai_detection.png)


**Figure 1.** Detection Recall for AI-Generated Phishing Emails.

### 4.3 False Positive Rate

The average false positive rate for legitimate emails was [Y%], with a 95% bootstrap confidence interval of [lower bound, upper bound].

This result represents the proportion of legitimate emails incorrectly identified as phishing.

![Figure 2. False Positive Rate for Legitimate Emails](../reports/figures/fig2_false_positive_rate.png)

**Figure 2.** False Positive Rate for Legitimate Emails.

### 4.4 Cybersecurity Knowledge and Detection Performance

Participant-level detection recall was also examined according to self-reported cybersecurity knowledge.

**Figure 3.** AI Phishing Detection by Self-Reported Cybersecurity Knowledge.

The visualization provides an exploratory view of differences in detection performance across cybersecurity knowledge groups. These differences should be interpreted cautiously and do not establish a causal relationship.

![Figure 3. AI Phishing Detection by Cybersecurity Knowledge](../reports/figures/fig3_cyber_knowledge.png)


## 5. Discussion

The pilot survey provides preliminary evidence about how participants identify AI-generated phishing emails and legitimate messages.

Detection recall indicates how successfully participants recognized AI-generated phishing attempts. The false positive rate provides additional information about whether participants incorrectly classified legitimate emails as suspicious.

Both metrics are important when evaluating human phishing detection. A high detection recall accompanied by a high false positive rate may indicate that participants tend to classify many emails as phishing, including legitimate ones.

The results should also be considered in relation to previous research. Earlier studies have shown that phishing detection depends on users' ability to recognize relevant email cues, their cybersecurity knowledge, and the conditions under which they evaluate messages.

The exploratory visualization of cybersecurity knowledge may help identify potential differences between participants with different self-assessed knowledge levels. However, further research with a larger sample and additional statistical testing is required to establish whether these differences are meaningful.

Importantly, the present survey focuses on AI-generated phishing emails and legitimate emails. It does not establish whether AI-generated phishing emails are more difficult to detect than human-written phishing emails.

## 6. Limitations

Several limitations should be considered when interpreting the findings.

First, the survey included only 12 email examples. A larger and more diverse set of emails would provide a broader evaluation of phishing detection ability.

Second, the survey included six AI-generated phishing emails and six legitimate emails but did not include human-written phishing emails. Consequently, a direct comparison between AI-generated and human-written phishing messages was not possible.

Third, the sample size may limit the generalizability of the findings. The results should therefore be interpreted as preliminary observations rather than representative estimates of the wider population.

Fourth, cybersecurity knowledge was self-reported by participants. Self-assessments may not accurately reflect their actual cybersecurity skills.

Finally, participants classified emails using a binary phishing-or-legitimate response. The study did not measure response time or confidence in individual decisions.

Future research should include a larger sample, a wider variety of email examples, and both AI-generated and human-written phishing messages.

## 7. Conclusion

This study examined human ability to identify AI-generated phishing emails through a review of existing research and an anonymous pilot survey.

The survey included six AI-generated phishing emails and six legitimate emails. Detection recall and false positive rate were used to evaluate participant performance. Self-reported cybersecurity knowledge was also explored as a possible factor associated with detection ability.

The findings provide preliminary insights into how participants distinguish AI-generated phishing messages from legitimate communication. However, the limited number of email examples and the absence of human-written phishing messages restrict the conclusions that can be drawn.

Further studies should use larger participant samples and compare AI-generated phishing emails directly with human-written phishing emails. Such research could contribute to a better understanding of human vulnerability to emerging AI-enabled cyber threats.

## 8. References

1. Heiding, F., Schneier, B., Vishwanath, A., Bernstein, J., & Park, P. S. (2024). Devising and Detecting Phishing Emails Using Large Language Models. *IEEE Access*. https://doi.org/10.1109/ACCESS.2024.3375882

2. Eze, C. S., & Shamir, L. (2024). Analysis and Prevention of AI-Based Phishing Email Attacks. *Electronics, 13*(10), 1839. https://doi.org/10.3390/electronics13101839

3. Sturman, D., Bell, E. A., Auton, J. C., Breakey, G. R., & Wiggins, M. W. (2024). The roles of phishing knowledge, cue utilization, and decision styles in phishing email detection. *Applied Ergonomics, 119*, 104309. https://doi.org/10.1016/j.apergo.2024.104309

4. Butavicius, M., Taib, R., & Han, S. J. (2022). Why people keep falling for phishing scams: The effects of time pressure and deception cues on the detection of phishing emails. *Computers & Security, 123*, 102937. https://doi.org/10.1016/j.cose.2022.102937

5. Canfield, C. I., Fischhoff, B., & Davis, A. (2016). Quantifying Phishing Susceptibility for Detection and Behavior Decisions. *Human Factors, 58*(8), 1158–1172. https://doi.org/10.1177/0018720816665025

6. Madleňák, M., & Hubočan, S. (2026). Phishing 2.0: Human Ability to Detect AI-Generated Content. *Transportation Research Procedia, 93*, 1125–1132. https://doi.org/10.1016/j.trpro.2025.12.051
