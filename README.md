# Human Ability to Detect AI-Generated Phishing Emails

## Project Overview

This project investigates human responses to phishing and legitimate email examples in the context of generative artificial intelligence.

The research combines a review of existing cybersecurity literature with a descriptive analysis of a student survey.

## Research Objectives

- Review existing research on human phishing detection.
- Examine how participants classify phishing and legitimate email examples.
- Analyze response patterns across 12 email examples.
- Explore the relevance of cybersecurity awareness in identifying suspicious messages.
- Discuss challenges associated with AI-generated phishing communication.

## Dataset

The available survey export contains:

- 27 participant records.
- 12 email-classification questions.
- 324 recorded classifications.

Overall response distribution:

| Category | Responses | Percentage |
|---|---:|---:|
| Phishing | 181 | 55.9% |
| Legitimate | 143 | 44.1% |

These figures describe participant choices and are not verified detection accuracy.

## Technologies

- Python
- Pandas
- Matplotlib
- Jupyter Notebook
- Git and GitHub

## Repository Structure

```text
ai-phishing-literature-review/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── domain_model.md
│   └── methodology.md
│
├── notebooks/
│   └── 01_data_analysis.ipynb
│
├── reports/
│   └── figures/
│
├── src/
│   ├── inspect_survey.py
│   ├── process_survey.py
│   └── visualize_survey.py
│
├── README.md
└── requirements.txt
```

## Methodology

The survey asked participants to classify email examples as either phishing or legitimate.

Python and Pandas were used to inspect and summarize the collected responses. Visualizations were prepared to present response distributions.

Performance metrics such as accuracy, precision, recall, and F1-score require verified ground-truth labels and are not reported from response frequencies alone.

## Research Limitations

The survey is based on a limited student sample. The available response export does not contain a verified answer key or complete source-provenance mapping for the email stimuli.

The findings should therefore be interpreted as descriptive participant response patterns.

## Authors

**Zhadyra Kurmanova**

**Meirim Yersultan**

## Repository

https://github.com/zhadritto/ai-phishing-literature-review
