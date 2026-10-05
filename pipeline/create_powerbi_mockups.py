"""Create static Power BI layout mockups from processed reporting tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
ASSETS_DIR = ROOT / "assets"


COLORS = {
    "ink": "#111827",
    "nav": "#0F172A",
    "blue": "#2563EB",
    "teal": "#14B8A6",
    "green": "#0F766E",
    "amber": "#F97316",
    "purple": "#7C3AED",
    "gray": "#64748B",
    "line": "#E5E7EB",
    "bg": "#F8FAFC",
    "soft": "#EEF2FF",
    "white": "#FFFFFF",
}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (1600, 900), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 188, 900), fill=COLORS["nav"])
    draw.text((34, 34), "EHR", fill=COLORS["white"], font=font(31, True))
    draw.text((34, 75), "QUALITY OPS", fill="#CBD5E1", font=font(13, True))
    for i, label in enumerate(["Overview", "Quality", "Cohort"]):
        y = 156 + i * 58
        fill = "#1E293B" if i == 0 else COLORS["nav"]
        draw.rounded_rectangle((22, y, 166, y + 38), radius=5, fill=fill)
        draw.text((42, y + 10), label, fill="#E2E8F0", font=font(14, True))
    draw.text((234, 42), title, fill=COLORS["ink"], font=font(33, True))
    draw.text((236, 88), subtitle, fill=COLORS["gray"], font=font(16))
    return img, draw


def canvas_with_active(title: str, subtitle: str, active_label: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (1600, 900), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 188, 900), fill=COLORS["nav"])
    draw.text((34, 34), "EHR", fill=COLORS["white"], font=font(31, True))
    draw.text((34, 75), "QUALITY OPS", fill="#CBD5E1", font=font(13, True))
    for i, label in enumerate(["Overview", "Quality", "Cohort"]):
        y = 156 + i * 58
        fill = "#1E293B" if label == active_label else COLORS["nav"]
        draw.rounded_rectangle((22, y, 166, y + 38), radius=5, fill=fill)
        draw.text((42, y + 10), label, fill="#E2E8F0", font=font(14, True))
    draw.text((234, 42), title, fill=COLORS["ink"], font=font(33, True))
    draw.text((236, 88), subtitle, fill=COLORS["gray"], font=font(16))
    return img, draw


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: str, accent: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill=COLORS["white"], outline=COLORS["line"], width=1)
    draw.rounded_rectangle((x1 + 22, y1 + 22, x1 + 72, y1 + 72), radius=8, fill=accent)
    draw.text((x1 + 92, y1 + 24), label.upper(), fill=COLORS["gray"], font=font(13, True))
    draw.text((x1 + 92, y1 + 54), value, fill=COLORS["ink"], font=font(35, True))


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> None:
    draw.rounded_rectangle(box, radius=10, fill=COLORS["white"], outline=COLORS["line"], width=1)
    draw.rectangle((box[0], box[1], box[2], box[1] + 5), fill=COLORS["blue"])
    draw.text((box[0] + 24, box[1] + 24), title, fill=COLORS["ink"], font=font(21, True))


def page_one() -> None:
    kpis = pd.read_csv(PROCESSED_DIR / "dashboard_kpis.csv").iloc[0]
    service = pd.read_csv(PROCESSED_DIR / "readmission_summary_by_service.csv")
    risk = pd.read_csv(PROCESSED_DIR / "risk_tier_summary.csv")

    img, draw = canvas(
        "EHR Readmission Analytics",
        "Clinical operations view: readmission monitoring, service variation, and risk tier stratification",
    )

    cards = [
        ("Index admissions", f"{int(kpis['index_admissions']):,}", COLORS["blue"]),
        ("30-day readmissions", f"{int(kpis['readmissions_30d']):,}", COLORS["teal"]),
        ("Readmission rate", pct(float(kpis["readmission_rate"])), COLORS["green"]),
        ("Avg. length of stay", f"{float(kpis['avg_length_of_stay']):.1f} d", COLORS["amber"]),
    ]
    for i, item in enumerate(cards):
        x = 234 + i * 326
        card(draw, (x, 142, x + 292, 260), item[0], item[1], item[2])

    panel(draw, (234, 304, 930, 754), "Readmission rate by service line")
    max_rate = service["readmission_rate"].max()
    y = 405
    for row in service.sort_values("readmission_rate", ascending=False).itertuples(index=False):
        draw.text((264, y), row.service_line, fill=COLORS["ink"], font=font(17, True))
        draw.rectangle((504, y + 5, 812, y + 31), fill="#E2E8F0")
        draw.rectangle((504, y + 5, 504 + int(308 * row.readmission_rate / max_rate), y + 31), fill=COLORS["blue"])
        draw.text((834, y + 1), pct(row.readmission_rate), fill=COLORS["ink"], font=font(16, True))
        y += 61

    panel(draw, (970, 304, 1276, 754), "Risk tier signal")
    order = ["Low", "Moderate", "High"]
    risk_map = {row.risk_tier: row.readmission_rate for row in risk.itertuples(index=False)}
    max_risk = max(risk_map.values())
    x = 1016
    for tier in order:
        rate = risk_map[tier]
        h = int(245 * rate / max_risk)
        color = COLORS["green"] if tier == "Low" else COLORS["teal"] if tier == "Moderate" else COLORS["amber"]
        draw.rectangle((x, 690 - h, x + 70, 690), fill=color)
        draw.text((x - 6, 710), tier, fill=COLORS["ink"], font=font(15, True))
        draw.text((x - 1, 658 - h), pct(rate), fill=COLORS["ink"], font=font(15, True))
        x += 82

    panel(draw, (1314, 304, 1556, 754), "Filters")
    slicers = ["Service line", "Risk tier", "Age group", "Insurance type", "Primary diagnosis"]
    y = 405
    for slicer in slicers:
        draw.rounded_rectangle((1342, y, 1524, y + 42), radius=8, fill="#F8FAFC", outline=COLORS["line"])
        draw.text((1356, y + 10), slicer, fill=COLORS["ink"], font=font(14, True))
        draw.text((1500, y + 10), "v", fill=COLORS["gray"], font=font(15, True))
        y += 62

    draw.text(
        (234, 834),
        "Data basis: encounter-level readmission_features fact table; slicers filter KPI cards and rate charts.",
        fill=COLORS["gray"],
        font=font(16),
    )
    img.save(ASSETS_DIR / "powerbi-page-1-readmission-overview.png")


def page_two() -> None:
    quality = pd.read_csv(PROCESSED_DIR / "quality_measure_summary.csv")
    dq = pd.read_csv(PROCESSED_DIR / "data_quality_summary.csv")
    operational = pd.read_csv(PROCESSED_DIR / "operational_flag_summary.csv")

    img, draw = canvas_with_active(
        "Care Quality and EHR Data Quality",
        "Documentation completion, gap counts, and operational data-quality checks",
        "Quality",
    )

    a1c = quality[quality["measure"].str.contains("A1c")].iloc[0]
    bp = quality[quality["measure"].str.contains("Blood pressure")].iloc[0]
    gap_count = int(quality["gap_count"].sum())
    issue_count = int(dq["issue_count"].sum())
    cards = [
        ("A1c completion", pct(float(a1c["completion_rate"])), COLORS["green"]),
        ("BP completion", pct(float(bp["completion_rate"])), COLORS["green"]),
        ("Quality gaps", f"{gap_count:,}", COLORS["amber"]),
        ("Data-quality issues", f"{issue_count:,}", COLORS["blue"]),
    ]
    for i, item in enumerate(cards):
        x = 234 + i * 326
        card(draw, (x, 142, x + 292, 260), item[0], item[1], item[2])

    panel(draw, (234, 304, 890, 754), "Documentation completion")
    y = 430
    for row in quality.itertuples(index=False):
        label = "A1c documented" if "A1c" in row.measure else "BP documented"
        draw.text((270, y), label, fill=COLORS["ink"], font=font(18, True))
        draw.rectangle((270, y + 38, 720, y + 72), fill="#E2E8F0")
        draw.rectangle((270, y + 38, 270 + int(450 * row.completion_rate), y + 72), fill=COLORS["green"])
        draw.text((742, y + 35), pct(row.completion_rate), fill=COLORS["ink"], font=font(18, True))
        draw.text((270, y + 86), f"Gap count: {int(row.gap_count)} of {int(row.denominator)}", fill=COLORS["gray"], font=font(15))
        y += 130

    panel(draw, (930, 304, 1556, 754), "Data-quality checks")
    dq = dq.sort_values("issue_count", ascending=True)
    max_count = dq["issue_count"].max()
    y = 500
    for row in dq.itertuples(index=False):
        label = row.check_name.replace(" encounters", "").replace(" among ", ": ")
        if len(label) > 43:
            label = label[:40] + "..."
        draw.text((960, y - 1), label, fill=COLORS["ink"], font=font(15, True))
        draw.rectangle((1264, y + 2, 1460, y + 25), fill="#E2E8F0")
        draw.rectangle((1264, y + 2, 1264 + int(196 * row.issue_count / max_count), y + 25), fill=COLORS["blue"])
        draw.text((1480, y - 1), f"{int(row.issue_count):,}", fill=COLORS["ink"], font=font(15, True))
        y -= 52

    draw.text((960, 570), "Operational review flags", fill=COLORS["ink"], font=font(18, True))
    operational = operational.sort_values("encounter_count", ascending=False)
    max_operational = operational["encounter_count"].max()
    y = 610
    for row in operational.itertuples(index=False):
        label = row.flag_name.replace(" encounters", "")
        if len(label) > 35:
            label = label[:32] + "..."
        draw.text((960, y - 1), label, fill=COLORS["ink"], font=font(13, True))
        draw.rectangle((1264, y + 2, 1460, y + 22), fill="#E2E8F0")
        draw.rectangle((1264, y + 2, 1264 + int(196 * row.encounter_count / max_operational), y + 22), fill=COLORS["amber"])
        draw.text((1480, y - 1), f"{int(row.encounter_count):,}", fill=COLORS["ink"], font=font(13, True))
        y += 35

    draw.text(
        (234, 834),
        "Data basis: quality_measure_summary and data_quality_summary; documentation gaps are kept separate from operational flags.",
        fill=COLORS["gray"],
        font=font(16),
    )
    img.save(ASSETS_DIR / "powerbi-page-2-quality-data.png")


def page_three() -> None:
    features = pd.read_csv(PROCESSED_DIR / "readmission_features.csv")
    feature_proxy = pd.read_csv(PROCESSED_DIR / "feature_importance_proxy.csv")

    img, draw = canvas_with_active(
        "Cohort Profile",
        "Encounter-level profile: demographics, utilization intensity, medication burden, and readmission flags",
        "Cohort",
    )

    # Age distribution
    panel(draw, (234, 142, 626, 390), "Index admissions by age group")
    age_counts = features["age_group"].value_counts().reindex(["18-39", "40-64", "65-79", "80+"], fill_value=0)
    max_age = max(age_counts.max(), 1)
    x = 286
    for age, count in age_counts.items():
        h = int(115 * count / max_age)
        draw.rectangle((x, 336 - h, x + 54, 336), fill=COLORS["purple"])
        draw.text((x - 5, 352), age, fill=COLORS["ink"], font=font(13, True))
        draw.text((x + 6, 312 - h), f"{int(count)}", fill=COLORS["ink"], font=font(12, True))
        x += 75

    # Insurance distribution
    panel(draw, (662, 142, 1054, 390), "Index admissions by insurance")
    ins_counts = features["insurance_type"].value_counts()
    max_ins = max(ins_counts.max(), 1)
    y = 222
    for ins, count in ins_counts.items():
        label = str(ins)
        draw.text((692, y), label, fill=COLORS["ink"], font=font(14, True))
        draw.rectangle((842, y + 4, 1000, y + 27), fill="#E2E8F0")
        draw.rectangle((842, y + 4, 842 + int(158 * count / max_ins), y + 27), fill=COLORS["teal"])
        draw.text((1014, y + 1), f"{int(count)}", fill=COLORS["ink"], font=font(13, True))
        y += 44

    # Feature proxy
    panel(draw, (1090, 142, 1556, 390), "Higher-risk feature groups")
    feature_proxy = feature_proxy.sort_values("readmission_rate", ascending=True)
    max_rate = max(feature_proxy["readmission_rate"].max(), 0.01)
    y = 350
    for row in feature_proxy.itertuples(index=False):
        label = row.feature
        if len(label) > 24:
            label = label[:22] + "..."
        draw.text((1120, y - 2), label, fill=COLORS["ink"], font=font(13, True))
        draw.rectangle((1320, y + 1, 1488, y + 22), fill="#E2E8F0")
        draw.rectangle((1320, y + 1, 1320 + int(168 * row.readmission_rate / max_rate), y + 22), fill=COLORS["amber"])
        draw.text((1502, y - 1), pct(row.readmission_rate), fill=COLORS["ink"], font=font(12, True))
        y -= 34

    # Encounter table mock
    panel(draw, (234, 430, 1556, 770), "Encounter-level sample")
    headers = ["Encounter", "Age", "Service line", "Primary diagnosis", "Risk", "LOS", "Readmit"]
    widths = [140, 90, 180, 270, 110, 80, 90]
    x = 270
    y = 505
    draw.rounded_rectangle((264, 492, 1515, 535), radius=6, fill="#EAF1F7")
    for header, width in zip(headers, widths):
        draw.text((x, 506), header, fill=COLORS["ink"], font=font(13, True))
        x += width
    sample = features.head(5)
    y = 552
    for row in sample.itertuples(index=False):
        x = 270
        values = [
            row.encounter_id,
            row.age_group,
            row.service_line,
            row.primary_diagnosis,
            row.risk_tier,
            f"{row.length_of_stay_days:.1f}",
            "Yes" if row.readmitted_30d == 1 else "No",
        ]
        for value, width in zip(values, widths):
            value = str(value)
            if len(value) > 26:
                value = value[:24] + "..."
            draw.text((x, y), value, fill=COLORS["ink"], font=font(12))
            x += width
        draw.line((264, y + 27, 1515, y + 27), fill=COLORS["line"], width=1)
        y += 39

    draw.text(
        (234, 834),
        "Data basis: readmission_features analytic cohort; feature proxy panel uses feature_importance_proxy.",
        fill=COLORS["gray"],
        font=font(16),
    )
    img.save(ASSETS_DIR / "powerbi-page-3-cohort-profile.png")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    page_one()
    page_two()
    page_three()


if __name__ == "__main__":
    main()
