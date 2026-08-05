# Aged Care Star Ratings Analysis (National, 2023–2026)

## Business question
Are aged care homes actually improving over time, does provider type
(not-for-profit vs private vs government) predict quality, and — the
question everyone assumes has an obvious answer — does higher staffing
directly translate into better resident outcomes?

## Data sources
**Star Ratings quarterly data extract** (Department of Health, Disability
and Ageing) — service-level Star Ratings for every government-funded
residential aged care home in Australia, published quarterly since May 2023.
Free direct download, no account required.
https://www.health.gov.au/resources/collections/star-ratings-quarterly-data-extracts

Four comparable quarters used for the trend: May 2023, May 2024, May 2025, May 2026.

Two sheets used from each file:
- **Star Ratings** (summary): Overall Star Rating + 4 sub-category ratings
  (Residents' Experience, Compliance, Staffing, Quality Measures) — used for
  the 4-year trend (2023–2026)
- **Detailed data**: real underlying numbers behind the Staffing and Quality
  Measures ratings — registered nurse care minutes (target vs actual), total
  care minutes (target vs actual), and quality measure percentages (falls,
  pressure injuries, unplanned weight loss, medication management). Only
  available from **2024 onward** — the 2023 extract doesn't include this sheet.

## Methodology
1. **Clean & merge**: standardise `Purpose` (provider type) labels, which are
   inconsistently cased/worded across releases ("Not for profit" vs "Not for
   Profit", "For profit" vs "Private for Profit") but represent the same 3
   categories throughout. Build a `facility_key` (Service Name + Provider
   Name) to track facilities across years, since there's no stable facility
   ID in the published data.
2. **Trend analysis**: mean overall star rating and sub-ratings by year,
   nationally and by provider type.
3. **Staffing-vs-outcome analysis**: correlate the *gap* between actual and
   target care minutes against quality measure outcomes (falls, pressure
   injuries, etc.), at the facility level, for 2024–2026.
4. **Facility drill-down**: an interactive Tableau view where a single
   facility can be selected and compared against state/national benchmarks
   across every metric in this analysis.

## Findings

- **Star ratings have risen every year**: national mean overall rating went
  3.38 (2023) → 3.64 (2024) → 3.77 (2025) → 3.83 (2026). Read this with
  caution though — the ratings methodology itself changed over this period
  (notably the Staffing rating redesign in October 2025), so part of this
  rise may reflect measurement changes rather than pure quality improvement.
  This is exactly the kind of caveat worth raising proactively in an interview.
- **Government-run facilities rate highest**: 4.21 stars on average (2026),
  vs 3.85 for Not for Profit and 3.71 for Private for Profit. Worth noting
  government facilities are a much smaller slice of the sector (~161 of 2,596
  facilities nationally), so this isn't necessarily a "government runs care
  better" story so much as a smaller, different-shaped sample.
- **The standout finding — staffing minutes barely predict quality outcomes.**
  Correlation between a facility's care-minutes gap (actual minus target) and
  its Quality Measures star rating is just **0.06** nationally, and stays weak
  (0.09–0.14) even when split by provider type. In plain terms: a facility
  hitting or exceeding its staffing minute targets is **only very weakly
  associated** with better falls, pressure injury, or medication management
  outcomes. This complicates the simple "more staff = better care" narrative
  the sector (and policy debate) often assumes — the real drivers of quality
  outcomes are likely elsewhere (skill mix, management quality, resident
  acuity, training) and staffing minutes alone are a poor proxy for them.
- **Staffing target compliance has improved sharply**: the share of
  facilities meeting their RN care minute target rose from 53% (2024) to 77%
  (2026) — a genuine operational improvement, even though (per the point
  above) it hasn't translated proportionally into better outcomes.
- **Sector consolidation**: total facility count has declined every year
  (2,620 → 2,607 → 2,601 → 2,591 by our facility-key count) — consistent with
  known industry consolidation trends, worth a one-line mention rather than a
  deep dive since it's a side observation, not the main analysis.

## Business recommendation
If the objective is improving resident outcomes rather than just hitting
staffing compliance targets, this data suggests the sector (and any provider,
including ones I've worked with) should be cautious about treating staffing
minute compliance as a sufficient quality strategy on its own — it's
necessary but evidently not close to sufficient. Outcome-focused metrics
(the Quality Measures themselves) deserve to be tracked and acted on
directly, not assumed to follow automatically from staffing inputs.

## Known data limitations
- **No stable facility ID** — matching facilities across years uses Service
  Name + Provider Name, which breaks if a facility renames or changes
  ownership between quarters. This is the same category of limitation as the
  LGA-name mismatches in Project 1.
- **2023 has no Detailed data sheet** — the staffing-minutes and quality-measure
  percentage analysis is necessarily limited to 2024–2026, not the full
  2023–2026 window used for the star-rating trend.
- **Methodology changes mid-series**: the Staffing rating calculation was
  redesigned in October 2025, and the Compliance rating gained additional
  sub-standard detail columns in 2026 that don't exist in earlier extracts.
  Year-over-year comparisons should be read as directional, not perfectly
  like-for-like.
- **Correlation ≠ causation, and there's likely confounding**: facilities
  with higher-need residents may both require (and receive) more staffing
  minutes *and* have inherently higher fall/injury rates regardless of care
  quality — this could partly explain why the staffing-outcome correlation is
  weak rather than negative. A more rigorous version of this analysis would
  control for resident acuity, which isn't available in this public dataset.
- **Missing data**: ~11% of facilities have no staffing-minutes data and ~6%
  have no Quality Measures rating in the latest quarter (typically newer or
  very small facilities); these are excluded from the relevant calculations
  rather than imputed.

## How to reproduce
1. Raw files in `data/raw/`: `star-ratings-2023/2024/2025/2026.xlsx`
2. Run `python analysis.py` — outputs land in `output/`:
   - `star_ratings_trend.csv` (2023–2026, summary level)
   - `staffing_quality_detail.csv` (2024–2026, care minutes + quality measure detail)
3. Open both CSVs in Tableau Public — see `tableau_dashboard_notes.md` for the build plan
