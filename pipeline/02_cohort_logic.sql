-- Cohort logic for adult inpatient 30-day readmission analytics.
-- SQL dialect: PostgreSQL-style reference implementation.

with inpatient_encounters as (
    select
        e.encounter_id,
        e.patient_id,
        e.admit_datetime,
        e.discharge_datetime,
        e.service_line,
        e.discharge_disposition,
        e.primary_diagnosis,
        e.planned_admission,
        extract(year from age(e.admit_datetime::date, p.birth_date)) as age_years
    from encounters e
    join patients p
        on p.patient_id = e.patient_id
    where e.encounter_type = 'inpatient'
      and e.discharge_datetime is not null
      and e.discharge_datetime > e.admit_datetime
), eligible_index as (
    select *
    from inpatient_encounters
    where age_years >= 18
      and planned_admission = false
      and discharge_disposition not in ('Expired', 'Transfer to acute care')
), next_inpatient as (
    select
        idx.encounter_id,
        min(next_e.admit_datetime) as next_inpatient_admit
    from eligible_index idx
    left join encounters next_e
        on next_e.patient_id = idx.patient_id
       and next_e.encounter_type = 'inpatient'
       and next_e.admit_datetime > idx.discharge_datetime
       and next_e.admit_datetime <= idx.discharge_datetime + interval '30 days'
    group by idx.encounter_id
), prior_utilization as (
    select
        idx.encounter_id,
        count(prior_e.encounter_id) as prior_encounters_180d
    from eligible_index idx
    left join encounters prior_e
        on prior_e.patient_id = idx.patient_id
       and prior_e.admit_datetime < idx.admit_datetime
       and prior_e.admit_datetime >= idx.admit_datetime - interval '180 days'
    group by idx.encounter_id
), chronic_flags as (
    select
        idx.encounter_id,
        max(case when c.condition_code = 'E11' then 1 else 0 end) as diabetes_flag,
        max(case when c.condition_code = 'I10' then 1 else 0 end) as hypertension_flag,
        max(case when c.condition_code = 'I50' then 1 else 0 end) as heart_failure_flag,
        max(case when c.condition_code = 'N18' then 1 else 0 end) as ckd_flag
    from eligible_index idx
    left join conditions c
        on c.patient_id = idx.patient_id
       and c.onset_date <= idx.admit_datetime::date
       and c.chronic_flag = true
    group by idx.encounter_id
)
select
    idx.*,
    extract(day from idx.discharge_datetime - idx.admit_datetime) as length_of_stay_days,
    case when n.next_inpatient_admit is not null then 1 else 0 end as readmitted_30d,
    n.next_inpatient_admit,
    coalesce(pu.prior_encounters_180d, 0) as prior_encounters_180d,
    coalesce(cf.diabetes_flag, 0) as diabetes_flag,
    coalesce(cf.hypertension_flag, 0) as hypertension_flag,
    coalesce(cf.heart_failure_flag, 0) as heart_failure_flag,
    coalesce(cf.ckd_flag, 0) as ckd_flag
from eligible_index idx
left join next_inpatient n
    on n.encounter_id = idx.encounter_id
left join prior_utilization pu
    on pu.encounter_id = idx.encounter_id
left join chronic_flags cf
    on cf.encounter_id = idx.encounter_id;
