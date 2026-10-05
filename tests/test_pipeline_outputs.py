import subprocess
import sys
import unittest
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class PipelineOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "pipeline" / "build_ehr_readmission_dataset.py")],
            check=True,
            cwd=ROOT,
        )
        subprocess.run(
            [sys.executable, str(ROOT / "pipeline" / "build_sqlite_database.py")],
            check=True,
            cwd=ROOT,
        )

    def test_expected_processed_outputs_exist(self) -> None:
        expected = {
            "dashboard_kpis.csv",
            "cohort_summary_by_age.csv",
            "cohort_summary_by_insurance.csv",
            "data_quality_summary.csv",
            "feature_importance_proxy.csv",
            "operational_flag_summary.csv",
            "quality_measure_summary.csv",
            "readmission_features.csv",
            "readmission_summary_by_service.csv",
            "risk_tier_summary.csv",
            "sql_validation_summary.csv",
        }
        actual = {path.name for path in (ROOT / "data" / "processed").glob("*.csv")}
        self.assertTrue(expected.issubset(actual))

    def test_dashboard_kpis_are_consistent(self) -> None:
        kpis = pd.read_csv(ROOT / "data" / "processed" / "dashboard_kpis.csv").iloc[0]
        features = pd.read_csv(ROOT / "data" / "processed" / "readmission_features.csv")

        self.assertEqual(int(kpis["index_admissions"]), len(features))
        self.assertEqual(int(kpis["readmissions_30d"]), int(features["readmitted_30d"].sum()))
        self.assertAlmostEqual(
            float(kpis["readmission_rate"]),
            round(float(features["readmitted_30d"].mean()), 3),
        )

    def test_risk_tier_signal_is_ordered(self) -> None:
        risk = pd.read_csv(ROOT / "data" / "processed" / "risk_tier_summary.csv")
        rates = dict(zip(risk["risk_tier"], risk["readmission_rate"]))

        self.assertGreater(rates["High"], rates["Moderate"])
        self.assertGreater(rates["Moderate"], rates["Low"])

    def test_sql_validation_matches_pandas_kpis(self) -> None:
        kpis = pd.read_csv(ROOT / "data" / "processed" / "dashboard_kpis.csv").iloc[0]
        sql = pd.read_csv(ROOT / "data" / "processed" / "sql_validation_summary.csv").iloc[0]

        self.assertEqual(int(kpis["index_admissions"]), int(sql["index_admissions"]))
        self.assertEqual(int(kpis["readmissions_30d"]), int(sql["readmissions_30d"]))
        self.assertAlmostEqual(float(kpis["readmission_rate"]), float(sql["readmission_rate"]))

    def test_data_quality_checks_are_documentation_issues_only(self) -> None:
        quality = pd.read_csv(ROOT / "data" / "processed" / "quality_measure_summary.csv")
        data_quality = pd.read_csv(ROOT / "data" / "processed" / "data_quality_summary.csv")

        self.assertEqual(int(quality["gap_count"].sum()), int(data_quality["issue_count"].sum()))
        self.assertEqual(
            set(data_quality["check_name"]),
            {"Missing A1c among diabetes encounters", "Missing BP among hypertension encounters"},
        )

    def test_no_real_patient_identifiers_are_present(self) -> None:
        patients = pd.read_csv(ROOT / "data" / "raw" / "patients.csv")

        self.assertTrue(patients["patient_id"].str.match(r"^P\d{5}$").all())
        self.assertNotIn("name", {col.lower() for col in patients.columns})
        self.assertNotIn("address", {col.lower() for col in patients.columns})

    def test_powerbi_project_files_are_valid_json(self) -> None:
        pbip = ROOT / "powerbi" / "EHR_Readmission_Quality_Analytics.pbip"
        report = ROOT / "powerbi" / "EHR_Readmission_Quality_Analytics.Report"
        semantic_model = ROOT / "powerbi" / "EHR_Readmission_Quality_Analytics.SemanticModel"

        self.assertTrue(pbip.exists())
        self.assertTrue(report.exists())
        self.assertTrue(semantic_model.exists())

        for json_path in report.rglob("*.json"):
            with json_path.open(encoding="utf-8") as handle:
                json.load(handle)


if __name__ == "__main__":
    unittest.main()
