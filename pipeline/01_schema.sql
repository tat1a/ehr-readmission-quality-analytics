-- Synthetic EHR readmission analytics schema.
-- This schema is for portfolio demonstration only and contains no real patient data.

create table patients (
    patient_id varchar(16) primary key,
    birth_date date not null,
    sex varchar(16) not null,
    race_group varchar(32) not null,
    ethnicity varchar(32) not null,
    insurance_type varchar(32) not null
);

create table encounters (
    encounter_id varchar(20) primary key,
    patient_id varchar(16) not null references patients(patient_id),
    encounter_type varchar(32) not null,
    admit_datetime timestamp not null,
    discharge_datetime timestamp,
    service_line varchar(48) not null,
    discharge_disposition varchar(48) not null,
    primary_diagnosis varchar(80) not null,
    planned_admission boolean not null
);

create table conditions (
    condition_id varchar(20) primary key,
    patient_id varchar(16) not null references patients(patient_id),
    condition_code varchar(16) not null,
    condition_name varchar(80) not null,
    onset_date date not null,
    chronic_flag boolean not null
);

create table observations (
    observation_id varchar(24) primary key,
    patient_id varchar(16) not null references patients(patient_id),
    encounter_id varchar(20) references encounters(encounter_id),
    observation_datetime timestamp not null,
    observation_code varchar(24) not null,
    observation_name varchar(80) not null,
    value_numeric numeric(10, 2),
    value_text varchar(80),
    unit varchar(24)
);

create table medications (
    medication_id varchar(24) primary key,
    patient_id varchar(16) not null references patients(patient_id),
    encounter_id varchar(20) references encounters(encounter_id),
    medication_name varchar(80) not null,
    therapeutic_class varchar(80) not null,
    start_date date not null,
    stop_date date
);
