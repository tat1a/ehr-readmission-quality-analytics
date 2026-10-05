# Power BI Clean Build Guide

Use this guide with the clean Power BI project:

`powerbi/EHR_Readmission_Quality_Analytics.pbip`

This version is designed as a stable Power BI semantic model: clean tables, grouped measures, and blank pages. Build the visuals manually in Power BI Desktop using the mockups in `assets/`.

## 1. Open and Prepare

1. Open `powerbi/EHR_Readmission_Quality_Analytics.pbip`.
2. In Power BI Desktop, go to **View > Themes > Browse for themes**.
3. Select `powerbi/theme-ehr-readmission.json`.
4. Confirm the report has these pages:
   - `Readmission Overview`
   - `Care Quality and Data Quality`
   - `Cohort Profile`
5. In the Data pane, use the measures under `dashboard_kpis`. Do not use the numeric columns inside `dashboard_kpis` for visuals.

## 2. Measure Groups

All DAX measures are stored under the `dashboard_kpis` table and grouped into these folders.

| Folder | Measure | Use |
| --- | --- | --- |
| `01 Readmission KPIs` | `Index Admissions` | Admission count cards and chart values |
| `01 Readmission KPIs` | `Readmissions 30D` | Readmission count cards and tooltips |
| `01 Readmission KPIs` | `Readmission Rate` | Rate cards and rate charts |
| `01 Readmission KPIs` | `Average Length of Stay` | LOS card and tooltips |
| `01 Readmission KPIs` | `High Risk Encounters` | High-risk cohort count |
| `01 Readmission KPIs` | `High Risk Readmission Rate` | High-risk rate reference |
| `02 Care Quality` | `Diabetes A1c Completion` | A1c KPI card |
| `02 Care Quality` | `Hypertension BP Completion` | BP KPI card |
| `02 Care Quality` | `Quality Gap Count` | Documentation gap KPI |
| `02 Care Quality` | `Data Quality Issue Count` | Missing documentation KPI |
| `03 Cohort Profile` | `Average Prior Encounters` | Utilization tooltip/reference |
| `03 Cohort Profile` | `Average Medication Count` | Medication burden chart |
| `04 Operational Flags` | `Operational Flag Count` | Operational flag total |

## 3. Global Formatting

Use a different look from the prior portfolio dashboard: light clinical workspace, deep left navigation, blue/teal data colors, and compact professional typography.

| Element | Setting |
| --- | --- |
| Canvas background | `#F8FAFC` |
| Left navigation band | `#0F172A` |
| Main text | `#111827` |
| Secondary text | `#64748B` |
| Main chart blue | `#2563EB` |
| Teal accent | `#14B8A6` |
| Green accent | `#0F766E` |
| Amber accent | `#F97316` |
| Purple accent | `#7C3AED` |
| Font | Segoe UI or Aptos |
| Card value size | 28-36 pt |
| Card label size | 11-13 pt |
| Chart title size | 12-14 pt |
| Count display units | None |
| Percent format | Percentage, 1 decimal |
| Decimal metrics | 1 decimal |

## 3A. Common Fixes If Your Visual Looks Wrong

Use this section to repair the exact issues that usually appear when building the report manually.

| Problem you see | What caused it | Exact fix |
| --- | --- | --- |
| Chart title says `Count of issue_count and Count of issue_count` | Power BI automatically set the field aggregation to Count | In the visual's field bucket, open the dropdown beside `issue_count` and choose **Sum**. Rename the visual title manually to `Data-quality checks`. |
| Chart title says `Count of encounter_count and Count of encounter_count` | `encounter_count` is being counted instead of summed | In the visual's field bucket, open the dropdown beside `encounter_count` and choose **Sum**. Rename the visual title to `Operational review flags`. |
| Completion bars show `1` instead of `78.7%` and `82.3%` | `completion_rate` is being counted | Open the dropdown beside `completion_rate` and choose **Average** or **Maximum**. Format the value as Percentage with 1 decimal. |
| Cohort charts have long titles like `Index Admissions, Readmissions 30D...` | Too many measures were added to the same visual | Keep only the one required measure in Values/Y-axis. Move extra measures to Tooltips only. |
| Filters appear as a long checkbox tree | The slicer style is List or a hierarchy was used | Use separate slicers. For each slicer: Format visual > Slicer settings > Style = **Dropdown**. Do not combine fields into one hierarchy slicer. |
| Service-line labels look different from the mockup | Axis/category labels or data labels are using default settings | Y-axis values on, Y-axis title off, X-axis title off, X-axis labels off or very light, Data labels on, position Outside end, 1 decimal percentage. |
| Numbers show `1K` instead of `1,102` | Display units are set to Auto | Format visual > Callout value or Data labels > Display units = **None**. |

## 4. Page 1: Readmission Overview

Mockup: `assets/powerbi-page-1-readmission-overview.png`

Title: `EHR Readmission Analytics`

Subtitle: `Clinical operations view: readmission monitoring, service variation, and risk tier stratification`

Footer: `Data basis: encounter-level readmission_features fact table; slicers filter KPI cards and rate charts.`

### KPI Cards

Create four **Card** visuals across the top.

| Card title | Field bucket | Field |
| --- | --- | --- |
| Index Admissions | Callout value / Fields | `dashboard_kpis` > `01 Readmission KPIs` > `Index Admissions` |
| Readmissions 30D | Callout value / Fields | `dashboard_kpis` > `01 Readmission KPIs` > `Readmissions 30D` |
| Readmission Rate | Callout value / Fields | `dashboard_kpis` > `01 Readmission KPIs` > `Readmission Rate` |
| Average Length of Stay | Callout value / Fields | `dashboard_kpis` > `01 Readmission KPIs` > `Average Length of Stay` |

Expected values with no slicers:

| Metric | Value |
| --- | ---: |
| Index Admissions | 1,102 |
| Readmissions 30D | 80 |
| Readmission Rate | 7.3% |
| Average Length of Stay | 3.1 |

### Chart 1: Readmission Rate by Service Line

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `readmission_features[service_line]` |
| X-axis / Values | `dashboard_kpis` > `01 Readmission KPIs` > `Readmission Rate` |
| Tooltips | `Index Admissions`, `Readmissions 30D`, `Average Length of Stay` |

Formatting:

- Sort by `Readmission Rate`, descending.
- X-axis format: percentage, 1 decimal.
- Data labels: on.
- Display units: None.
- Y-axis values: on.
- Y-axis title: off.
- X-axis title: off.
- X-axis labels: off or light gray if you prefer to keep the scale.
- Data label position: Outside end.
- Visual title text: `Readmission rate by service line`.
- Category label font size: 9-10 pt.
- Data label font size: 8-9 pt.

Expected values:

| Service line | Index admissions | Readmissions 30D | Readmission rate |
| --- | ---: | ---: | ---: |
| General Medicine | 407 | 32 | 7.9% |
| Cardiology | 206 | 16 | 7.8% |
| General Surgery | 174 | 12 | 6.9% |
| Pulmonary | 178 | 12 | 6.7% |
| Endocrinology | 137 | 8 | 5.8% |

### Chart 2: Risk Tier Signal

Visual type: **Clustered column chart**

| Power BI bucket | Field |
| --- | --- |
| X-axis | `readmission_features[risk_tier]` |
| Y-axis / Values | `dashboard_kpis` > `01 Readmission KPIs` > `Readmission Rate` |
| Tooltips | `Index Admissions`, `Readmissions 30D`, `Average Medication Count` |

Formatting:

- X-axis order: Low, Moderate, High.
- Y-axis format: percentage, 1 decimal.
- Data labels: on.

Expected values:

| Risk tier | Index admissions | Readmissions 30D | Readmission rate |
| --- | ---: | ---: | ---: |
| Low | 295 | 17 | 5.8% |
| Moderate | 677 | 45 | 6.6% |
| High | 130 | 18 | 13.8% |

### Page 1 Slicers

Create separate slicers, not a hierarchy slicer. The cleanest version is **Dropdown** because it keeps the right filter panel compact. If you prefer visible checkboxes, use List style, but keep the five slicers separate.

| Slicer title | Field |
| --- | --- |
| Service line | `readmission_features[service_line]` |
| Risk tier | `readmission_features[risk_tier]` |
| Age group | `readmission_features[age_group]` |
| Insurance type | `readmission_features[insurance_type]` |
| Diagnosis | `readmission_features[primary_diagnosis]` |

Dropdown slicer settings:

- Format visual > Slicer settings > Style: Dropdown.
- Selection controls > Multi-select with CTRL: Off.
- Header: On.
- Title: On.
- Visual title text should be the simple label above, not the table/field name.

## 5. Page 2: Care Quality and EHR Data Quality

Mockup: `assets/powerbi-page-2-quality-data.png`

Title: `Care Quality and EHR Data Quality`

Subtitle: `Documentation completion, gap counts, and operational data-quality checks`

Footer: `Data basis: quality_measure_summary and data_quality_summary; documentation gaps are kept separate from operational flags.`

### KPI Cards

Create four **Card** visuals across the top.

| Card title | Field bucket | Field |
| --- | --- | --- |
| Diabetes A1c Completion | Callout value / Fields | `dashboard_kpis` > `02 Care Quality` > `Diabetes A1c Completion` |
| Hypertension BP Completion | Callout value / Fields | `dashboard_kpis` > `02 Care Quality` > `Hypertension BP Completion` |
| Quality Gap Count | Callout value / Fields | `dashboard_kpis` > `02 Care Quality` > `Quality Gap Count` |
| Data Quality Issue Count | Callout value / Fields | `dashboard_kpis` > `02 Care Quality` > `Data Quality Issue Count` |

Expected values:

| Metric | Value |
| --- | ---: |
| Diabetes A1c Completion | 78.7% |
| Hypertension BP Completion | 82.3% |
| Quality Gap Count | 97 |
| Data Quality Issue Count | 97 |

### Chart 1: Documentation Completion

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `quality_measure_summary[measure]` |
| X-axis / Values | `quality_measure_summary[completion_rate]` |
| Tooltips | `quality_measure_summary[denominator]`, `quality_measure_summary[numerator]`, `quality_measure_summary[gap_count]` |

Important:

- Aggregation for `completion_rate`: Average or Max.
- Do not use Count of `completion_rate`.
- X-axis format: percentage, 1 decimal.
- Visual title text: `Documentation completion`.
- Rename the field display if Power BI shows `Average of completion_rate`; the chart title should not use field names.

Expected values:

| Measure | Denominator | Numerator | Gap count | Completion rate |
| --- | ---: | ---: | ---: | ---: |
| A1c documented for diabetes encounters | 169 | 133 | 36 | 78.7% |
| Blood pressure documented for hypertension encounters | 345 | 284 | 61 | 82.3% |

### Chart 2: Data-Quality Checks

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `data_quality_summary[check_name]` |
| X-axis / Values | `data_quality_summary[issue_count]` |
| Tooltips | `data_quality_summary[issue_count]` |

Formatting:

- Aggregation: Sum.
- Display units: None.
- Data labels: on.
- Visual title text: `Data-quality checks`.
- If the title says `Count of issue_count`, the visual is wrong. Change aggregation to Sum.

Expected values:

| Check | Issue count |
| --- | ---: |
| Missing BP among hypertension encounters | 61 |
| Missing A1c among diabetes encounters | 36 |

### Chart 3: Operational Review Flags

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `operational_flag_summary[flag_name]` |
| X-axis / Values | `operational_flag_summary[encounter_count]` |
| Tooltips | `operational_flag_summary[encounter_count]` |

Formatting:

- Aggregation: Sum.
- Display units: None.
- Keep this separate from `data_quality_summary`.
- Visual title text: `Operational review flags`.
- If the title says `Count of encounter_count`, the visual is wrong. Change aggregation to Sum.

Expected values:

| Operational flag | Encounter count |
| --- | ---: |
| Prior utilization >= 2 encounters | 901 |
| Long stay encounters | 144 |
| High risk tier encounters | 130 |
| High medication count encounters | 38 |

### Table: Quality Measure Summary

Visual type: **Table**

Add fields in this order:

1. `quality_measure_summary[measure]`
2. `quality_measure_summary[denominator]`
3. `quality_measure_summary[numerator]`
4. `quality_measure_summary[gap_count]`
5. `quality_measure_summary[completion_rate]`

## 6. Page 3: Cohort Profile

Mockup: `assets/powerbi-page-3-cohort-profile.png`

Title: `Cohort Profile`

Subtitle: `Encounter-level profile: demographics, utilization intensity, medication burden, and readmission flags`

Footer: `Data basis: readmission_features analytic cohort; feature proxy panel uses feature_importance_proxy.`

### Chart 1: Index Admissions by Age Group

Visual type: **Clustered column chart**

| Power BI bucket | Field |
| --- | --- |
| X-axis | `readmission_features[age_group]` |
| Y-axis / Values | `dashboard_kpis` > `01 Readmission KPIs` > `Index Admissions` |
| Tooltips | `Readmissions 30D`, `Readmission Rate`, `Average Length of Stay` |

Important:

- Values/Y-axis must contain only `Index Admissions`.
- Put `Readmissions 30D`, `Readmission Rate`, and `Average Length of Stay` in Tooltips only.
- Visual title text: `Index admissions by age group`.

Expected values:

| Age group | Index admissions |
| --- | ---: |
| 18-39 | 247 |
| 40-64 | 503 |
| 65-79 | 221 |
| 80+ | 131 |

### Chart 2: Index Admissions by Insurance

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `readmission_features[insurance_type]` |
| X-axis / Values | `dashboard_kpis` > `01 Readmission KPIs` > `Index Admissions` |
| Tooltips | `Readmissions 30D`, `Readmission Rate` |

Important:

- Values/X-axis must contain only `Index Admissions`.
- Put `Readmissions 30D` and `Readmission Rate` in Tooltips only.
- Visual title text: `Index admissions by insurance`.

Expected values:

| Insurance type | Index admissions |
| --- | ---: |
| Medicare | 471 |
| Commercial | 342 |
| Medicaid | 227 |
| Self-pay | 62 |

### Chart 3: Higher-Risk Feature Groups

Visual type: **Clustered bar chart**

| Power BI bucket | Field |
| --- | --- |
| Y-axis | `feature_importance_proxy[feature]` |
| X-axis / Values | `feature_importance_proxy[readmission_rate]` |
| Tooltips | `feature_importance_proxy[readmission_rate]` |

Important:

- Aggregation for `readmission_rate`: Average or Max.
- X-axis format: percentage, 1 decimal.
- This is an explanatory static comparison, not a predictive model.
- Visual title text: `Higher-risk feature groups`.
- Do not add `readmission_rate` twice.

Expected values:

| Feature group | Readmission rate |
| --- | ---: |
| Heart failure diagnosis | 15.0% |
| High risk tier | 13.8% |
| Medication count >= 6 | 7.9% |
| Prior utilization >= 2 encounters | 7.4% |
| Chronic kidney disease | 7.2% |

Optional interview talking point: the `Average Medication Count` measure remains available under `dashboard_kpis` > `03 Cohort Profile`. Use it in tooltips or add a small optional chart only if you have extra space; it is not part of the main mockup layout.

### Table: Encounter-Level Sample

Visual type: **Table**

Add fields in this order:

1. `readmission_features[encounter_id]`
2. `readmission_features[age_group]`
3. `readmission_features[service_line]`
4. `readmission_features[primary_diagnosis]`
5. `readmission_features[risk_tier]`
6. `readmission_features[length_of_stay_days]`
7. `readmission_features[readmitted_30d]`

## 7. Final QA Checklist

Before saving, confirm:

- The file name is `powerbi/EHR_Readmission_Quality_Analytics.pbip`.
- Cards show `1,102`, `80`, `7.3%`, and `3.1` on Page 1 before slicers.
- `Readmission Rate by Service Line` uses `readmission_features[service_line]` plus the DAX measure `Readmission Rate`.
- Page 2 data-quality chart has only two rows: missing BP and missing A1c.
- Operational flags are on a separate visual.
- No visual uses `Count of readmission_rate`, `Count of completion_rate`, or `Count of issue_count`.
- Count display units are set to None, not Auto.
- Visual titles are clean and do not expose table names.
- Footer notes say the data is synthetic and describe the data basis.

