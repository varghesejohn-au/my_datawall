"""
Aged Care Star Ratings Analysis (National, 2023-2026)
-------------------------------------------------------
Reads 4 years of quarterly Star Ratings data extracts (Department of Health,
Disability and Ageing) and produces two Tableau-ready outputs:

1. star_ratings_trend.csv   - one row per facility per year, 2023-2026
                               (overall + 4 sub-category star ratings)
2. staffing_quality_detail.csv - one row per facility per year, 2024-2026 only
                               (real care-minute numbers + quality measure %s,
                               since the "Detailed data" sheet doesn't exist
                               in the 2023 extract)

WHY THIS STRUCTURE:
Government data changes shape release to release -- column labels get
re-cased, categories get renamed, new columns get added. Each loader function
below handles one year's quirks explicitly so the reasoning is inspectable,
not hidden inside a generic "clean everything" function.

HOW TO USE:
1. Files already in data/raw/: star-ratings-2023/2024/2025/2026.xlsx
2. Run: python analysis.py
3. Outputs land in output/
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

FILES = {
    2023: {"path": DATA_DIR / "star-ratings-2023.xlsx", "sheet": "Star-Ratings_Q2_FY2022-23"},
    2024: {"path": DATA_DIR / "star-ratings-2024.xlsx", "sheet": "Star Ratings"},
    2025: {"path": DATA_DIR / "star-ratings-2025.xlsx", "sheet": "Star Ratings"},
    2026: {"path": DATA_DIR / "star-ratings-2026.xlsx", "sheet": "Star Ratings"},
}
DETAIL_SHEET = "Detailed data"
DETAIL_YEARS = [2024, 2025, 2026]  # 2023 extract has no Detailed data sheet

# Normalises inconsistent labelling across release years onto one standard set
PURPOSE_MAP = {
    "Not for profit": "Not for Profit",
    "Not for Profit": "Not for Profit",
    "For profit": "Private for Profit",
    "For Profit": "Private for Profit",
    "Private for Profit": "Private for Profit",
    "Government": "Government",
}


def _facility_key(df: pd.DataFrame) -> pd.Series:
    """
    Builds a best-available facility identifier. There's no stable ID column
    in this data, so Service Name + Provider Name is the closest proxy --
    imperfect if a facility renames or changes owner between quarters
    (noted as a limitation in the README).
    """
    return (df["Service Name"].str.strip() + " | " + df["Provider Name"].str.strip())


# ---------------------------------------------------------------------------
# STEP 1: STAR RATINGS TREND (2023-2026)
# ---------------------------------------------------------------------------
def load_star_ratings_year(year: int) -> pd.DataFrame:
    cfg = FILES[year]
    df = pd.read_excel(cfg["path"], sheet_name=cfg["sheet"], header=0)

    df["Purpose"] = df["Purpose"].map(PURPOSE_MAP).fillna(df["Purpose"])

    if "Service Suburb" not in df.columns:
        df["Service Suburb"] = np.nan  # not present in the 2023 extract

    df["year"] = year
    df["facility_key"] = _facility_key(df)

    keep = [
        "year", "facility_key", "Service Name", "Provider Name", "Service Suburb",
        "Purpose", "State/Territory", "Aged Care Planning Region", "MMM Region", "Size",
        "Overall Star Rating", "Residents' Experience rating", "Compliance rating",
        "Staffing rating", "Quality Measures rating",
    ]
    df = df[keep].rename(columns={
        "Service Name": "service_name",
        "Provider Name": "provider_name",
        "Service Suburb": "service_suburb",
        "Purpose": "provider_type",
        "State/Territory": "state",
        "Aged Care Planning Region": "planning_region",
        "MMM Region": "remoteness",
        "Size": "size",
        "Overall Star Rating": "overall_stars",
        "Residents' Experience rating": "residents_experience_stars",
        "Compliance rating": "compliance_stars",
        "Staffing rating": "staffing_stars",
        "Quality Measures rating": "quality_measures_stars",
    })
    return df


def build_star_ratings_trend() -> pd.DataFrame:
    frames = []
    for year in FILES:
        df = load_star_ratings_year(year)
        frames.append(df)
        print(f"[INFO] Star Ratings {year}: {len(df)} facilities")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# STEP 2: STAFFING MINUTES + QUALITY MEASURES DETAIL (2024-2026)
# ---------------------------------------------------------------------------
def load_detail_year(year: int) -> pd.DataFrame:
    cfg = FILES[year]
    df = pd.read_excel(cfg["path"], sheet_name=DETAIL_SHEET, header=0)

    # 2024 calls it "[QM] Physical restraint"; 2025/2026 call it
    # "[QM] Restrictive practices" -- same measure, renamed.
    df = df.rename(columns={"[QM] Physical restraint": "[QM] Restrictive practices"})

    df["Purpose"] = df["Purpose"].map(PURPOSE_MAP).fillna(df["Purpose"])
    df["year"] = year
    df["facility_key"] = _facility_key(df)

    keep = {
        "year": "year",
        "facility_key": "facility_key",
        "Service Name": "service_name",
        "Provider Name": "provider_name",
        "Service Suburb": "service_suburb",
        "Purpose": "provider_type",
        "State/Territory": "state",
        "Size": "size",
        "Staffing rating": "staffing_stars",
        "[S] Registered Nurse Care Minutes - Target": "rn_minutes_target",
        "[S] Registered Nurse Care Minutes - Actual": "rn_minutes_actual",
        "[S] Total Care Minutes - Target": "total_care_minutes_target",
        "[S] Total Care Minutes - Actual": "total_care_minutes_actual",
        "Quality Measures rating": "quality_measures_stars",
        "[QM] Pressure injuries*": "pct_pressure_injuries",
        "[QM] Restrictive practices": "pct_restrictive_practices",
        "[QM] Unplanned weight loss*": "pct_unplanned_weight_loss",
        "[QM] Falls and major injury - falls*": "pct_falls",
        "[QM] Falls and major injury - major injury from a fall*": "pct_falls_major_injury",
        "[QM] Medication management - polypharmacy": "pct_polypharmacy",
        "[QM] Medication management - antipsychotic": "pct_antipsychotic",
    }
    df = df[list(keep.keys())].rename(columns=keep)

    df["rn_minutes_gap"] = df["rn_minutes_actual"] - df["rn_minutes_target"]
    df["total_care_minutes_gap"] = df["total_care_minutes_actual"] - df["total_care_minutes_target"]
    df["met_rn_target"] = df["rn_minutes_gap"] >= 0
    df["met_total_care_target"] = df["total_care_minutes_gap"] >= 0

    return df


def build_staffing_quality_detail() -> pd.DataFrame:
    frames = []
    for year in DETAIL_YEARS:
        df = load_detail_year(year)
        frames.append(df)
        print(f"[INFO] Detailed data {year}: {len(df)} facilities")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# STEP 3: SUMMARY STATS
# ---------------------------------------------------------------------------
def print_summary(trend: pd.DataFrame, detail: pd.DataFrame):
    print("\n=== Facility count by year (sector consolidation check) ===")
    print(trend.groupby("year")["facility_key"].nunique())

    print("\n=== Mean overall star rating by year ===")
    print(trend.groupby("year")["overall_stars"].mean().round(2))

    print("\n=== Mean overall star rating by provider type, latest year ===")
    latest = trend[trend["year"] == trend["year"].max()]
    print(latest.groupby("provider_type")["overall_stars"].mean().round(2))

    print("\n=== Staffing target met rate by year ===")
    print(detail.groupby("year")[["met_rn_target", "met_total_care_target"]].mean().round(3))

    print("\n=== Correlation: RN minutes gap vs quality measures star rating ===")
    latest_detail = detail[detail["year"] == detail["year"].max()].dropna(
        subset=["rn_minutes_gap", "quality_measures_stars"]
    )
    corr = latest_detail["rn_minutes_gap"].corr(latest_detail["quality_measures_stars"])
    print(f"Correlation coefficient: {corr:.3f}")

    print("\n=== Correlation: total care minutes gap vs falls % ===")
    corr2 = latest_detail["total_care_minutes_gap"].corr(latest_detail["pct_falls"])
    print(f"Correlation coefficient: {corr2:.3f}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    trend = build_star_ratings_trend()
    detail = build_staffing_quality_detail()

    print_summary(trend, detail)

    trend_path = OUTPUT_DIR / "star_ratings_trend.csv"
    detail_path = OUTPUT_DIR / "staffing_quality_detail.csv"
    trend.to_csv(trend_path, index=False)
    detail.to_csv(detail_path, index=False)
    print(f"\nSaved: {trend_path}")
    print(f"Saved: {detail_path}")
