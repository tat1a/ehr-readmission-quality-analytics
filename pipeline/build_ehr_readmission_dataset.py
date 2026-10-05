"""Build synthetic EHR readmission and care-quality analytics tables.

This script intentionally uses only simulated records. It creates EHR-style raw
tables and processed reporting tables for a Power BI portfolio dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from random import Random

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
ASSETS_DIR = ROOT / "assets"
SEED = 5105


SERVICE_LINES = [
    "General Medicine",
    "Cardiology",
    "Pulmonary",
    "Endocrinology",
    "General Surgery",
]

PRIMARY_DIAGNOSES = {
    "General Medicine": ["Sepsis", "Cellulitis", "Syncope", "Electrolyte disorder"],
    "Cardiology": ["Heart failure exacerbation", "Chest pain", "Atrial fibrillation"],
    "Pulmonary": ["COPD exacerbation", "Pneumonia", "Asthma exacerbation"],
    "Endocrinology": ["Diabetes complication", "Hyperglycemia", "Hypoglycemia"],
    "General Surgery": ["Postoperative wound issue", "Abdominal pain", "Biliary disease"],
}

CONDITIONS = [
    ("E11", "Type 2 diabetes mellitus"),
    ("I10", "Essential hypertension"),
    ("I50", "Heart failure"),
    ("N18", "Chronic kidney disease"),
    ("J44", "Chronic obstructive pulmonary disease"),
    ("E66", "Obesity"),
]

MEDICATION_CLASSES = [
    ("Metformin", "Antihyperglycemic"),
    ("Insulin glargine", "Antihyperglycemic"),
    ("Lisinopril", "Antihypertensive"),
    ("Amlodipine", "Antihypertensive"),
    ("Furosemide", "Diuretic"),
    ("Atorvastatin", "Lipid lowering"),
    ("Albuterol", "Bronchodilator"),
    ("Apixaban", "Anticoagulant"),
]


@dataclass(frozen=True)
class ProjectSummary:
    patient_count: int
    raw_encounter_count: int
    index_admission_count: int
    readmission_count: int
    readmission_rate: float


def ensure_directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, ASSETS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def date_string(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def datetime_string(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def build_patients(rng: Random, n: int = 900) -> pd.DataFrame:
    rows = []
    sexes = ["Female", "Male"]
    race_groups = ["White", "Black", "Asian", "Other", "Unknown"]
    ethnicities = ["Hispanic or Latino", "Not Hispanic or Latino", "Unknown"]
    insurance_types = ["Medicare", "Medicaid", "Commercial", "Self-pay"]
    anchor = datetime(2026, 1, 1)

    for i in range(1, n + 1):
        age = rng.choices(
            population=[rng.randint(18, 39), rng.randint(40, 64), rng.randint(65, 89)],
            weights=[0.20, 0.45, 0.35],
            k=1,
        )[0]
        rows.append(
            {
                "patient_id": f"P{i:05d}",
                "birth_date": date_string(anchor - timedelta(days=age * 365 + rng.randint(0, 364))),
                "sex": rng.choice(sexes),
                "race_group": rng.choices(race_groups, weights=[0.48, 0.22, 0.12, 0.10, 0.08], k=1)[0],
                "ethnicity": rng.choices(ethnicities, weights=[0.16, 0.76, 0.08], k=1)[0],
                "insurance_type": rng.choices(insurance_types, weights=[0.42, 0.21, 0.31, 0.06], k=1)[0],
            }
        )
    return pd.DataFrame(rows)


def build_conditions(rng: Random, patients: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in patients.itertuples(index=False):
        birth_year = int(str(row.birth_date)[:4])
        age = 2026 - birth_year
        base_probs = {
            "E11": 0.10 + (0.14 if age >= 65 else 0.07 if age >= 40 else 0.00),
            "I10": 0.16 + (0.28 if age >= 65 else 0.15 if age >= 40 else 0.00),
            "I50": 0.04 + (0.12 if age >= 65 else 0.03 if age >= 40 else 0.00),
            "N18": 0.03 + (0.09 if age >= 65 else 0.03 if age >= 40 else 0.00),
            "J44": 0.04 + (0.09 if age >= 65 else 0.03 if age >= 40 else 0.00),
            "E66": 0.18,
        }
        for code, name in CONDITIONS:
            if rng.random() < base_probs[code]:
                rows.append(
                    {
                        "condition_id": f"C{len(rows) + 1:06d}",
                        "patient_id": row.patient_id,
                        "condition_code": code,
                        "condition_name": name,
                        "onset_date": date_string(datetime(2020, 1, 1) + timedelta(days=rng.randint(0, 2100))),
                        "chronic_flag": True,
                    }
                )
    return pd.DataFrame(rows)


def risk_score(patient_id: str, conditions: pd.DataFrame) -> int:
    patient_conditions = set(conditions.loc[conditions["patient_id"] == patient_id, "condition_code"])
    score = 0
    score += 2 if "I50" in patient_conditions else 0
    score += 2 if "N18" in patient_conditions else 0
    score += 1 if "E11" in patient_conditions else 0
    score += 1 if "J44" in patient_conditions else 0
    return score


def build_encounters(rng: Random, patients: pd.DataFrame, conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    start = datetime(2025, 1, 1, 8, 0, 0)
    patient_ids = list(patients["patient_id"])
    encounter_n = 1

    for patient_id in patient_ids:
        score = risk_score(patient_id, conditions)
        inpatient_count = rng.choices([0, 1, 2, 3], weights=[0.12, 0.48, 0.30, 0.10], k=1)[0]
        outpatient_count = rng.randint(1, 5)
        emergency_count = rng.randint(0, 2 + min(score, 3))
        patient_start = start + timedelta(days=rng.randint(0, 300))

        prior_dates = []
        for _ in range(outpatient_count):
            prior_dates.append((patient_start - timedelta(days=rng.randint(15, 180)), "outpatient"))
        for _ in range(emergency_count):
            prior_dates.append((patient_start - timedelta(days=rng.randint(1, 160)), "emergency"))
        for encounter_start, encounter_type in sorted(prior_dates):
            rows.append(
                {
                    "encounter_id": f"E{encounter_n:07d}",
                    "patient_id": patient_id,
                    "encounter_type": encounter_type,
                    "admit_datetime": datetime_string(encounter_start),
                    "discharge_datetime": datetime_string(encounter_start + timedelta(hours=rng.randint(1, 8))),
                    "service_line": rng.choice(SERVICE_LINES),
                    "discharge_disposition": "Home",
                    "primary_diagnosis": rng.choice(["Follow-up", "Medication review", "Acute symptom visit"]),
                    "planned_admission": False,
                }
            )
            encounter_n += 1

        previous_discharge: datetime | None = None
        for visit_idx in range(inpatient_count):
            if visit_idx == 0 or previous_discharge is None:
                admit = patient_start + timedelta(days=rng.randint(0, 45))
            else:
                readmission_probability = min(0.16 + score * 0.07, 0.50)
                if rng.random() < readmission_probability:
                    admit = previous_discharge + timedelta(days=rng.randint(3, 28), hours=rng.randint(0, 12))
                else:
                    admit = previous_discharge + timedelta(days=rng.randint(45, 150), hours=rng.randint(0, 12))

            service = rng.choices(SERVICE_LINES, weights=[0.34, 0.20, 0.16, 0.12, 0.18], k=1)[0]
            los = max(1, int(rng.gauss(3 + min(score, 5) * 0.6, 1.4)))
            discharge = admit + timedelta(days=los, hours=rng.randint(2, 10))
            disposition = rng.choices(
                ["Home", "Home health", "Skilled nursing facility", "Transfer to acute care", "Expired"],
                weights=[0.62, 0.18, 0.13, 0.05, 0.02],
                k=1,
            )[0]
            planned = service == "General Surgery" and rng.random() < 0.18
            rows.append(
                {
                    "encounter_id": f"E{encounter_n:07d}",
                    "patient_id": patient_id,
                    "encounter_type": "inpatient",
                    "admit_datetime": datetime_string(admit),
                    "discharge_datetime": datetime_string(discharge),
                    "service_line": service,
                    "discharge_disposition": disposition,
                    "primary_diagnosis": rng.choice(PRIMARY_DIAGNOSES[service]),
                    "planned_admission": planned,
                }
            )
            encounter_n += 1
            previous_discharge = discharge

    return pd.DataFrame(rows).sort_values(["patient_id", "admit_datetime"]).reset_index(drop=True)


def build_observations(rng: Random, patients: pd.DataFrame, encounters: pd.DataFrame, conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    diabetic = set(conditions.loc[conditions["condition_code"] == "E11", "patient_id"])
    hypertensive = set(conditions.loc[conditions["condition_code"] == "I10", "patient_id"])

    inpatient = encounters[encounters["encounter_type"] == "inpatient"]
    for enc in inpatient.itertuples(index=False):
        admit = datetime.fromisoformat(enc.admit_datetime)
        rows.append(
            {
                "observation_id": f"O{len(rows) + 1:08d}",
                "patient_id": enc.patient_id,
                "encounter_id": enc.encounter_id,
                "observation_datetime": datetime_string(admit + timedelta(hours=2)),
                "observation_code": "8867-4",
                "observation_name": "Heart rate",
                "value_numeric": max(48, round(rng.gauss(84, 16), 0)),
                "value_text": "",
                "unit": "beats/min",
            }
        )
        rows.append(
            {
                "observation_id": f"O{len(rows) + 1:08d}",
                "patient_id": enc.patient_id,
                "encounter_id": enc.encounter_id,
                "observation_datetime": datetime_string(admit + timedelta(hours=2)),
                "observation_code": "8310-5",
                "observation_name": "Body temperature",
                "value_numeric": round(rng.gauss(37.0, 0.7), 1),
                "value_text": "",
                "unit": "Cel",
            }
        )
        if enc.patient_id in hypertensive and rng.random() < 0.83:
            rows.extend(
                [
                    {
                        "observation_id": f"O{len(rows) + 1:08d}",
                        "patient_id": enc.patient_id,
                        "encounter_id": enc.encounter_id,
                        "observation_datetime": datetime_string(admit + timedelta(hours=3)),
                        "observation_code": "8480-6",
                        "observation_name": "Systolic blood pressure",
                        "value_numeric": max(90, round(rng.gauss(138, 18), 0)),
                        "value_text": "",
                        "unit": "mmHg",
                    },
                    {
                        "observation_id": f"O{len(rows) + 1:08d}",
                        "patient_id": enc.patient_id,
                        "encounter_id": enc.encounter_id,
                        "observation_datetime": datetime_string(admit + timedelta(hours=3)),
                        "observation_code": "8462-4",
                        "observation_name": "Diastolic blood pressure",
                        "value_numeric": max(50, round(rng.gauss(78, 11), 0)),
                        "value_text": "",
                        "unit": "mmHg",
                    },
                ]
            )
        if enc.patient_id in diabetic and rng.random() < 0.76:
            rows.append(
                {
                    "observation_id": f"O{len(rows) + 1:08d}",
                    "patient_id": enc.patient_id,
                    "encounter_id": enc.encounter_id,
                    "observation_datetime": datetime_string(admit + timedelta(hours=5)),
                    "observation_code": "4548-4",
                    "observation_name": "Hemoglobin A1c",
                    "value_numeric": round(rng.gauss(7.6, 1.4), 1),
                    "value_text": "",
                    "unit": "%",
                }
            )
    return pd.DataFrame(rows)


def build_medications(rng: Random, encounters: pd.DataFrame, conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    codes_by_patient = conditions.groupby("patient_id")["condition_code"].apply(set).to_dict()
    inpatient = encounters[encounters["encounter_type"] == "inpatient"]

    for enc in inpatient.itertuples(index=False):
        codes = codes_by_patient.get(enc.patient_id, set())
        base_count = 2 + len(codes)
        medication_count = min(9, max(1, int(rng.gauss(base_count, 1.4))))
        selected = rng.sample(MEDICATION_CLASSES, k=min(medication_count, len(MEDICATION_CLASSES)))
        admit = datetime.fromisoformat(enc.admit_datetime)
        discharge = datetime.fromisoformat(enc.discharge_datetime)
        for medication_name, med_class in selected:
            rows.append(
                {
                    "medication_id": f"M{len(rows) + 1:08d}",
                    "patient_id": enc.patient_id,
                    "encounter_id": enc.encounter_id,
                    "medication_name": medication_name,
                    "therapeutic_class": med_class,
                    "start_date": date_string(admit + timedelta(days=rng.randint(0, 1))),
                    "stop_date": "" if rng.random() < 0.55 else date_string(discharge),
                }
            )
    return pd.DataFrame(rows)


def age_at_admit(birth_date: str, admit_datetime: str) -> int:
    birth = datetime.fromisoformat(birth_date)
    admit = datetime.fromisoformat(admit_datetime)
    return int((admit - birth).days // 365.25)


def age_group(age: int) -> str:
    if age < 40:
        return "18-39"
    if age < 65:
        return "40-64"
    if age < 80:
        return "65-79"
    return "80+"


def build_readmission_features(
    patients: pd.DataFrame,
    encounters: pd.DataFrame,
    conditions: pd.DataFrame,
    observations: pd.DataFrame,
    medications: pd.DataFrame,
) -> pd.DataFrame:
    inpatient = encounters[encounters["encounter_type"] == "inpatient"].copy()
    inpatient = inpatient.merge(patients, on="patient_id", how="left")
    inpatient["age_years"] = inpatient.apply(lambda r: age_at_admit(r["birth_date"], r["admit_datetime"]), axis=1)
    inpatient["admit_dt"] = pd.to_datetime(inpatient["admit_datetime"])
    inpatient["discharge_dt"] = pd.to_datetime(inpatient["discharge_datetime"])
    inpatient["length_of_stay_days"] = (inpatient["discharge_dt"] - inpatient["admit_dt"]).dt.total_seconds() / 86400
    inpatient["length_of_stay_days"] = inpatient["length_of_stay_days"].round(1)

    eligible = inpatient[
        (inpatient["age_years"] >= 18)
        & (~inpatient["planned_admission"])
        & (~inpatient["discharge_disposition"].isin(["Expired", "Transfer to acute care"]))
        & (inpatient["length_of_stay_days"] > 0)
    ].copy()

    all_inpatient = inpatient[["patient_id", "encounter_id", "admit_dt", "discharge_dt"]].copy()
    readmitted = []
    prior_counts = []
    for row in eligible.itertuples(index=False):
        patient_stays = all_inpatient[all_inpatient["patient_id"] == row.patient_id]
        next_stays = patient_stays[
            (patient_stays["admit_dt"] > row.discharge_dt)
            & (patient_stays["admit_dt"] <= row.discharge_dt + pd.Timedelta(days=30))
        ]
        readmitted.append(0 if next_stays.empty else 1)
        prior = encounters[
            (encounters["patient_id"] == row.patient_id)
            & (pd.to_datetime(encounters["admit_datetime"]) < row.admit_dt)
            & (pd.to_datetime(encounters["admit_datetime"]) >= row.admit_dt - pd.Timedelta(days=180))
        ]
        prior_counts.append(len(prior))
    eligible["readmitted_30d"] = readmitted
    eligible["prior_encounters_180d"] = prior_counts

    condition_pivot = pd.crosstab(conditions["patient_id"], conditions["condition_code"])
    for code in ["E11", "I10", "I50", "N18", "J44"]:
        eligible[f"{code}_flag"] = eligible["patient_id"].map(condition_pivot.get(code, pd.Series(dtype=int))).fillna(0).astype(int)

    med_counts = medications.groupby("encounter_id").size().rename("medication_count")
    eligible = eligible.merge(med_counts, on="encounter_id", how="left")
    eligible["medication_count"] = eligible["medication_count"].fillna(0).astype(int)

    obs_codes = observations.groupby(["encounter_id", "observation_code"]).size().unstack(fill_value=0)
    eligible["has_a1c"] = eligible["encounter_id"].map(obs_codes.get("4548-4", pd.Series(dtype=int))).fillna(0).gt(0).astype(int)
    eligible["has_bp"] = (
        eligible["encounter_id"].map(obs_codes.get("8480-6", pd.Series(dtype=int))).fillna(0).gt(0)
        & eligible["encounter_id"].map(obs_codes.get("8462-4", pd.Series(dtype=int))).fillna(0).gt(0)
    ).astype(int)
    eligible["age_group"] = eligible["age_years"].apply(age_group)
    eligible["risk_score"] = (
        eligible["prior_encounters_180d"].clip(upper=3)
        + eligible["I50_flag"] * 4
        + eligible["N18_flag"] * 3
        + eligible["E11_flag"] * 2
        + eligible["J44_flag"] * 2
        + (eligible["medication_count"] >= 6).astype(int)
        + (eligible["length_of_stay_days"] >= 5).astype(int)
    )
    eligible["risk_tier"] = pd.cut(
        eligible["risk_score"],
        bins=[-1, 2, 6, 99],
        labels=["Low", "Moderate", "High"],
    ).astype(str)

    columns = [
        "encounter_id",
        "patient_id",
        "age_years",
        "age_group",
        "sex",
        "race_group",
        "ethnicity",
        "insurance_type",
        "service_line",
        "primary_diagnosis",
        "length_of_stay_days",
        "prior_encounters_180d",
        "medication_count",
        "E11_flag",
        "I10_flag",
        "I50_flag",
        "N18_flag",
        "J44_flag",
        "has_a1c",
        "has_bp",
        "risk_score",
        "risk_tier",
        "readmitted_30d",
    ]
    return eligible[columns].sort_values("encounter_id").reset_index(drop=True)


def build_processed_tables(features: pd.DataFrame) -> dict[str, pd.DataFrame]:
    service = (
        features.groupby("service_line", as_index=False)
        .agg(
            index_admissions=("encounter_id", "count"),
            readmissions_30d=("readmitted_30d", "sum"),
            avg_length_of_stay=("length_of_stay_days", "mean"),
            high_risk_encounters=("risk_tier", lambda s: (s == "High").sum()),
        )
    )
    service["readmission_rate"] = service["readmissions_30d"] / service["index_admissions"]
    service["avg_length_of_stay"] = service["avg_length_of_stay"].round(1)
    service["readmission_rate"] = service["readmission_rate"].round(3)

    risk = (
        features.groupby("risk_tier", as_index=False)
        .agg(
            index_admissions=("encounter_id", "count"),
            readmissions_30d=("readmitted_30d", "sum"),
            avg_prior_encounters=("prior_encounters_180d", "mean"),
            avg_medication_count=("medication_count", "mean"),
        )
    )
    risk["readmission_rate"] = (risk["readmissions_30d"] / risk["index_admissions"]).round(3)
    risk["avg_prior_encounters"] = risk["avg_prior_encounters"].round(1)
    risk["avg_medication_count"] = risk["avg_medication_count"].round(1)

    diabetes = features[features["E11_flag"] == 1]
    hypertension = features[features["I10_flag"] == 1]
    quality = pd.DataFrame(
        [
            {
                "measure": "A1c documented for diabetes encounters",
                "denominator": len(diabetes),
                "numerator": int(diabetes["has_a1c"].sum()),
            },
            {
                "measure": "Blood pressure documented for hypertension encounters",
                "denominator": len(hypertension),
                "numerator": int(hypertension["has_bp"].sum()),
            },
        ]
    )
    quality["gap_count"] = quality["denominator"] - quality["numerator"]
    quality["completion_rate"] = (quality["numerator"] / quality["denominator"]).round(3)

    feature_proxy = pd.DataFrame(
        [
            {"feature": "High risk tier", "readmission_rate": features.loc[features["risk_tier"] == "High", "readmitted_30d"].mean()},
            {"feature": "Heart failure", "readmission_rate": features.loc[features["I50_flag"] == 1, "readmitted_30d"].mean()},
            {"feature": "Chronic kidney disease", "readmission_rate": features.loc[features["N18_flag"] == 1, "readmitted_30d"].mean()},
            {"feature": "Prior utilization >= 2", "readmission_rate": features.loc[features["prior_encounters_180d"] >= 2, "readmitted_30d"].mean()},
            {"feature": "Medication count >= 6", "readmission_rate": features.loc[features["medication_count"] >= 6, "readmitted_30d"].mean()},
        ]
    ).fillna(0)
    feature_proxy["readmission_rate"] = feature_proxy["readmission_rate"].round(3)

    data_quality = pd.DataFrame(
        [
            {"check_name": "Missing A1c among diabetes encounters", "issue_count": int((diabetes["has_a1c"] == 0).sum())},
            {"check_name": "Missing BP among hypertension encounters", "issue_count": int((hypertension["has_bp"] == 0).sum())},
        ]
    )

    operational_flags = pd.DataFrame(
        [
            {"flag_name": "Prior utilization >= 2 encounters", "encounter_count": int((features["prior_encounters_180d"] >= 2).sum())},
            {"flag_name": "Long stay encounters", "encounter_count": int((features["length_of_stay_days"] >= 5).sum())},
            {"flag_name": "High medication count encounters", "encounter_count": int((features["medication_count"] >= 6).sum())},
            {"flag_name": "High risk tier encounters", "encounter_count": int((features["risk_tier"] == "High").sum())},
        ]
    )

    cohort_by_age = (
        features.groupby("age_group", as_index=False)
        .agg(
            index_admissions=("encounter_id", "count"),
            readmissions_30d=("readmitted_30d", "sum"),
            avg_length_of_stay=("length_of_stay_days", "mean"),
            avg_medication_count=("medication_count", "mean"),
        )
    )
    cohort_by_age["readmission_rate"] = (cohort_by_age["readmissions_30d"] / cohort_by_age["index_admissions"]).round(3)
    cohort_by_age["avg_length_of_stay"] = cohort_by_age["avg_length_of_stay"].round(1)
    cohort_by_age["avg_medication_count"] = cohort_by_age["avg_medication_count"].round(1)

    cohort_by_insurance = (
        features.groupby("insurance_type", as_index=False)
        .agg(
            index_admissions=("encounter_id", "count"),
            readmissions_30d=("readmitted_30d", "sum"),
            avg_length_of_stay=("length_of_stay_days", "mean"),
        )
    )
    cohort_by_insurance["readmission_rate"] = (
        cohort_by_insurance["readmissions_30d"] / cohort_by_insurance["index_admissions"]
    ).round(3)
    cohort_by_insurance["avg_length_of_stay"] = cohort_by_insurance["avg_length_of_stay"].round(1)

    kpis = pd.DataFrame(
        [
            {
                "index_admissions": len(features),
                "readmissions_30d": int(features["readmitted_30d"].sum()),
                "readmission_rate": round(float(features["readmitted_30d"].mean()), 3),
                "avg_length_of_stay": round(float(features["length_of_stay_days"].mean()), 1),
                "high_risk_encounters": int((features["risk_tier"] == "High").sum()),
            }
        ]
    )

    return {
        "readmission_features": features,
        "readmission_summary_by_service": service.sort_values("readmission_rate", ascending=False),
        "risk_tier_summary": risk.sort_values("risk_tier"),
        "quality_measure_summary": quality,
        "feature_importance_proxy": feature_proxy.sort_values("readmission_rate", ascending=False),
        "data_quality_summary": data_quality.sort_values("issue_count", ascending=False),
        "operational_flag_summary": operational_flags.sort_values("encounter_count", ascending=False),
        "cohort_summary_by_age": cohort_by_age,
        "cohort_summary_by_insurance": cohort_by_insurance.sort_values("index_admissions", ascending=False),
        "dashboard_kpis": kpis,
    }


def write_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)


def create_preview(processed: dict[str, pd.DataFrame]) -> None:
    from PIL import Image, ImageDraw, ImageFont

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def draw_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: str, label: str, value: str) -> None:
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=0, fill="white")
        draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
        draw.text((x1 + 28, y1 + 26), label.upper(), fill="#5b6978", font=font(17, True))
        draw.text((x1 + 28, y1 + 70), value, fill="#102033", font=font(48, True))

    def pct(value: float) -> str:
        return f"{value * 100:.1f}%"

    kpis = processed["dashboard_kpis"].iloc[0]
    service = processed["readmission_summary_by_service"].copy()
    quality = processed["quality_measure_summary"].copy()
    risk = processed["risk_tier_summary"].copy()

    width, height = 1600, 900
    img = Image.new("RGB", (width, height), "#f3f6f8")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, width, 120), fill="#102033")
    draw.text((46, 28), "EHR Readmission & Care Quality Analytics", fill="white", font=font(36, True))
    draw.text((46, 76), "Synthetic EHR cohort monitoring | Python + SQL + Power BI-ready outputs", fill="#d7e0ea", font=font(18))

    kpi_values = [
        ("Index admissions", f"{int(kpis['index_admissions']):,}", "#1f77a0"),
        ("30-day readmissions", f"{int(kpis['readmissions_30d']):,}", "#0f8b8d"),
        ("Readmission rate", pct(float(kpis["readmission_rate"])), "#248f6f"),
        ("Avg. LOS", f"{float(kpis['avg_length_of_stay']):.1f} d", "#d77a00"),
    ]
    card_w, card_h, gap = 350, 155, 42
    for i, (label, value, accent) in enumerate(kpi_values):
        x = 46 + i * (card_w + gap)
        draw_card(draw, (x, 180, x + card_w, 180 + card_h), accent, label, value)

    # Service readmission panel
    draw.rectangle((46, 390, 760, 770), fill="white")
    draw.text((72, 422), "30-day readmission rate by service line", fill="#102033", font=font(24, True))
    service = service.sort_values("readmission_rate", ascending=False).head(5)
    max_rate = max(float(service["readmission_rate"].max()), 0.01)
    y = 475
    for row in service.itertuples(index=False):
        rate = float(row.readmission_rate)
        draw.text((72, y + 5), row.service_line, fill="#22313f", font=font(19, True))
        draw.rectangle((320, y + 9, 665, y + 34), fill="#dfe6ed")
        draw.rectangle((320, y + 9, 320 + int(345 * rate / max_rate), y + 34), fill="#1f77a0")
        draw.text((685, y + 4), pct(rate), fill="#22313f", font=font(18, True))
        y += 56

    # Risk tier panel
    draw.rectangle((805, 390, 1170, 770), fill="white")
    draw.text((832, 422), "Readmission by risk tier", fill="#102033", font=font(24, True))
    risk_order = ["Low", "Moderate", "High"]
    risk_map = {str(r.risk_tier): float(r.readmission_rate) for r in risk.itertuples(index=False)}
    colors = {"Low": "#1f77a0", "Moderate": "#0f8b8d", "High": "#d77a00"}
    max_risk = max(risk_map.values()) if risk_map else 0.01
    x = 845
    for tier in risk_order:
        rate = risk_map.get(tier, 0.0)
        bar_h = int(220 * rate / max_risk)
        draw.rectangle((x, 700 - bar_h, x + 75, 700), fill=colors[tier])
        draw.text((x - 4, 712), tier, fill="#22313f", font=font(17, True))
        draw.text((x + 2, 670 - bar_h), pct(rate), fill="#22313f", font=font(17, True))
        x += 105

    # Quality panel
    draw.rectangle((1215, 390, 1554, 770), fill="white")
    draw.text((1242, 422), "Care-quality completion", fill="#102033", font=font(24, True))
    y = 492
    for row in quality.itertuples(index=False):
        rate = float(row.completion_rate)
        label = "A1c documented" if "A1c" in row.measure else "BP documented"
        draw.text((1242, y), label, fill="#22313f", font=font(18, True))
        draw.rectangle((1242, y + 34, 1495, y + 58), fill="#dfe6ed")
        draw.rectangle((1242, y + 34, 1242 + int(253 * rate), y + 58), fill="#248f6f")
        draw.text((1505, y + 30), pct(rate), fill="#22313f", font=font(17, True))
        y += 105

    draw.text(
        (46, 840),
        "All records are synthetic. Dashboard supports cohort review, readmission monitoring, care-quality checks, and EHR data-quality discussion.",
        fill="#526173",
        font=font(17),
    )
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    img.save(ASSETS_DIR / "dashboard-preview.png")


def build_project() -> ProjectSummary:
    ensure_directories()
    rng = Random(SEED)
    patients = build_patients(rng)
    conditions = build_conditions(rng, patients)
    encounters = build_encounters(rng, patients, conditions)
    observations = build_observations(rng, patients, encounters, conditions)
    medications = build_medications(rng, encounters, conditions)

    raw_tables = {
        "patients": patients,
        "encounters": encounters,
        "conditions": conditions,
        "observations": observations,
        "medications": medications,
    }
    write_tables(raw_tables, RAW_DIR)

    features = build_readmission_features(patients, encounters, conditions, observations, medications)
    processed = build_processed_tables(features)
    write_tables(processed, PROCESSED_DIR)
    create_preview(processed)

    kpis = processed["dashboard_kpis"].iloc[0]
    return ProjectSummary(
        patient_count=len(patients),
        raw_encounter_count=len(encounters),
        index_admission_count=int(kpis["index_admissions"]),
        readmission_count=int(kpis["readmissions_30d"]),
        readmission_rate=float(kpis["readmission_rate"]),
    )


if __name__ == "__main__":
    summary = build_project()
    print(
        "Built synthetic EHR project: "
        f"{summary.patient_count} patients, "
        f"{summary.raw_encounter_count} encounters, "
        f"{summary.index_admission_count} index admissions, "
        f"{summary.readmission_count} readmissions "
        f"({summary.readmission_rate:.1%})."
    )
