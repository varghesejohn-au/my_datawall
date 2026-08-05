# Tableau Public Dashboard Build Notes

**Data source**: `output/affordability_clean.csv` (connect via Text File connector)

## Sheet 1 — Affordability trend over time
- Line chart: X = `year`, Y = `price_to_income_ratio`, Color = `region_group`
- Duplicate as a second line chart for `rent_to_income_ratio`
- Add a reference line at y=6 (severe unaffordability threshold) on the price chart,
  and y=0.30 (rental stress threshold) on the rent chart

## Sheet 2 — LGA comparison (current year)
- Bar chart: X = `lga`, Y = `price_to_income_ratio`, Color = `region_group`
- Filter to latest year, sort descending
- This is the "which suburb should I actually consider" view

## Sheet 3 — Best value ranking
- Table or bar chart: lowest `price_to_income_ratio` and `rent_to_income_ratio`
  combined into one score, ranked ascending
- This is your "so what" slide — the one recruiters remember

## Dashboard layout
- Top: trend chart (the story over time)
- Bottom-left: LGA bar chart (the detail)
- Bottom-right: best-value ranking (the takeaway)
- Add a text box at the top with a one-line insight, e.g.:
  "Sydney's price-to-income ratio has grown 16% faster than regional NSW's since 2015,
  while rental stress remains high in both."

## Publishing
- Publish to Tableau Public, title it clearly: "Sydney vs Regional NSW Housing
  Affordability (2015–2025)"
- Add a short description with your data sources listed (this signals rigor to
  anyone reviewing it)
