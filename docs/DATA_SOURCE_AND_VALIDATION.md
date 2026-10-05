# Data Source and Validation

## Data Source

This project uses a deterministic synthetic EHR-style dataset created by `pipeline/build_ehr_readmission_dataset.py`.

The dataset is not downloaded from an external clinical database and does not contain real patient records. It includes simulated patient, encounter, diagnosis, observation, and medication tables designed to resemble common EHR analytics structures.

## Why Synthetic Data Was Used

Synthetic data is appropriate for this portfolio project because it allows the repository to demonstrate clinical analytics workflows without using protected health information, restricted credentialed datasets, or institutional data.

This avoids HIPAA and data-use restrictions while still showing practical skills in:

- EHR table modeling.
- Cohort construction.
- 30-day readmission outcome logic.
- Chronic-condition feature engineering.
- Care-quality documentation checks.
- SQL and pandas validation.
- Power BI-ready reporting design.

## What Is Validated

The project validates technical consistency, not clinical truth.

Validated items include:

- Raw tables are created reproducibly from a fixed seed.
- Patient identifiers are synthetic and do not include names or addresses.
- Adult inpatient index admissions are built using documented exclusion rules.
- 30-day readmission counts are internally consistent.
- Risk-tier ordering is directionally coherent in the synthetic cohort.
- SQL validation reproduces the pandas KPI results.
- Processed reporting tables are rebuilt by the pipeline.
- Automated tests confirm the core output checks.

## What Is Not Validated

The project does not validate a clinical model and should not be used for patient-care decisions.

Not validated:

- Real-world readmission rates.
- Causal relationships.
- Clinical prediction performance.
- Hospital quality performance.
- Generalizability to real EHR data.
- Formal measure compliance for CMS or another quality program.

## How To Interpret Results

The results should be interpreted as an analytics workflow demonstration. The value of the project is in the reproducible pipeline, SQL logic, data-quality checks, dashboard-ready outputs, and clear explanation of limitations.

For real clinical research, the same structure could be adapted to a credentialed dataset such as MIMIC-IV after completing the required access and data-use steps.
