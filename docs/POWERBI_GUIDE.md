# Power BI Guide

Use the processed CSV files in `data/processed/` as Power BI sources.

Recommended report pages:

1. **Readmission Overview**
   - KPI cards: index admissions, readmissions, readmission rate, average length of stay.
   - Bar chart: readmission rate by service line.
   - Column chart: readmission rate by risk tier.

2. **Care Quality**
   - KPI cards: A1c completion, blood-pressure completion, quality gap count, data-quality issue count.
   - Table: quality measure denominator, numerator, gap count, and completion rate.
   - Bar chart: documentation completion by measure.
   - Bar chart: data-quality issue counts.
   - Optional bar chart: operational review flags.

3. **Cohort Profile**
   - Index admissions by age group.
   - Index admissions by insurance type.
   - Average medication count by risk tier.
   - Encounter-level audit table.

Suggested DAX measures are stored in `powerbi/measures.dax`. For exact Power BI field placement and expected values, use `docs/POWERBI_MANUAL_VISUAL_SPEC.md`.
