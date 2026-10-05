"""Create a local SQLite database and validate SQL cohort logic.

The database is generated from synthetic CSV files created by
build_ehr_readmission_dataset.py. It is not intended to be committed as a
source artifact; the reproducible script and SQL validation summary are the
portfolio deliverables.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "ehr_readmission.sqlite"
VALIDATION_SQL = ROOT / "pipeline" / "04_sqlite_cohort_validation.sql"


RAW_TABLES = ["patients", "encounters", "conditions", "observations", "medications"]


def load_raw_tables(connection: sqlite3.Connection) -> None:
    for table in RAW_TABLES:
        csv_path = RAW_DIR / f"{table}.csv"
        frame = pd.read_csv(csv_path)
        frame.to_sql(table, connection, if_exists="replace", index=False)


def build_database() -> pd.DataFrame:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    with sqlite3.connect(DATABASE_PATH) as connection:
        load_raw_tables(connection)
        connection.executescript(VALIDATION_SQL.read_text(encoding="utf-8"))
        summary = pd.read_sql_query("select * from sql_validation_summary", connection)

    summary.to_csv(PROCESSED_DIR / "sql_validation_summary.csv", index=False)
    return summary


if __name__ == "__main__":
    result = build_database().iloc[0]
    print(
        "Built SQLite validation database: "
        f"{int(result['index_admissions'])} index admissions, "
        f"{int(result['readmissions_30d'])} readmissions, "
        f"{float(result['readmission_rate']):.1%} readmission rate."
    )
