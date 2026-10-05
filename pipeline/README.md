# Pipeline Overview

The pipeline builds a deterministic synthetic EHR-style dataset and converts it into reporting tables for readmission and quality monitoring.

## Steps

1. Generate raw EHR-style tables:
   - `patients`
   - `encounters`
   - `conditions`
   - `observations`
   - `medications`
2. Identify eligible adult inpatient index encounters.
3. Calculate 30-day readmission outcomes.
4. Engineer encounter-level features:
   - age group
   - service line
   - length of stay
   - prior utilization
   - chronic-condition flags
   - medication complexity
   - A1c and blood-pressure availability
5. Create dashboard-ready aggregate tables.
6. Export data-quality checks.
7. Build a local SQLite validation database from raw CSV tables.
8. Run SQL cohort validation and export `sql_validation_summary.csv`.

## Run

```bash
python pipeline/build_ehr_readmission_dataset.py
python pipeline/build_sqlite_database.py
```

No real patient data or restricted clinical data are used.
