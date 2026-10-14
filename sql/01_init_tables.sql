-- Create Staging Schema
CREATE SCHEMA IF NOT EXISTS clinical_staging;

-- 1. Demographics Table
CREATE TABLE clinical_staging.raw_demographics (
    subjid VARCHAR(20) PRIMARY KEY,
    brthdat DATE,
    ic_date DATE
);

-- 2. Vital Signs Table
CREATE TABLE clinical_staging.raw_vitals (
    subjid VARCHAR(20),
    vs_sysbp INT,
    vs_diabp INT
);

-- 3. Adverse Events Table
CREATE TABLE clinical_staging.raw_adverse_events (
    subjid VARCHAR(20),
    ae_term VARCHAR(100),
    ae_sev VARCHAR(20),
    ae_ser VARCHAR(10)
);

SELECT * FROM clinical_staging.raw_demographics;