# Interactive Power BI Specification

## Goal

Build an interactive dashboard for inpatient readmission monitoring, care-quality documentation, and EHR data-quality review.

## Data Sources

Use the processed CSV files in `data/processed/`:

- `dashboard_kpis.csv`
- `readmission_features.csv`
- `readmission_summary_by_service.csv`
- `risk_tier_summary.csv`
- `quality_measure_summary.csv`
- `data_quality_summary.csv`
- `operational_flag_summary.csv`
- `cohort_summary_by_age.csv`
- `cohort_summary_by_insurance.csv`
- `feature_importance_proxy.csv`

## Page 1: Readmission Overview

Recommended visuals:

- KPI cards: index admissions, 30-day readmissions, readmission rate, average length of stay.
- Clustered bar chart: readmission rate by service line.
- Column chart: readmission rate by risk tier.
- Matrix: service line by risk tier with index admissions, readmissions, and rate.

Recommended slicers:

- Service line.
- Risk tier.
- Age group.
- Insurance type.
- Primary diagnosis.

Interactions:

- Selecting a service line should filter all KPI cards, risk-tier charts, and the matrix.
- Selecting a risk tier should filter the service-line chart and cohort profile.
- Use tooltip values for denominator, numerator, readmission rate, and average length of stay.

## Page 2: Care Quality and Data Quality

Recommended visuals:

- KPI cards: A1c completion, blood-pressure completion, quality gap count, data-quality issue count.
- Bar chart: quality measure completion rate.
- Bar chart: data-quality issue count by check.
- Bar chart or table: operational review flags.
- Table: quality measure, denominator, numerator, gap count, completion rate.

Recommended slicers:

- Service line.
- Age group.
- Chronic-condition flags.
- Risk tier.

Interactions:

- Use the chronic-condition slicers to focus diabetes and hypertension documentation review.
- Keep quality measure tables visible without horizontal scrolling.

## Page 3: Cohort Profile

Recommended visuals:

- Column chart: index admissions by age group.
- Bar chart: index admissions by insurance type.
- Column chart: average medication count by risk tier.
- Table: encounter-level cohort sample with encounter ID, age group, service line, primary diagnosis, risk tier, length of stay, and readmission flag.

Recommended slicers:

- Readmission flag.
- Service line.
- Risk tier.
- Insurance type.

## Formatting Standards

- Use a clean clinical palette: navy `#102033`, blue `#1F77A0`, teal `#0F8B8D`, green `#248F6F`, amber `#D77A00`, light background `#F3F6F8`.
- Use Segoe UI or Aptos.
- Keep card labels at 11-13 pt and KPI values at 28-36 pt.
- Avoid truncated labels. Increase card height before decreasing readability.
- Use consistent decimal formatting:
  - Rates as percentages with one decimal place.
  - Counts as whole numbers.
  - Count card display units set to None.
  - Length of stay with one decimal place.

## Power BI Deliverable

The final Power BI deliverable should be a `.pbix` or `.pbip` file built in Power BI Desktop and verified by opening it successfully. Until that file is created and tested, the repository should describe the Power BI layer as dashboard-ready rather than claiming to include a finished interactive report.
