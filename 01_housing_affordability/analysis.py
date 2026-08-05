"""
Sydney vs Regional NSW Housing Affordability Analysis
------------------------------------------------------
Reads raw rent/sales data (DCJ Rent and Sales Report) and income data (ABS),
merges them, computes affordability ratios, and exports a clean CSV for Tableau.

WHY THIS STRUCTURE:
- Real government data is messy (inconsistent LGA names, merged header rows,
  footnote rows at the bottom). This script is written so each cleaning step
  is a separate, named function -- when an interviewer asks "why did you do X",
  you can point to the exact function and explain the reasoning.

HOW TO USE:
1. Put your downloaded files in data/raw/
     - rent_sales_raw.xlsx   (from DCJ Rent and Sales Report)
     - income_raw.xlsx       (from ABS)
2. Update the COLUMN MAPPING section below to match your actual file's column
   names (government exports vary — this is normal, not a sign you did
   something wrong).
3. Run: python analysis.py
4. Output lands in output/affordability_clean.csv

NOTE: This script currently runs on SYNTHETIC sample data (see
generate_sample_data()) so you can test the whole pipeline immediately,
before your real downloads are ready. Once you have real files, switch
USE_SAMPLE_DATA to False.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
USE_SAMPLE_DATA = False   # real DCJ rent + sales files are in; income is still pending

DATA_DIR = Path("data/raw")
RENT_FILE = DATA_DIR / "rent-tables-march-2026-quarter.xlsx"
SALES_FILE = DATA_DIR / "sales-tables-december-2025-quarter.xlsx"
INCOME_FILE = DATA_DIR / "2021Census_G02_NSW_LGA.csv"
GEOG_LOOKUP_FILE = DATA_DIR / "2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

RENTAL_STRESS_THRESHOLD = 0.30   # 30% of income on rent = rental stress
PRICE_INCOME_SEVERE = 6.0        # price-to-income ratio > 6 = severely unaffordable


# ---------------------------------------------------------------------------
# STEP 1: LOAD DATA
# ---------------------------------------------------------------------------
def generate_sample_data():
    """
    Creates realistic-looking sample data so the pipeline can be tested
    end-to-end before real government files are downloaded.
    Replace this with real load_real_data() once files are in data/raw/.
    """
    np.random.seed(42)
    years = list(range(2015, 2026))
    regions = {
        "Greater Sydney": ["Sydney City", "Parramatta", "Blacktown", "Sutherland", "Penrith"],
        "Regional NSW": ["Wollongong", "Newcastle", "Wagga Wagga", "Orange", "Coffs Harbour"],
    }

    rows = []
    for group, lgas in regions.items():
        base_price = 950000 if group == "Greater Sydney" else 550000
        base_rent = 650 if group == "Greater Sydney" else 420
        base_income = 105000 if group == "Greater Sydney" else 82000
        for lga in lgas:
            price = base_price * np.random.uniform(0.85, 1.15)
            rent = base_rent * np.random.uniform(0.85, 1.15)
            income = base_income * np.random.uniform(0.9, 1.1)
            for year in years:
                growth = 1 + 0.045 * (year - 2015) if group == "Greater Sydney" else 1 + 0.06 * (year - 2015)
                income_growth = 1 + 0.025 * (year - 2015)
                rows.append({
                    "year": year,
                    "region_group": group,
                    "lga": lga,
                    "median_sale_price": round(price * growth, 0),
                    "median_weekly_rent": round(rent * growth, 0),
                    "median_household_income": round(income * income_growth, 0),
                })
    return pd.DataFrame(rows)


def _region_group(series: pd.Series) -> pd.Series:
    """Maps the DCJ 'Greater Sydney' column to a 2-way Sydney vs Regional split."""
    return series.map({
        "Greater Sydney": "Greater Sydney",
        "Rest of GMR": "Regional NSW",     # e.g. Wollongong, Newcastle
        "Rest of State": "Regional NSW",
    })


def load_rent_data() -> pd.DataFrame:
    """
    Loads the DCJ Rent and Sales Report - LGA sheet (rent tables).
    Filters down to the LGA-level 'Total' row (all dwelling types, all
    bedroom counts) so we get one clean median rent per LGA.
    """
    rent = pd.read_excel(RENT_FILE, sheet_name="LGA", header=8)

    mask = (
        (rent["Dwelling Types"] == "Total")
        & (rent["Number of Bedrooms"] == "Total")
        & (rent["Greater Metropolitan Region (GMR)"] == "Total")
        & (rent["Rings"] == "Total")
        & (rent["Greater Sydney"].isin(["Greater Sydney", "Rest of GMR", "Rest of State"]))
        & (rent["Local Government Area (LGA)"] != "Total")
    )
    rent = rent.loc[mask].copy()

    rent["region_group"] = _region_group(rent["Greater Sydney"])
    rent = rent.rename(columns={
        "Local Government Area (LGA)": "lga",
        "Median Weekly Rent for New Bonds\n$": "median_weekly_rent",
    })

    # Some LGAs are suppressed for confidentiality (marked "s" or "-") - drop those
    rent["median_weekly_rent"] = pd.to_numeric(rent["median_weekly_rent"], errors="coerce")

    return rent[["lga", "region_group", "median_weekly_rent"]].dropna()


def load_sales_data() -> pd.DataFrame:
    """
    Loads the DCJ Rent and Sales Report - LGA sheet (sales tables).
    Prices are reported in $'000s in the source file, so we convert to dollars.
    """
    sales = pd.read_excel(SALES_FILE, sheet_name="LGA", header=6)

    mask = (
        (sales["DwellingType"] == "Total")
        & (sales["Greater Metropolitan Region (GMR)"] == "Total")
        & (sales["Rings"] == "Total")
        & (sales["Greater Sydney"].isin(["Greater Sydney", "Rest of GMR", "Rest of State"]))
        & (sales["Local Government Area (LGA)"] != "Total")
    )
    sales = sales.loc[mask].copy()

    sales["region_group"] = _region_group(sales["Greater Sydney"])
    sales = sales.rename(columns={
        "Local Government Area (LGA)": "lga",
        "Median Sales Price\n$'000s": "median_sale_price_000s",
    })

    sales["median_sale_price_000s"] = pd.to_numeric(sales["median_sale_price_000s"], errors="coerce")
    sales["median_sale_price"] = sales["median_sale_price_000s"] * 1000

    return sales[["lga", "region_group", "median_sale_price"]].dropna()


def load_income_data() -> pd.DataFrame:
    """
    Loads LGA-level median household income from the ABS Census 2021
    DataPack, Table G02, joined to LGA names via the geography metadata file
    (G02 only has LGA codes like 'LGA10050', not names).
    """
    if not INCOME_FILE.exists() or not GEOG_LOOKUP_FILE.exists():
        raise FileNotFoundError(
            f"Income data not found. Expected {INCOME_FILE.name} and "
            f"{GEOG_LOOKUP_FILE.name} in data/raw/."
        )

    income = pd.read_csv(INCOME_FILE)

    geog = pd.read_excel(GEOG_LOOKUP_FILE, sheet_name="2021_ASGS_Non_ABS_Structures")
    geog = geog[geog["ASGS_Structure"] == "LGA"][["Census_Code_2021", "Census_Name_2021"]]

    income = income.merge(
        geog, left_on="LGA_CODE_2021", right_on="Census_Code_2021", how="left"
    )

    # A handful of LGAs were renamed or amalgamated after the 2021 Census, so
    # the current DCJ rent/sales report uses a different name than the
    # Census DataPack. Known cases, checked manually:
    #   - Dubbo Regional Council renamed itself "Western Plains Regional" (2024)
    #   - "Nambucca" is shortened from the Census's "Nambucca Valley"
    #   - Cootamundra-Gundagai Regional still gets reported by DCJ split into
    #     its pre-amalgamation "Gundagai" component -- income mapped at the
    #     combined-LGA level as the closest available proxy (caveat noted in README)
    NAME_OVERRIDES = {
        "Dubbo Regional": "Western Plains Regional",
        "Nambucca Valley": "Nambucca",
        "Cootamundra-Gundagai Regional": "Gundagai",
    }
    income["lga"] = income["Census_Name_2021"].str.replace(r"\s*\(NSW\)", "", regex=True).str.strip()
    income["lga"] = income["lga"].replace(NAME_OVERRIDES)

    income["median_household_income"] = income["Median_tot_hhd_inc_weekly"] * 52

    return income[["lga", "median_household_income"]].dropna()


def load_real_data() -> pd.DataFrame:
    rent = load_rent_data()
    sales = load_sales_data()

    df = pd.merge(rent, sales[["lga", "median_sale_price"]], on="lga", how="inner")

    try:
        income = load_income_data()
        df["_merge_key"] = df["lga"].str.lower()
        income["_merge_key"] = income["lga"].str.lower()
        df = pd.merge(df, income[["_merge_key", "median_household_income"]], on="_merge_key", how="left")
        df = df.drop(columns="_merge_key")
    except FileNotFoundError as e:
        print(f"[WARNING] {e}")
        print("Continuing without income data -- affordability ratios will be skipped.\n")
        df["median_household_income"] = np.nan

    df["year"] = 2026  # single-quarter snapshot; update if multiple quarters are merged later
    return df


# ---------------------------------------------------------------------------
# STEP 2: CLEAN
# ---------------------------------------------------------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["median_sale_price", "median_weekly_rent"])
    df["lga"] = df["lga"].str.strip().str.title()
    df["region_group"] = df["region_group"].str.strip()
    return df


# ---------------------------------------------------------------------------
# STEP 3: COMPUTE AFFORDABILITY METRICS
# ---------------------------------------------------------------------------
def compute_affordability(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["annual_rent"] = df["median_weekly_rent"] * 52
    df["price_to_income_ratio"] = (df["median_sale_price"] / df["median_household_income"]).round(2)
    df["rent_to_income_ratio"] = (df["annual_rent"] / df["median_household_income"]).round(3)
    df["in_rental_stress"] = df["rent_to_income_ratio"] > RENTAL_STRESS_THRESHOLD
    df["severely_unaffordable"] = df["price_to_income_ratio"] > PRICE_INCOME_SEVERE
    return df


# ---------------------------------------------------------------------------
# STEP 4: SUMMARY STATS (for your README "Findings" section)
# ---------------------------------------------------------------------------
def print_summary(df: pd.DataFrame):
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year]
    has_income = df["median_household_income"].notna().any()

    print(f"\n=== Summary for {latest_year} ===")
    if has_income:
        summary = latest.groupby("region_group")[
            ["price_to_income_ratio", "rent_to_income_ratio"]
        ].mean().round(2)
        print(summary)

        best_value = latest.sort_values("price_to_income_ratio").head(5)[
            ["lga", "region_group", "price_to_income_ratio", "rent_to_income_ratio"]
        ]
        print(f"\n=== Best-value LGAs in {latest_year} (by price-to-income ratio) ===")
        print(best_value.to_string(index=False))
    else:
        # No income data yet -- show raw price/rent comparison so this quarter's
        # numbers are still usable while income is pending
        summary = latest.groupby("region_group")[
            ["median_sale_price", "median_weekly_rent"]
        ].agg(["mean", "median"]).round(0)
        print(summary)
        print("\n[Income data not yet loaded -- showing raw price/rent only. "
              "Affordability ratios will appear once income_by_lga.xlsx is added.]")

        cheapest = latest.sort_values("median_sale_price").head(5)[
            ["lga", "region_group", "median_sale_price", "median_weekly_rent"]
        ]
        print(f"\n=== 5 cheapest LGAs by median sale price, {latest_year} ===")
        print(cheapest.to_string(index=False))

        priciest = latest.sort_values("median_sale_price", ascending=False).head(5)[
            ["lga", "region_group", "median_sale_price", "median_weekly_rent"]
        ]
        print(f"\n=== 5 most expensive LGAs by median sale price, {latest_year} ===")
        print(priciest.to_string(index=False))


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    raw = generate_sample_data() if USE_SAMPLE_DATA else load_real_data()
    clean = clean_data(raw)
    result = compute_affordability(clean)

    print_summary(result)

    out_path = OUTPUT_DIR / "affordability_clean.csv"
    result.to_csv(out_path, index=False)
    print(f"\nSaved Tableau-ready file to: {out_path}")
