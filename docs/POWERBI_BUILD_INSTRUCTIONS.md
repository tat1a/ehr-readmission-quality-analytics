# Power BI Build Instructions

## Objective

Create a three-page interactive Power BI report:

1. Readmission Overview
2. Care Quality and Data Quality
3. Cohort Profile

Use the processed CSV files from `data/processed/`.

## Import Data

1. Open Power BI Desktop.
2. Select **Get data**.
3. Choose **Text/CSV**.
4. Import these files:
   - `data/processed/readmission_features.csv`
   - `data/processed/dashboard_kpis.csv`
   - `data/processed/readmission_summary_by_service.csv`
   - `data/processed/risk_tier_summary.csv`
   - `data/processed/quality_measure_summary.csv`
   - `data/processed/data_quality_summary.csv`
   - `data/processed/operational_flag_summary.csv`
   - `data/processed/cohort_summary_by_age.csv`
   - `data/processed/cohort_summary_by_insurance.csv`
   - `data/processed/feature_importance_proxy.csv`
5. Select **Transform data** if Power BI asks to confirm types.
6. Confirm numeric fields are set correctly:
   - Counts: whole number.
   - Rates: decimal number, formatted as percentage in report visuals.
   - Length of stay: decimal number.
7. Apply changes.

## Apply Theme

1. Go to **View**.
2. Select **Browse for themes**.
3. Choose `powerbi/theme-ehr-readmission.json`.

## Add Measures

Use the DAX formulas in `powerbi/measures.dax`.

Important: the main readmission and cohort measures are calculated from `readmission_features`, not from `dashboard_kpis`. This keeps cards and charts responsive to slicers.

Recommended formatting:

- `Readmission Rate`: Percentage, 1 decimal place.
- `Diabetes A1c Completion`: Percentage, 1 decimal place.
- `Hypertension BP Completion`: Percentage, 1 decimal place.
- `Average Length of Stay`: Decimal number, 1 decimal place.
- Count measures: Whole number with thousands separator.
- Display units for count cards: **None**.

For exact field placement, expected values, aggregation settings, titles, and subtitles, use `docs/POWERBI_MANUAL_VISUAL_SPEC.md`.

## Page 1: Readmission Overview

Canvas:

- 16:9 widescreen.
- Background: `#F8FAFC`.
- Left navigation rail: dark slate `#0F172A`.
- Main text: near-black `#111827`.
- Accent colors: blue `#2563EB`, teal `#14B8A6`, green `#0F766E`, amber `#F97316`, purple `#7C3AED`.

Top KPI cards:

- Index Admissions
- Readmissions 30D
- Readmission Rate
- Average Length of Stay

Main visuals:

- Clustered bar chart: `readmission_features[service_line]` by `[Readmission Rate]`.
- Column chart: `readmission_features[risk_tier]` by `[Readmission Rate]`.
- Table or matrix: service line, index admissions, readmissions, readmission rate, average length of stay.

Slicers:

- Service line.
- Risk tier.
- Age group.
- Insurance type.

## Page 2: Care Quality and Data Quality

Top KPI cards:

- Diabetes A1c Completion
- Hypertension BP Completion
- Quality Gap Count
- Data Quality Issue Count

Main visuals:

- Bar chart: quality measure by completion rate.
- Bar chart: data-quality check by issue count.
- Bar chart or table: operational review flags by encounter count.
- Table: measure, denominator, numerator, gap count, completion rate.

Slicers:

- Risk tier.
- Service line.
- Chronic-condition flags if added as slicer fields.

## Page 3: Cohort Profile

Main visuals:

- Column chart: `readmission_features[age_group]` by `[Index Admissions]`.
- Bar chart: `readmission_features[insurance_type]` by `[Index Admissions]`.
- Column chart: `readmission_features[risk_tier]` by `[Average Medication Count]`.
- Table: encounter-level sample with encounter ID, age group, service line, primary diagnosis, risk tier, length of stay, readmission flag.

Slicers:

- Readmission flag.
- Service line.
- Risk tier.
- Insurance type.

## Layout Rules

- Avoid oversized card labels; values should be prominent, labels should fit.
- Keep all table headers visible.
- Use short visual titles.
- Do not use decorative gradients.
- Use consistent colors:
  - Navy for headers.
  - Blue/teal for readmission and service-line visuals.
  - Green for completion.
  - Amber for risk or gaps.
- Check every page at 100% zoom before saving.

## Exported File

Save as:

`powerbi/EHR_Readmission_Quality_Analytics.pbix`

If using Power BI Project format, save as:

`powerbi/EHR_Readmission_Quality_Analytics.pbip`
