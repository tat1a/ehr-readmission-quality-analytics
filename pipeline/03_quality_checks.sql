-- Data-quality checks for synthetic EHR analytics.

-- 1. Encounters with invalid or missing discharge timestamps.
select
    count(*) as invalid_discharge_rows
from encounters
where discharge_datetime is null
   or discharge_datetime <= admit_datetime;

-- 2. Orphan records by table.
select 'encounters_without_patient' as check_name, count(*) as issue_count
from encounters e
left join patients p on p.patient_id = e.patient_id
where p.patient_id is null
union all
select 'conditions_without_patient', count(*)
from conditions c
left join patients p on p.patient_id = c.patient_id
where p.patient_id is null
union all
select 'observations_without_patient', count(*)
from observations o
left join patients p on p.patient_id = o.patient_id
where p.patient_id is null
union all
select 'medications_without_patient', count(*)
from medications m
left join patients p on p.patient_id = m.patient_id
where p.patient_id is null;

-- 3. Diabetes patients without a recent A1c observation.
select
    count(distinct c.patient_id) as diabetes_patients_without_recent_a1c
from conditions c
left join observations o
    on o.patient_id = c.patient_id
   and o.observation_code = '4548-4'
   and o.observation_datetime::date >= current_date - interval '365 days'
where c.condition_code = 'E11'
  and o.observation_id is null;

-- 4. Hypertension patients without a blood-pressure observation.
select
    count(distinct c.patient_id) as hypertension_patients_without_bp
from conditions c
left join observations o
    on o.patient_id = c.patient_id
   and o.observation_code in ('8480-6', '8462-4')
   and o.observation_datetime::date >= current_date - interval '365 days'
where c.condition_code = 'I10'
  and o.observation_id is null;

-- 5. Summary of readmission outcome by service line.
select
    service_line,
    count(*) as index_admissions,
    sum(readmitted_30d) as readmissions_30d,
    avg(readmitted_30d::numeric) as readmission_rate
from cohort_readmission_features
group by service_line
order by readmission_rate desc;
