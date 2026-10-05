# Data Dictionary

## Raw Tables

### `patients`

| Field | Description |
| --- | --- |
| `patient_id` | Synthetic patient identifier. |
| `birth_date` | Simulated birth date. |
| `sex` | Recorded sex category. |
| `race_group` | Broad race grouping. |
| `ethnicity` | Ethnicity category. |
| `insurance_type` | Simulated payer category. |

### `encounters`

| Field | Description |
| --- | --- |
| `encounter_id` | Synthetic encounter identifier. |
| `patient_id` | Patient identifier. |
| `encounter_type` | Inpatient, emergency, or outpatient. |
| `admit_datetime` | Encounter start timestamp. |
| `discharge_datetime` | Encounter end timestamp. |
| `service_line` | Clinical service line. |
| `discharge_disposition` | Simulated discharge destination. |
| `primary_diagnosis` | Primary diagnosis label. |
| `planned_admission` | Planned admission flag. |

### `conditions`

| Field | Description |
| --- | --- |
| `condition_code` | Diagnosis code family. |
| `condition_name` | Diagnosis label. |
| `chronic_flag` | Chronic-condition indicator. |

### `observations`

| Field | Description |
| --- | --- |
| `observation_code` | Observation code. |
| `observation_name` | Observation label. |
| `value_numeric` | Numeric result where applicable. |
| `unit` | Measurement unit. |

### `medications`

| Field | Description |
| --- | --- |
| `medication_name` | Medication label. |
| `therapeutic_class` | Broad medication class. |
| `start_date` | Medication start date. |
| `stop_date` | Medication stop date, if present. |

## Processed Tables

### `readmission_features`

Encounter-level analytic table used for cohort profiling and dashboard aggregation.

### `dashboard_kpis`

Single-row KPI table with total index admissions, readmissions, readmission rate, average length of stay, and high-risk encounter count.

### `readmission_summary_by_service`

Service-line readmission summary.

### `risk_tier_summary`

Readmission summary by derived risk tier.

### `quality_measure_summary`

Care-quality measure summary for A1c and blood-pressure documentation.

### `data_quality_summary`

Documentation-related EHR data-quality issue counts. This table intentionally includes only missing clinical documentation checks, not utilization or risk flags.

### `operational_flag_summary`

Operational review flags such as high prior utilization, long stays, high medication burden, and high-risk tier counts.

### `cohort_summary_by_age`

Age-group summary with index admissions, readmissions, readmission rate, average length of stay, and average medication count.

### `cohort_summary_by_insurance`

Insurance-type summary with index admissions, readmissions, readmission rate, and average length of stay.
