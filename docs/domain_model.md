
# Domain Model

## 1. System Overview

The project studies how accurately people can identify phishing emails, including AI-generated and human-written phishing messages.

The system consists of several stages:

1. Participants evaluate 12 email examples through an online questionnaire.
2. Responses are collected using Google Forms.
3. The collected responses are exported for data processing.
4. Raw data is cleaned, anonymized, and transformed into a structured dataset.
5. Python scripts and Jupyter Notebook are used for statistical analysis.
6. The results are presented through scientific visualizations and research reports.

The main purpose of the system is to support the analysis of human phishing detection performance while protecting participants' data and ensuring the integrity of research results.


## 2. System Actors

| Actor | Description |
|---|---|
| Participant | Evaluates email examples and submits classification responses. |
| Researchers | Manage the study, process collected data, perform statistical analysis, and interpret results. |
| Google Forms | External service used to collect questionnaire responses. |

## 3. System Components

| Component | Description |
|---|---|
| Google Forms | Collects participant responses. |
| Raw CSV Dataset | Stores exported questionnaire responses. |
| Data Processing Script | Cleans, anonymizes, and transforms the collected data. |
| Processed Dataset | Contains structured data prepared for analysis. |
| Jupyter Notebook | Performs exploratory and statistical analysis. |
| Visualization Script | Generates scientific charts and figures. |
| GitHub Repository | Stores source code, documentation, and approved research outputs. |
