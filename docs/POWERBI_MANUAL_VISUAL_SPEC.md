# Power BI Manual Visual Specification

Use this file when building the report manually in Power BI Desktop. The safest approach is to create the measures in `powerbi/measures.dax`, then build visuals from `readmission_features` for interactive readmission/cohort pages.

## Visual Data Basis

| Report area | Primary data basis | Why |
| --- | --- | --- |
| Readmission KPI cards | Measures calculated from `readmission_features` | Cards respond correctly to slicers. |
| Readmission service/risk charts | `readmission_features` dimensions + DAX measures | Prevents repeated identical rates across categories. |
| Page 1 slicers | `readmission_features` | Filters the encounter-level fact table directly. |
| Care-quality KPI cards | `quality_measure_summary` | Uses numerator/denominator documentation logic. |
| Data-quality chart | `data_quality_summary` | Shows only missing documentation checks. |
| Operational flags | `operational_flag_summary` | Keeps utilization/risk review separate from data quality. |
| Cohort profile charts | `readmission_features` + DAX measures | Keeps charts interactive and consistent with slicers. |
| Feature proxy chart | `feature_importance_proxy` | Static explanatory comparison for higher-risk groups. |

## Required Formatting

Set these formatting options before final review:

- Count cards: Display units = None, decimal places = 0, thousands separator = On.
- Rate cards and rate axes: Percentage, 1 decimal place.
- Length of stay and medication count: Decimal number, 1 decimal place.
- Do not use `dashboard_kpis` for slicer-responsive charts. It is a static audit table.
- Do not use Count of rate/count columns. If using summary tables, rates should be Average or Max; counts should be Sum.

## Page 1: Readmission Overview

Title: `EHR Readmission Analytics`

Subtitle: `Clinical operations view: readmission monitoring, service variation, and risk tier stratification`

Footer: `All records are synthetic. Use slicers to review readmission patterns by service line, risk tier, age, and payer.`

### KPI Cards

| Visual | Visual type | Field | Data basis |
| --- | --- | --- | --- |
| Index Admissions | Card | `[Index Admissions]` | `readmission_features` |
| Readmissions 30D | Card | `[Readmissions 30D]` | `readmission_features` |
| Readmission Rate | Card | `[Readmission Rate]` | `readmission_features` |
| Average Length of Stay | Card | `[Average Length of Stay]` | `readmission_features` |

### Readmission Rate by Service Line

Visual type: Clustered bar chart

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `readmission_features[service_line]` |
| X-axis | `[Readmission Rate]` |
| Tooltips | `[Index Admissions]`, `[Readmissions 30D]`, `[Average Length of Stay]` |

Data basis: encounter-level rows in `readmission_features`, grouped by `service_line`.

Expected values:

| Service line | Index admissions | Readmissions 30D | Readmission rate |
| --- | ---: | ---: | ---: |
| General Medicine | 407 | 32 | 7.9% |
| Cardiology | 206 | 16 | 7.8% |
| General Surgery | 174 | 12 | 6.9% |
| Pulmonary | 178 | 12 | 6.7% |
| Endocrinology | 137 | 8 | 5.8% |

### Readmission Rate by Risk Tier

Visual type: Clustered column chart

| Power BI bucket | Field |
| --- | --- |
| X-axis | `readmission_features[risk_tier]` |
| Y-axis | `[Readmission Rate]` |
| Tooltips | `[Index Admissions]`, `[Readmissions 30D]`, `[Average Medication Count]` |

Data basis: encounter-level rows in `readmission_features`, grouped by derived `risk_tier`.

Expected values:

| Risk tier | Index admissions | Readmissions 30D | Readmission rate |
| --- | ---: | ---: | ---: |
| High | 130 | 18 | 13.8% |
| Moderate | 677 | 45 | 6.6% |
| Low | 295 | 17 | 5.8% |

### Slicers

Create separate slicers, not a hierarchy:

- `readmission_features[service_line]`
- `readmission_features[risk_tier]`
- `readmission_features[age_group]`
- `readmission_features[insurance_type]`
- Optional: `readmission_features[primary_diagnosis]`

## Page 2: Care Quality and EHR Data Quality

Title: `Care Quality and EHR Data Quality`

Subtitle: `Documentation completion, gap counts, and operational data-quality checks`

Footer: `Use this page to discuss documentation gaps separately from clinical outcomes.`

### KPI Cards

| Visual | Visual type | Field | Data basis |
| --- | --- | --- | --- |
| Diabetes A1c Completion | Card | `[Diabetes A1c Completion]` | `quality_measure_summary` |
| Hypertension BP Completion | Card | `[Hypertension BP Completion]` | `quality_measure_summary` |
| Quality Gap Count | Card | `[Quality Gap Count]` | `quality_measure_summary` |
| Data Quality Issue Count | Card | `[Data Quality Issue Count]` | `data_quality_summary` |

Expected KPI values:

| Metric | Value |
| --- | ---: |
| Diabetes A1c Completion | 78.7% |
| Hypertension BP Completion | 82.3% |
| Quality Gap Count | 97 |
| Data Quality Issue Count | 97 |

### Documentation Completion

Visual type: Clustered bar chart

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `quality_measure_summary[measure]` |
| X-axis | `quality_measure_summary[completion_rate]` |

Data basis: `quality_measure_summary`, generated from condition flags and documentation flags in `readmission_features`.

Aggregation: Average or Max. Do not use Count.

Expected values:

| Measure | Completion rate | Gap count |
| --- | ---: | ---: |
| A1c documented for diabetes encounters | 78.7% | 36 |
| Blood pressure documented for hypertension encounters | 82.3% | 61 |

### Data-Quality Checks

Visual type: Clustered bar chart

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `data_quality_summary[check_name]` |
| X-axis | `data_quality_summary[issue_count]` |

Data basis: `data_quality_summary`, limited to missing A1c/BP documentation checks.

Aggregation: Sum. Display units = None.

Expected values:

| Check | Issue count |
| --- | ---: |
| Missing BP among hypertension encounters | 61 |
| Missing A1c among diabetes encounters | 36 |

### Operational Review Flags

Visual type: Clustered bar chart or table

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `operational_flag_summary[flag_name]` |
| X-axis | `operational_flag_summary[encounter_count]` |

Data basis: operational review flags derived from `readmission_features`.

Use this visual separately from data-quality checks.

## Page 3: Cohort Profile

Title: `Cohort Profile`

Subtitle: `Encounter-level profile: demographics, utilization intensity, medication burden, and readmission flags`

Footer: `Use this page for interview discussion: cohort construction, stratification logic, and row-level auditability.`

### Index Admissions by Age Group

Visual type: Clustered column chart

| Power BI bucket | Field |
| --- | --- |
| X-axis | `readmission_features[age_group]` |
| Y-axis | `[Index Admissions]` |

Data basis: encounter-level rows in `readmission_features`, grouped by `age_group`.

### Index Admissions by Insurance

Visual type: Clustered bar chart

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `readmission_features[insurance_type]` |
| X-axis | `[Index Admissions]` |

Data basis: encounter-level rows in `readmission_features`, grouped by `insurance_type`.

### Average Medication Count by Risk Tier

Visual type: Clustered column chart

| Power BI bucket | Field |
| --- | --- |
| X-axis | `readmission_features[risk_tier]` |
| Y-axis | `[Average Medication Count]` |

Data basis: encounter-level medication burden in `readmission_features`, grouped by `risk_tier`.

Expected values:

| Risk tier | Average medication count |
| --- | ---: |
| High | 3.6 |
| Moderate | 2.5 |
| Low | 2.2 |

### Encounter-Level Table

Visual type: Table

Add these fields:

- `readmission_features[encounter_id]`
- `readmission_features[age_group]`
- `readmission_features[service_line]`
- `readmission_features[primary_diagnosis]`
- `readmission_features[risk_tier]`
- `readmission_features[length_of_stay_days]`
- `readmission_features[readmitted_30d]`

Data basis: row-level `readmission_features` analytic cohort table.

