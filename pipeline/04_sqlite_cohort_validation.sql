-- SQLite validation query for the synthetic EHR readmission cohort.
-- This mirrors the pandas cohort logic and is used by build_sqlite_database.py.

drop table if exists cohort_readmission_features_sql;

create table cohort_readmission_features_sql as
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
        cast(
            (julianday(e.admit_datetime) - julianday(p.birth_date)) / 365.25
            as integer
        ) as age_years
    from encounters e
    join patients p
        on p.patient_id = e.patient_id
    where e.encounter_type = 'inpatient'
      and e.discharge_datetime is not null
      and julianday(e.discharge_datetime) > julianday(e.admit_datetime)
), eligible_index as (
    select *
    from inpatient_encounters
    where age_years >= 18
      and planned_admission in ('False', '0', 0)
      and discharge_disposition not in ('Expired', 'Transfer to acute care')
), next_inpatient as (
    select
        idx.encounter_id,
        min(next_e.admit_datetime) as next_inpatient_admit
    from eligible_index idx
    left join encounters next_e
        on next_e.patient_id = idx.patient_id
       and next_e.encounter_type = 'inpatient'
       and julianday(next_e.admit_datetime) > julianday(idx.discharge_datetime)
       and julianday(next_e.admit_datetime) <= julianday(idx.discharge_datetime) + 30
    group by idx.encounter_id
), prior_utilization as (
    select
        idx.encounter_id,
        count(prior_e.encounter_id) as prior_encounters_180d
    from eligible_index idx
    left join encounters prior_e
        on prior_e.patient_id = idx.patient_id
       and julianday(prior_e.admit_datetime) < julianday(idx.admit_datetime)
       and julianday(prior_e.admit_datetime) >= julianday(idx.admit_datetime) - 180
    group by idx.encounter_id
), chronic_flags as (
    select
        idx.encounter_id,
        max(case when c.condition_code = 'E11' then 1 else 0 end) as diabetes_flag,
        max(case when c.condition_code = 'I10' then 1 else 0 end) as hypertension_flag,
        max(case when c.condition_code = 'I50' then 1 else 0 end) as heart_failure_flag,
        max(case when c.condition_code = 'N18' then 1 else 0 end) as ckd_flag,
        max(case when c.condition_code = 'J44' then 1 else 0 end) as copd_flag
    from eligible_index idx
    left join conditions c
        on c.patient_id = idx.patient_id
       and date(c.onset_date) <= date(idx.admit_datetime)
       and c.chronic_flag in ('True', '1', 1)
    group by idx.encounter_id
), medications_by_encounter as (
    select
        encounter_id,
        count(*) as medication_count
    from medications
    group by encounter_id
), observations_by_encounter as (
    select
        encounter_id,
        max(case when observation_code = '4548-4' then 1 else 0 end) as has_a1c,
        max(case when observation_code = '8480-6' then 1 else 0 end) as has_sbp,
        max(case when observation_code = '8462-4' then 1 else 0 end) as has_dbp
    from observations
    group by encounter_id
)
select
    idx.encounter_id,
    idx.patient_id,
    idx.age_years,
    idx.service_line,
    idx.primary_diagnosis,
    round(julianday(idx.discharge_datetime) - julianday(idx.admit_datetime), 1) as length_of_stay_days,
    case when n.next_inpatient_admit is not null then 1 else 0 end as readmitted_30d,
    coalesce(pu.prior_encounters_180d, 0) as prior_encounters_180d,
    coalesce(cf.diabetes_flag, 0) as E11_flag,
    coalesce(cf.hypertension_flag, 0) as I10_flag,
    coalesce(cf.heart_failure_flag, 0) as I50_flag,
    coalesce(cf.ckd_flag, 0) as N18_flag,
    coalesce(cf.copd_flag, 0) as J44_flag,
    coalesce(m.medication_count, 0) as medication_count,
    coalesce(o.has_a1c, 0) as has_a1c,
    case
        when coalesce(o.has_sbp, 0) = 1 and coalesce(o.has_dbp, 0) = 1 then 1
        else 0
    end as has_bp
from eligible_index idx
left join next_inpatient n
    on n.encounter_id = idx.encounter_id
left join prior_utilization pu
    on pu.encounter_id = idx.encounter_id
left join chronic_flags cf
    on cf.encounter_id = idx.encounter_id
left join medications_by_encounter m
    on m.encounter_id = idx.encounter_id
left join observations_by_encounter o
    on o.encounter_id = idx.encounter_id;

drop table if exists sql_validation_summary;

create table sql_validation_summary as
select
    count(*) as index_admissions,
    sum(readmitted_30d) as readmissions_30d,
    round(avg(readmitted_30d), 3) as readmission_rate,
    round(avg(length_of_stay_days), 1) as avg_length_of_stay,
    sum(case when medication_count >= 6 then 1 else 0 end) as high_medication_count_encounters
from cohort_readmission_features_sql;
