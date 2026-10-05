# Analyst Brief

## Project

EHR Readmission and Care Quality Analytics

## Business Question

Which adult inpatient encounters have higher 30-day readmission risk, and where do documentation gaps affect care-quality monitoring?

## Data Scope

The project uses a deterministic synthetic EHR-style dataset with linked patient, encounter, diagnosis, observation, and medication tables. It contains no real patient data, no PHI, no MIMIC-IV data, and no restricted source data.

## Cohort

The analytic cohort includes adult inpatient index encounters. Planned admissions, invalid encounter intervals, expired discharges, and acute-care transfers are excluded from the readmission denominator.

## Key Findings

| Metric | Result |
| --- | ---: |
| Patients | 900 |
| Total encounters | 5,020 |
| Eligible index admissions | 1,102 |
| 30-day readmissions | 80 |
| Overall readmission rate | 7.3% |
| Average length of stay | 3.1 days |
| High-risk encounters | 130 |

### Readmission Risk

High-risk encounters had the highest readmission rate at 13.8%, compared with 6.6% for moderate-risk encounters and 5.8% for low-risk encounters. This pattern supports the derived risk-tier logic and gives the dashboard a clinically interpretable stratification layer.

### Service-Line Variation

General Medicine had the largest index-admission volume and the highest readmission count. Cardiology had a similar readmission rate, while General Surgery, Pulmonary, and Endocrinology showed lower rates in this synthetic cohort.

| Service line | Index admissions | Readmissions | Readmission rate |
| --- | ---: | ---: | ---: |
| General Medicine | 407 | 32 | 7.9% |
| Cardiology | 206 | 16 | 7.8% |
| General Surgery | 174 | 12 | 6.9% |
| Pulmonary | 178 | 12 | 6.7% |
| Endocrinology | 137 | 8 | 5.8% |

### Care-Quality Monitoring

Documentation completion was 78.7% for A1c among diabetes encounters and 82.3% for blood-pressure documentation among hypertension encounters. These measures are examples of operational monitoring logic rather than formal quality-program specifications.

| Measure | Denominator | Complete | Gap count | Completion rate |
| --- | ---: | ---: | ---: | ---: |
| A1c documented for diabetes encounters | 169 | 133 | 36 | 78.7% |
| Blood pressure documented for hypertension encounters | 345 | 284 | 61 | 82.3% |

## Methods Summary

The pipeline creates synthetic EHR-style raw tables, applies SQL-style cohort rules, engineers encounter-level features in Python/pandas, derives a 30-day readmission outcome, creates care-quality flags, and exports Power BI-ready reporting tables.

## Portfolio Value

This project demonstrates practical clinical analytics skills: EHR table relationships, cohort construction, readmission outcome logic, data-quality checks, pandas transformations, SQL documentation, dashboard modeling, DAX measures, and responsible interpretation of synthetic healthcare data.

## Limitations

The results are not clinical evidence and should not be interpreted as real-world readmission performance. The risk tiers are designed for demonstration, not for patient-care decision support or validated prediction.
