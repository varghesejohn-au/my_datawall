"""
Aged Care Star Ratings Analysis (National, 2023-2026)
-------------------------------------------------------
Reads 4 years of quarterly Star Ratings data extracts (Department of Health,
Disability and Ageing) and produces three Tableau-ready outputs:

1. star_ratings_trend.csv      - one row per facility per year, 2023-2026
                                  (overall + 4 sub-category star ratings)
2. staffing_quality_detail.csv - one row per facility per year, 2024-2026 only
                                  (real care-minute numbers, quality measure %s,
                                  and a computed "weakest link" sub-rating)
3. re_dimension_detail.csv     - one row per facility PER RESIDENT-EXPERIENCE
                                  DIMENSION per year, 2024-2026 (tidy/long format,
                                  12 dimensions x facilities x years)

NOTE ON COMPLIANCE STANDARDS: the raw data includes 7 individual compliance
"Standard" columns (added in the 2026 extract only), but they are populated
for essentially 1 facility nationally per quarter -- they appear to only
record a value when a specific audit event happened that exact quarter, not
as a persistent status. A standard-by-standard failure analysis was
considered but dropped as unsupportable with this data; we use the
aggregate Compliance star rating instead, which is well populated throughout.

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
        "Overall Star Rating": "overall_stars",
        "Residents' Experience rating": "residents_experience_stars",
        "Compliance rating": "compliance_stars",
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

    # Weakest-link diagnostic: which of the 4 sub-ratings is dragging this
    # facility's overall rating down? Ties broken by column order (RE first).
    sub_ratings = ["residents_experience_stars", "compliance_stars", "staffing_stars", "quality_measures_stars"]
    sub_rating_labels = {
        "residents_experience_stars": "Residents' Experience",
        "compliance_stars": "Compliance",
        "staffing_stars": "Staffing",
        "quality_measures_stars": "Quality Measures",
    }
    valid_mask = df[sub_ratings].notna().any(axis=1)
    df["weakest_link_stars"] = df[sub_ratings].min(axis=1)
    df["weakest_link_category"] = None
    df.loc[valid_mask, "weakest_link_category"] = (
        df.loc[valid_mask, sub_ratings].idxmin(axis=1).map(sub_rating_labels)
    )

    return df


def build_staffing_quality_detail() -> pd.DataFrame:
    frames = []
    for year in DETAIL_YEARS:
        df = load_detail_year(year)
        frames.append(df)
        print(f"[INFO] Detailed data {year}: {len(df)} facilities")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# STEP 2b: RESIDENTS' EXPERIENCE DIMENSION DETAIL (2024-2026, tidy/long format)
# ---------------------------------------------------------------------------
# The raw data has 12 survey dimensions x 4 response levels (Always/Most of
# the time/Some of the time/Never) as 48 separate wide columns. We reshape
# this into long format (one row per facility per dimension) since that's
# far easier to chart in Tableau -- a single bar chart of "dimension" on
# rows, "pct_always" on columns, works directly with no pivoting needed.
#
# Friendly labels below are our own plain-language interpretation of each
# survey dimension's short column name, for readability on charts -- the
# underlying raw dimension name is kept too, for anyone who wants to check
# against the original survey instrument.
RE_DIMENSIONS = {
    "Food": "Food quality",
    "Safety": "Feeling safe",
    "Operation": "Service runs well",
    "Care Need": "Care meets my needs",
    "Competent": "Staff are competent",
    "Independent": "Supports independence",
    "Explain": "Staff explain clearly",
    "Respect": "Treated with respect",
    "Follow Up": "Follows up on concerns",
    "Caring": "Staff are caring",
    "Voice": "I feel heard",
    "Home": "Feels like home",
}


def load_re_dimensions_year(year: int) -> pd.DataFrame:
    cfg = FILES[year]
    df = pd.read_excel(cfg["path"], sheet_name=DETAIL_SHEET, header=0)

    df["Purpose"] = df["Purpose"].map(PURPOSE_MAP).fillna(df["Purpose"])
    df["year"] = year
    df["facility_key"] = _facility_key(df)

    id_cols = {
        "year": "year", "facility_key": "facility_key", "Service Name": "service_name",
        "Purpose": "provider_type", "State/Territory": "state", "Size": "size",
        "Overall Star Rating": "overall_stars",
    }
    base = df[list(id_cols.keys())].rename(columns=id_cols)

    rows = []
    for raw_dim, friendly_dim in RE_DIMENSIONS.items():
        chunk = base.copy()
        chunk["dimension"] = friendly_dim
        chunk["pct_always"] = df[f"[RE] {raw_dim} - Always"]
        chunk["pct_most_of_time"] = df[f"[RE] {raw_dim} - Most of the time"]
        chunk["pct_some_of_time"] = df[f"[RE] {raw_dim} - Some of the time"]
        chunk["pct_never"] = df[f"[RE] {raw_dim} - Never"]
        rows.append(chunk)

    return pd.concat(rows, ignore_index=True)


def build_re_dimension_detail() -> pd.DataFrame:
    frames = []
    for year in DETAIL_YEARS:
        df = load_re_dimensions_year(year)
        frames.append(df)
        print(f"[INFO] RE dimensions {year}: {len(df)} facility-dimension rows")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# STEP 2c: BENCHMARK FACILITIES -- actual performance, not star rating
# ---------------------------------------------------------------------------
# Combines real clinical outcomes (adverse-event %s), staffing minutes, and
# resident-reported experience into one composite z-score, to find facilities
# that are genuinely excelling on the underlying numbers -- as opposed to
# facilities that simply hold a 5-star badge. Restricted to Medium/Large
# facilities only: Small facilities can show 0% falls purely from having very
# few residents, which isn't a reliable signal at that scale.
ADVERSE_MEASURE_COLS = [
    "pct_falls", "pct_pressure_injuries", "pct_restrictive_practices",
    "pct_unplanned_weight_loss", "pct_antipsychotic", "pct_polypharmacy",
]


def build_benchmark_facilities(detail: pd.DataFrame, re_detail: pd.DataFrame, year: int) -> pd.DataFrame:
    latest = detail[detail["year"] == year].copy()
    latest_re = re_detail[re_detail["year"] == year]

    re_avg = latest_re.groupby("facility_key")["pct_always"].mean().rename("re_avg_always_pct")
    df = latest.merge(re_avg, on="facility_key", how="left")

    df = df[df["size"].isin(["Medium", "Large"])].copy()
    df = df.dropna(subset=ADVERSE_MEASURE_COLS + ["re_avg_always_pct", "rn_minutes_actual"])

    for c in ADVERSE_MEASURE_COLS:
        # Negated: lower adverse-event % is better, so a lower raw value should
        # produce a HIGHER (better) z-score contribution
        df[c + "_z"] = -(df[c] - df[c].mean()) / df[c].std()
    df["staffing_z"] = (df["rn_minutes_actual"] - df["rn_minutes_actual"].mean()) / df["rn_minutes_actual"].std()
    df["re_z"] = (df["re_avg_always_pct"] - df["re_avg_always_pct"].mean()) / df["re_avg_always_pct"].std()

    z_cols = [c + "_z" for c in ADVERSE_MEASURE_COLS] + ["staffing_z", "re_z"]
    df["composite_score"] = df[z_cols].mean(axis=1)

    keep = [
        "facility_key", "service_name", "provider_name", "state", "provider_type", "size",
        "overall_stars", "compliance_stars", "staffing_stars", "quality_measures_stars",
        "pct_falls", "pct_pressure_injuries", "pct_restrictive_practices",
        "rn_minutes_actual", "total_care_minutes_actual", "re_avg_always_pct", "composite_score",
    ]
    return df[keep].sort_values("composite_score", ascending=False)


# ---------------------------------------------------------------------------
# STEP 4: AUDIT & QUALITY INTELLIGENCE
# ---------------------------------------------------------------------------
# A deeper pass, built after cross-checking against an independent parallel
# analysis of the same source data. Where a claim from that analysis was
# checked against our own pipeline and confirmed, we adopt it; where our
# numbers came out meaningfully different (see the QM matched-trend finding
# below), we report our own verified number instead.

def build_matched_trend(trend: pd.DataFrame, year_a: int, year_b: int) -> pd.DataFrame:
    """
    Restricts to facilities present in BOTH years before computing average
    change -- a fairer trend measure than comparing raw yearly national
    averages, since the raw averages mix in facilities entering/exiting the
    sector between years.
    """
    cols = ["overall_stars", "residents_experience_stars", "compliance_stars",
            "staffing_stars", "quality_measures_stars"]
    da = trend[trend["year"] == year_a][["facility_key"] + cols].add_suffix(f"_{year_a}")
    da = da.rename(columns={f"facility_key_{year_a}": "facility_key"})
    db = trend[trend["year"] == year_b][["facility_key"] + cols].add_suffix(f"_{year_b}")
    db = db.rename(columns={f"facility_key_{year_b}": "facility_key"})
    matched = da.merge(db, on="facility_key", how="inner")

    rows = []
    for col in cols:
        ca, cb = f"{col}_{year_a}", f"{col}_{year_b}"
        pair = matched[[ca, cb]].dropna()
        rows.append({
            "sub_rating": col,
            f"mean_{year_a}": pair[ca].mean(),
            f"mean_{year_b}": pair[cb].mean(),
            "mean_change": (pair[cb] - pair[ca]).mean(),
            "n_matched": len(pair),
        })
    return pd.DataFrame(rows), matched


def _outcome_composite(detail_year_df: pd.DataFrame) -> pd.Series:
    """
    A pure CLINICAL outcome composite -- adverse-event measures only, no
    staffing or resident-experience mixed in. Kept separate from staffing/RE
    deliberately, since this composite is used to test whether staffing/
    rating/compliance PREDICT outcomes -- mixing them into the outcome
    measure itself would make that test circular.
    """
    df = detail_year_df.dropna(subset=ADVERSE_MEASURE_COLS).copy()
    for c in ADVERSE_MEASURE_COLS:
        df[c + "_z"] = -(df[c] - df[c].mean()) / df[c].std()
    return df[[c + "_z" for c in ADVERSE_MEASURE_COLS]].mean(axis=1)


def eta_squared(values: pd.Series, groups: pd.Series) -> float:
    """
    Standard one-way ANOVA effect size: what fraction of total variance in
    `values` is explained by group membership? 0 = group tells you nothing,
    1 = group perfectly determines the value.
    """
    d = pd.DataFrame({"v": values, "g": groups}).dropna()
    grand_mean = d["v"].mean()
    ss_total = ((d["v"] - grand_mean) ** 2).sum()
    ss_between = d.groupby("g")["v"].apply(lambda x: len(x) * (x.mean() - grand_mean) ** 2).sum()
    return ss_between / ss_total if ss_total > 0 else np.nan


def build_rating_vs_outcome_residuals(detail: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Regresses the clinical outcome composite against the official overall
    star rating, then flags facilities whose actual outcome diverges
    substantially from what their rating alone would predict -- i.e. where
    the badge and the underlying numbers disagree.
    """
    latest = detail[detail["year"] == year].copy()
    latest["outcome_composite"] = np.nan
    valid_idx = latest.dropna(subset=ADVERSE_MEASURE_COLS).index
    latest.loc[valid_idx, "outcome_composite"] = _outcome_composite(latest.loc[valid_idx])

    d = latest.dropna(subset=["outcome_composite", "overall_stars"]).copy()
    x = d["overall_stars"].values
    y = d["outcome_composite"].values
    slope, intercept = np.polyfit(x, y, 1)
    d["predicted_outcome"] = slope * x + intercept
    d["residual"] = d["outcome_composite"] - d["predicted_outcome"]

    resid_std = d["residual"].std()
    d["rating_classification"] = "Aligned"
    d.loc[d["residual"] > resid_std, "rating_classification"] = "Potentially under-rated"
    d.loc[d["residual"] < -resid_std, "rating_classification"] = "Potentially over-rated"
    d["is_statistical_outlier"] = d["residual"].abs() > 3 * resid_std

    return d[["facility_key", "service_name", "state", "provider_type", "size",
              "overall_stars", "outcome_composite", "predicted_outcome", "residual",
              "rating_classification", "is_statistical_outlier"]]


def build_risk_flags(detail: pd.DataFrame, re_detail: pd.DataFrame, year: int, prior_year: int) -> pd.DataFrame:
    """
    Facility-level audit flags. Thresholds are our own explicit choices
    (documented here and in the README), not inherited from any external
    source:
    - persistent_food_failure: bottom-quartile Food score in BOTH this year
      and the prior year (requires two consecutive low scores, not one)
    - high_compliance_dignity_gap: Compliance = 5 stars but bottom-quartile
      resident-reported dignity (avg of Respect/Feel Heard/Feels Like Home)
    - adequately_staffed_poor_outcomes: met RN care-minute target AND
      Quality Measures rating of 1-2 stars
    - understaffed_good_outcomes: missed RN care-minute target AND
      Quality Measures rating of 4-5 stars
    - five_star_low_qm: Overall = 5 stars but Quality Measures <= 2 stars
      (the most direct, named "badge disagrees with clinical data" case)
    """
    latest = detail[detail["year"] == year].copy()

    food_this = re_detail[(re_detail["year"] == year) & (re_detail["dimension"] == "Food quality")]
    food_prior = re_detail[(re_detail["year"] == prior_year) & (re_detail["dimension"] == "Food quality")]
    food_this_q1 = food_this["pct_always"].quantile(0.25)
    food_prior_q1 = food_prior["pct_always"].quantile(0.25)
    low_food_this = set(food_this[food_this["pct_always"] <= food_this_q1]["facility_key"])
    low_food_prior = set(food_prior[food_prior["pct_always"] <= food_prior_q1]["facility_key"])
    persistent_food_failure_keys = low_food_this & low_food_prior

    dignity = re_detail[(re_detail["year"] == year) & (re_detail["dimension"].isin(
        ["Treated with respect", "I feel heard", "Feels like home"]))]
    dignity_avg = dignity.groupby("facility_key")["pct_always"].mean()
    dignity_q1 = dignity_avg.quantile(0.25)
    low_dignity_keys = set(dignity_avg[dignity_avg <= dignity_q1].index)

    latest["persistent_food_failure"] = latest["facility_key"].isin(persistent_food_failure_keys)
    latest["high_compliance_dignity_gap"] = (
        (latest["compliance_stars"] == 5) & latest["facility_key"].isin(low_dignity_keys)
    )
    latest["adequately_staffed_poor_outcomes"] = (
        latest["met_rn_target"] & latest["quality_measures_stars"].isin([1, 2])
    )
    latest["understaffed_good_outcomes"] = (
        (~latest["met_rn_target"]) & latest["quality_measures_stars"].isin([4, 5])
    )
    latest["five_star_low_qm"] = (
        (latest["overall_stars"] == 5) & (latest["quality_measures_stars"] <= 2)
    )

    flag_cols = ["persistent_food_failure", "high_compliance_dignity_gap",
                 "adequately_staffed_poor_outcomes", "understaffed_good_outcomes", "five_star_low_qm"]
    return latest[["facility_key", "service_name", "state", "provider_type", "size",
                    "overall_stars", "quality_measures_stars", "compliance_stars"] + flag_cols]


def build_state_rank_divergence(detail: pd.DataFrame, year: int) -> pd.DataFrame:
    latest = detail[detail["year"] == year].copy()
    official = latest.groupby("state")["overall_stars"].mean()

    outcome_df = latest.dropna(subset=ADVERSE_MEASURE_COLS).copy()
    outcome_df["outcome_composite"] = _outcome_composite(outcome_df)
    outcome = outcome_df.groupby("state")["outcome_composite"].mean()

    result = pd.DataFrame({
        "mean_overall_stars": official,
        "official_rank": official.rank(ascending=False),
        "outcome_composite": outcome,
        "outcome_rank": outcome.rank(ascending=False),
    })
    result["rank_divergence"] = result["official_rank"] - result["outcome_rank"]  # positive = under-rated
    return result.sort_values("official_rank")


def build_hidden_champions(residuals: pd.DataFrame, detail: pd.DataFrame, year: int) -> pd.DataFrame:
    """3-star (or below) facilities sitting in the top quartile of actual outcomes."""
    d = residuals[residuals["size"].isin(["Medium", "Large"])]
    q75 = d["outcome_composite"].quantile(0.75)
    champions = d[(d["overall_stars"] <= 3) & (d["outcome_composite"] >= q75)]
    return champions.sort_values("outcome_composite", ascending=False)


# ---------------------------------------------------------------------------
# STEP 3: SUMMARY STATS
# ---------------------------------------------------------------------------
def print_summary(trend: pd.DataFrame, detail: pd.DataFrame, re_detail: pd.DataFrame):
    print("\n=== Facility count by year (sector consolidation check) ===")
    print(trend.groupby("year")["facility_key"].nunique())

    print("\n=== Mean overall star rating by year ===")
    print(trend.groupby("year")["overall_stars"].mean().round(2))

    print("\n=== Mean overall star rating by provider type, latest year ===")
    latest = trend[trend["year"] == trend["year"].max()]
    print(latest.groupby("provider_type")["overall_stars"].mean().round(2))

    print("\n=== Staffing target met rate by year ===")
    print(detail.groupby("year")[["met_rn_target", "met_total_care_target"]].mean().round(3))

    latest_detail = detail[detail["year"] == detail["year"].max()]

    print("\n=== Correlation: RN minutes gap vs quality measures star rating ===")
    d1 = latest_detail.dropna(subset=["rn_minutes_gap", "quality_measures_stars"])
    print(f"Correlation coefficient: {d1['rn_minutes_gap'].corr(d1['quality_measures_stars']):.3f}")

    print("\n=== Correlation: total care minutes gap vs falls % ===")
    d2 = latest_detail.dropna(subset=["total_care_minutes_gap", "pct_falls"])
    print(f"Correlation coefficient: {d2['total_care_minutes_gap'].corr(d2['pct_falls']):.3f}")

    print("\n=== ANGLE 5: Correlation: Compliance star rating vs quality outcomes ===")
    d3 = latest_detail.dropna(subset=["compliance_stars", "quality_measures_stars"])
    print(f"Compliance stars vs Quality Measures stars: {d3['compliance_stars'].corr(d3['quality_measures_stars']):.3f}")
    d4 = latest_detail.dropna(subset=["compliance_stars", "pct_falls"])
    print(f"Compliance stars vs falls %: {d4['compliance_stars'].corr(d4['pct_falls']):.3f}")

    print("\n=== ANGLE 1: Weakest-link sub-rating distribution, latest year ===")
    print(latest_detail["weakest_link_category"].value_counts(normalize=True).round(3))
    print("\n--- Weakest link, facilities with overall 3 stars or below only ---")
    low_rated = latest_detail[latest_detail["overall_stars"] <= 3]
    print(low_rated["weakest_link_category"].value_counts(normalize=True).round(3))

    print("\n=== ANGLE 3: Resident Experience dimension ranking (mean % Always), latest year ===")
    latest_re = re_detail[re_detail["year"] == re_detail["year"].max()]
    dim_rank = latest_re.groupby("dimension")["pct_always"].mean().sort_values().round(1)
    print(dim_rank)

    print("\n=== ANGLE 2: Compliance star rating vs 'Respect'/'Voice'/'Home' resident survey ===")
    dignity_dims = latest_re[latest_re["dimension"].isin(
        ["Treated with respect", "I feel heard", "Feels like home"]
    )]
    dignity_avg = dignity_dims.groupby("facility_key")["pct_always"].mean().rename("dignity_pct_always")
    compliance = latest_detail.groupby("facility_key")["compliance_stars"].mean()
    merged = pd.concat([dignity_avg, compliance], axis=1).dropna()
    print(f"Correlation, compliance stars vs resident-reported dignity measures: {merged['dignity_pct_always'].corr(merged['compliance_stars']):.3f}")
    print(f"n = {len(merged)} facilities")

    print("\n=== Star-rating discriminating power (std dev) - which sub-ratings actually differ facility to facility? ===")
    for col in ["residents_experience_stars", "compliance_stars", "staffing_stars", "quality_measures_stars", "overall_stars"]:
        print(f"{col}: std={latest_detail[col].std():.2f}, distribution={latest_detail[col].value_counts(normalize=True).sort_index().round(3).to_dict()}")

    print("\n=== Sanity check: does the QM star reflect its own underlying measures? ===")
    print(f"QM star vs falls %: {latest_detail['quality_measures_stars'].corr(latest_detail['pct_falls']):.3f}")
    print(f"QM star vs pressure injuries %: {latest_detail['quality_measures_stars'].corr(latest_detail['pct_pressure_injuries']):.3f}")
    print(f"QM star vs restrictive practices %: {latest_detail['quality_measures_stars'].corr(latest_detail['pct_restrictive_practices']):.3f}")

    print("\n" + "="*70)
    print("AUDIT & QUALITY INTELLIGENCE (Step 4)")
    print("="*70)

    print("\n=== Matched-facility trend, 2024->2026 (fairer than raw yearly averages) ===")
    matched_summary, _ = build_matched_trend(trend, 2024, 2026)
    print(matched_summary.round(3).to_string(index=False))

    print("\n=== Provider type effect size (eta-squared): rating vs actual outcome ===")
    d5 = latest_detail.dropna(subset=ADVERSE_MEASURE_COLS)
    outcome_composite_latest = _outcome_composite(d5)
    eta_rating = eta_squared(latest_detail["overall_stars"], latest_detail["provider_type"])
    eta_outcome = eta_squared(outcome_composite_latest, d5["provider_type"])
    print(f"Provider type effect on official rating (eta^2): {eta_rating:.3f}")
    print(f"Provider type effect on actual outcome (eta^2): {eta_outcome:.3f}")

    print("\n=== Rating vs outcome residual classification, 2026 ===")
    residuals = build_rating_vs_outcome_residuals(detail, 2026)
    print(residuals["rating_classification"].value_counts(normalize=True).round(3))
    print(f"Statistical outliers (|residual| > 3 std): {residuals['is_statistical_outlier'].sum()}")

    print("\n=== Risk flags, 2026 (vs 2025 for the persistent-food-failure check) ===")
    flags = build_risk_flags(detail, re_detail, 2026, 2025)
    for col in ["persistent_food_failure", "high_compliance_dignity_gap",
                "adequately_staffed_poor_outcomes", "understaffed_good_outcomes", "five_star_low_qm"]:
        n = flags[col].sum()
        print(f"{col}: {n} facilities ({n/len(flags)*100:.1f}%)")

    print("\n=== State rank divergence: official rating rank vs actual outcome rank ===")
    state_div = build_state_rank_divergence(detail, 2026)
    print(state_div.round(3))

    print("\n=== Hidden Champions: <=3 star facilities in top quartile of actual outcomes ===")
    champions = build_hidden_champions(residuals, detail, 2026)
    print(f"Count: {len(champions)}")
    print(champions.head(10)[["service_name", "state", "overall_stars", "outcome_composite"]].to_string(index=False))

    print("\n=== Staffing vs specific quality measures (not just aggregate QM star) ===")
    d6 = latest_detail.dropna(subset=["rn_minutes_actual", "pct_falls", "pct_polypharmacy", "pct_antipsychotic"])
    print(f"RN minutes vs falls %: {d6['rn_minutes_actual'].corr(d6['pct_falls']):.3f}")
    print(f"RN minutes vs polypharmacy %: {d6['rn_minutes_actual'].corr(d6['pct_polypharmacy']):.3f}")
    print(f"RN minutes vs antipsychotic %: {d6['rn_minutes_actual'].corr(d6['pct_antipsychotic']):.3f}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    trend = build_star_ratings_trend()
    detail = build_staffing_quality_detail()
    re_detail = build_re_dimension_detail()

    print_summary(trend, detail, re_detail)

    benchmark = build_benchmark_facilities(detail, re_detail, year=2026)
    print("\n=== Top 10 facilities nationally by actual composite performance ===")
    print(benchmark.head(10)[["service_name", "state", "provider_type", "overall_stars", "composite_score"]].to_string(index=False))
    print("\n=== Overall star rating distribution among the top 20 actual performers ===")
    print(benchmark.head(20)["overall_stars"].value_counts(dropna=False))

    trend_path = OUTPUT_DIR / "star_ratings_trend.csv"
    detail_path = OUTPUT_DIR / "staffing_quality_detail.csv"
    re_path = OUTPUT_DIR / "re_dimension_detail.csv"
    benchmark_path = OUTPUT_DIR / "benchmark_facilities.csv"
    trend.to_csv(trend_path, index=False)
    detail.to_csv(detail_path, index=False)
    re_detail.to_csv(re_path, index=False)
    benchmark.to_csv(benchmark_path, index=False)
    print(f"\nSaved: {trend_path}")
    print(f"Saved: {detail_path}")
    print(f"Saved: {re_path}")
    print(f"Saved: {benchmark_path}")

    # --- Audit & Quality Intelligence outputs ---
    matched_summary, _ = build_matched_trend(trend, 2024, 2026)
    residuals = build_rating_vs_outcome_residuals(detail, 2026)
    flags = build_risk_flags(detail, re_detail, 2026, 2025)
    state_div = build_state_rank_divergence(detail, 2026)
    champions = build_hidden_champions(residuals, detail, 2026)

    # Merge residuals + risk flags into one facility-level audit file --
    # single rich data source for the Tableau audit dashboard
    audit = residuals.merge(
        flags.drop(columns=["service_name", "state", "provider_type", "size", "overall_stars"]),
        on="facility_key", how="left"
    )
    audit["is_hidden_champion"] = audit["facility_key"].isin(champions["facility_key"])

    matched_trend_path = OUTPUT_DIR / "matched_trend.csv"
    audit_path = OUTPUT_DIR / "facility_audit_intelligence.csv"
    state_div_path = OUTPUT_DIR / "state_rank_divergence.csv"

    matched_summary.to_csv(matched_trend_path, index=False)
    audit.to_csv(audit_path, index=False)
    state_div.to_csv(state_div_path, index=True)

    print(f"Saved: {matched_trend_path}")
    print(f"Saved: {audit_path}")
    print(f"Saved: {state_div_path}")
