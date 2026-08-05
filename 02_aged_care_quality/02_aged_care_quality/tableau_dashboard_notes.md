# Tableau Public Dashboard Build Notes — Project 2

**Data sources**: connect to BOTH CSVs as separate data sources (or a single
workbook with two connections) — `star_ratings_trend.csv` (2023–2026,
national) and `staffing_quality_detail.csv` (2024–2026, care-minute detail).
They share `facility_key` and `year`, so you can blend them in a sheet if needed.

## Sheet 1 — National trend
- Line chart: X = `year` (discrete), Y = AVG(`overall_stars`)
- Color = `provider_type` — shows the Government/Not for Profit/Private gap
  persisting across all 4 years
- Add data labels

## Sheet 2 — Provider type comparison (latest year)
- Bar chart: X = `provider_type`, Y = AVG(`overall_stars`)
- Filter to `year` = 2026
- Consider a second small bar chart breaking down the 4 sub-ratings
  (Residents' Experience, Compliance, Staffing, Quality Measures) by
  provider type — use Measure Names/Measure Values to get all 4 sub-ratings
  onto one chart

## Sheet 3 — Staffing vs quality scatter (the headline finding)
- Scatter: X = `rn_minutes_gap`, Y = `quality_measures_stars`
- Detail = `facility_key`, Color = `provider_type`
- Filter to `year` = 2026 (or leave all 3 years in with Year on Color/Shape,
  same pattern as Project 1's scatter, if you want to show it's weak in
  every year, not just the latest)
- Add a trend line (Analytics pane → drag "Trend Line" onto the chart) —
  this will visually confirm just how flat/weak the relationship is, which
  is the whole point of this chart
- This is your "surprising finding" chart — the one that should anchor the dashboard

## Sheet 4 — Staffing target compliance trend
- Bar chart: X = `year`, Y = % meeting target (create a calculated field:
  `SUM([met_rn_target]) / COUNT([met_rn_target])` or use AVG on the boolean)
- Shows the operational-improvement story (53% → 77%) even though it hasn't
  moved outcomes much — pairs well next to Sheet 3 as a contrast

## Sheet 5 — Facility drill-down (your requested feature)
This is the interactive "how did MY facility do" view:
1. Right-click in the data pane → **Create Parameter**
   - Name: `Selected Facility`
   - Data type: String
   - List: add values (you can populate this from `facility_key` — Tableau
     lets you pull "Add from field" if you've loaded the data first)
2. Create a calculated field `Is Selected Facility`:
   `[facility_key] = [Selected Facility]`
3. Build a chart (e.g. a bar chart of the 4 sub-ratings, or the staffing
   scatter) and drag `Is Selected Facility` onto Color — the selected
   facility will highlight distinctly against all others
4. Right-click the `Selected Facility` parameter → **Show Parameter Control**
   — this adds a dropdown/search box to the dashboard so a viewer can type
   or select any facility by name
5. For a cleaner "report card" feel, also build a dedicated text table:
   filter to `Is Selected Facility` = True, show all its key metrics
   (star ratings, RN minutes actual vs target, quality measure %s) in one
   row — this becomes a mini scorecard for whichever facility is selected

## Styling
Reuse the same disciplined approach as Project 1, but with a palette suited
to healthcare rather than housing — avoid generic "medical blue," aim for
something that reads as considered:
- Government: deep teal (`#1E5C55`)
- Not for Profit: muted gold (`#B08B2E`)
- Private for Profit: brick red (`#A13D2C`)
- Background: very light warm gray (`#F5F3F0`), consistent font via
  Format → Workbook

## Publishing
- Title: "Aged Care Star Ratings: Does Staffing Predict Quality? (2023–2026)"
- Description should mention both data sources and the facility-count caveat
- Consider leading the dashboard with the scatter (Sheet 3) rather than the
  trend line, since the surprising correlation finding is the strongest hook
