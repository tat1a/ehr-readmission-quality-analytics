# Methods

## Design

This project is a synthetic EHR analytics demonstration. It emulates common clinical data analyst tasks: cohort construction, encounter-level feature engineering, outcome definition, data-quality checks, and dashboard-ready aggregation.

## Cohort

The index cohort is adult inpatient encounters. Planned admissions, invalid encounter intervals, expired discharges, and transfers to acute care are excluded from the readmission denominator.

## Outcome

The primary reporting outcome is 30-day inpatient readmission. An index encounter is flagged if the same patient has a subsequent inpatient encounter after discharge and within 30 days.

## Feature Engineering

Encounter-level features include:

- age group;
- service line;
- length of stay;
- prior utilization in the preceding 180 days;
- diabetes, hypertension, heart failure, and chronic kidney disease flags;
- medication count at discharge;
- A1c and blood-pressure observation availability.

## Quality Measures

The project includes two care-quality examples:

- A1c documentation among patients with diabetes.
- Blood-pressure documentation among patients with hypertension.

These are operational reporting measures, not formal quality-program specifications.

## Limitations

All records are simulated. Results are suitable for portfolio demonstration and workflow review only. They should not be interpreted as clinical evidence, real-world performance, or model validation.

See `DATA_SOURCE_AND_VALIDATION.md` for a fuller explanation of what is technically validated and what is not clinically validated.
