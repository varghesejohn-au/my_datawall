# Tableau Public Dashboard Build Notes — v3 (4-dashboard restructure)

**Data sources to connect** (7 CSVs, each as a separate Text File connection):
`star_ratings_trend.csv`, `staffing_quality_detail.csv`, `re_dimension_detail.csv`,
`benchmark_facilities.csv`, `matched_trend.csv`, `facility_audit_intelligence.csv`,
`state_rank_divergence.csv`

All share `facility_key` (and most share `year`) so they can be blended in a
sheet if ever needed, but each dashboard below mostly uses one primary source.

---

## DASHBOARD 1 — National Overview
*Purpose: the sector-level picture. What's the trend, who's rated highest, is staffing improving.*

**Sheet 1.1 — National Trend** *(already built — keep as-is)*
`star_ratings_trend` — line chart, X=year (discrete), Y=AVG(overall_stars), Color=provider_type

**Sheet 1.2 — Provider Type Comparison** *(already built — keep as-is)*
`star_ratings_trend` — bar chart, X=provider_type, Y=AVG(overall_stars), filter year=2026

**Sheet 1.3 — Staffing Compliance Trend** *(already built — keep as-is)*
`staffing_quality_detail` — bar chart, X=year, Y=% Met RN Target (calculated field), formatted as %

**Sheet 1.4 — Matched-Facility Trend (NEW — replaces the naive trend as the headline of this dashboard)**
`matched_trend` — bar chart: X=sub_rating, Y=mean_change. Color rule: negative values (Quality
Measures, the only decline) should stand out — use a diverging color (e.g. red for negative,
blue/green for positive). Add data labels showing the exact +/- value. This is the sheet that
carries the "everything improved except Quality Measures" finding — make sure Quality Measures'
bar is visually the standout.

**Layout**: 1.4 (matched trend) at top as the headline, 1.1 and 1.2 side by side below, 1.3 at
the bottom. Add a title text box: "Ratings are rising — except the one that tracks real outcomes"

---

## DASHBOARD 2 — What Actually Predicts Quality?
*Purpose: the core "staffing/compliance don't predict outcomes" story.*

**Sheet 2.1 — Staffing vs Quality** *(already built — keep as-is)*
`staffing_quality_detail` — scatter, X=rn_minutes_gap, Y=quality_measures_stars, Detail=facility_key,
Tooltip=provider_type, single trend line, filter year=2026, subtitle showing R²=0.004

**Sheet 2.2 — Compliance vs Quality (NEW, mirrors 2.1)**
`staffing_quality_detail` — scatter, X=compliance_stars, Y=quality_measures_stars, Detail=facility_key,
single trend line (same steps as 2.1: don't put provider_type on Color if you want one overall
line — Tooltip only). Filter year=2026. Subtitle: state the R² once you see it (expect very low,
consistent with the 0.067 correlation we calculated).

**Sheet 2.3 — Weakest Link Breakdown (NEW)**
`staffing_quality_detail` — bar chart, X=weakest_link_category, Y=COUNT(facility_key). Build TWO
versions side by side: (a) all facilities, (b) filtered to overall_stars <= 3. Easiest approach:
duplicate the sheet, apply the filter to the second copy, place them side by side on the
dashboard. This is what shows Staffing jumping from 37.7% to 56.9% as the weak link for
struggling facilities.

**Sheet 2.4 — Resident Experience Dimension Ranking (NEW)**
`re_dimension_detail` — horizontal bar chart, X=AVG(pct_always), Y=dimension, sorted ascending
(weakest at top). Filter year=2026. This surfaces Food Quality as the clear weakest dimension.
Consider a reference line or color threshold to flag anything under ~40%.

**Layout**: 2.1 and 2.2 side by side at top (the two scatters, same visual language), 2.3 and 2.4
side by side below. Headline text box: "Neither staffing nor compliance meaningfully predicts
quality outcomes — but the weakest-link data tells you where to actually look"

---

## DASHBOARD 3 — Audit & Quality Intelligence (NEW dashboard)
*Purpose: where does the official rating disagree with reality, and who's a genuine benchmark.*

**Sheet 3.1 — Rating vs Outcome (the central audit visual)**
`facility_audit_intelligence` — scatter, X=overall_stars, Y=outcome_composite, Detail=facility_key,
Color=rating_classification (3 categories: Aligned / Potentially under-rated / Potentially
over-rated — use a clear diverging palette, e.g. gray for Aligned, blue for under-rated, red for
over-rated). Add a trend/reference line if useful. Tooltip should include service_name and state.

**Sheet 3.2 — Risk Flag Summary**
`facility_audit_intelligence` — needs Measure Names/Measure Values, since the 5 risk flags are
separate boolean columns. Drag Measure Names to Columns (filter to just the 5 flag fields:
persistent_food_failure, high_compliance_dignity_gap, adequately_staffed_poor_outcomes,
understaffed_good_outcomes, five_star_low_qm), drag Measure Values to Rows/Text as a bar chart.
Booleans: use AVG of each flag to get the percentage directly (AVG of True/False = the % True).
Sort descending by frequency.

**Sheet 3.3 — State Rank Divergence**
`state_rank_divergence` — small 8-row table; a bar chart of `rank_divergence` sorted descending
(NSW at one end, NT at the other) tells the story simply and clearly. A dumbbell/slope chart
(two points per state, official_rank and outcome_rank, connected by a line) is more visually
interesting if you want to attempt it, but the simple bar is the reliable starting point.

**Sheet 3.4 — Top Performers / Hidden Champions**
`benchmark_facilities` — table: service_name, state, provider_type, overall_stars,
composite_score, sorted descending, filtered to Top 15. Add a second small table or filter
toggle for Hidden Champions specifically (from `facility_audit_intelligence`, filter
is_hidden_champion=True AND overall_stars<=3) — these are the "officially 3-star, actually
excellent" facilities.

**Layout**: 3.1 (the scatter) large at top — this is the dashboard's anchor. 3.2 and 3.3 side by
side in the middle. 3.4 (leaderboard table) at the bottom, full width. Headline text box:
"1 in 7 facilities are meaningfully mis-rated in either direction — here's where to look"

---

## DASHBOARD 4 — Facility Report Card
*Purpose: look up any one facility and see everything about it.*

**Sheet 4.1 — Facility Drill-Down** *(already built — keep the parameter setup as-is)*
`staffing_quality_detail` — scorecard table using the `Selected Facility` parameter and
`Is Selected Facility` calculated field, as already built.

**Sheet 4.2 — Selected Facility's Resident Experience Breakdown (NEW)**
`re_dimension_detail` — needs the SAME parameter (`Selected Facility`) and an equivalent
`Is Selected Facility` calculated field built on THIS data source (parameters are workbook-level
and reusable across sources, but calculated fields referencing `facility_key` need to be
recreated per source since it's a different table). Bar chart: X=dimension, Y=pct_always,
filtered to the selected facility, filter year=2026. Shows the actual survey results across
all 12 dimensions, not just the composite star.

**Sheet 4.3 — Selected Facility's Audit Status (NEW, small)**
`facility_audit_intelligence` — again needs the parameter + calculated field rebuilt on this
source. Simple text display: rating_classification, residual value, and which (if any) risk
flags are True for this facility. Turns the report card into a genuine mini-audit summary.

**Layout**: 4.1 (scorecard) at top, 4.2 (RE breakdown chart) and 4.3 (audit status) side by side
below. Make sure the `Selected Facility` parameter control is visible and easy to find.

---

## Styling (carry over from Project 2's earlier styling pass)
- Government: deep teal (`#1E5C55`), Not for Profit: muted gold (`#B08B2E`), Private for Profit:
  brick red (`#A13D2C`) — consistent across all 4 dashboards
- Rating classification colors (Dashboard 3 specifically): Aligned=gray, Under-rated=blue,
  Over-rated=red — deliberately different palette from provider type, so the two color schemes
  never get confused when a viewer moves between dashboards
- Background: very light warm gray (`#F5F3F0`), consistent font via Format → Workbook
- Each dashboard needs its own title + one-line headline insight text box, same pattern as
  Project 1 and Dashboards 1/2 above

## Publishing
- These can be 4 separate published vizzes, OR 4 dashboards within one workbook published once
  (Tableau Public supports multi-dashboard workbooks with tabs) — recommend the single-workbook
  approach so there's one link to share, with dashboard tabs for navigation
- Title: "Aged Care Star Ratings: Audit & Quality Intelligence (2023–2026)"
- Description should mention both data sources and reference the cross-validation methodology
  note from the README
