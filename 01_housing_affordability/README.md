# Sydney vs Regional NSW Housing Affordability Analysis (2024–2026)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data%20cleaning-150458?logo=pandas&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-Public-E97627?logo=tableau&logoColor=white)
![Data](https://img.shields.io/badge/Data-NSW%20DCJ%20%7C%20ABS%20Census-blue)

**Live dashboard**: [View on Tableau Public](https://public.tableau.com/app/profile/varghese.john4878/viz/Rentalproject_17858981785590/Dashboard1)

**📊 Findings summary**: [View key finding of this project](https://varghesejohn-au.github.io/my_datawall/01_housing_affordability/findings.html

## Business question
Is the affordability gap between Greater Sydney and Regional NSW widening or narrowing,
and which regions offer the best value relative to local incomes — for renters and buyers?

## Data sources
1. **NSW Rent and Sales Report** (DCJ) — median weekly rent & median sale price by LGA,
   split Greater Sydney / Regional NSW. One comparable quarter pulled per year
   (2024, 2025, 2026) to build a genuine trend rather than a single snapshot:
   - 2024: March 2024 rent / December 2023 sales (Issue 147)
   - 2025: March 2025 rent / December 2024 sales (Issue 151)
   - 2026: March 2026 rent / December 2025 sales (latest available)
   https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales.html
2. **ABS Census 2021** — median household income by LGA (Table G02). Census
   income is only refreshed every 5 years, so the same 2021 figure is applied
   across all three years — see Known Limitations below.

## Methodology
1. **Clean & merge**: standardise LGA names across all three DCJ report years
   and the Census DataPack (naming differences, amalgamated LGAs, and case
   mismatches all needed manual resolution — see `analysis.py` for details).
2. **Calculate affordability metrics** per LGA, per year:
   - Price-to-income ratio = median sale price / median annual household income
     (ratio > 6 is generally considered "severely unaffordable")
   - Rent-to-income ratio = (median weekly rent × 52) / median annual household income
     (>30% of income is the standard "rental stress" threshold)
3. **Trend analysis**: compare both ratios across 2024 → 2025 → 2026 for
   Sydney vs Regional NSW, and track the gap between the two groups over time.
4. **Dashboard**: interactive Tableau Public dashboard with a year-over-year
   trend view, LGA-level rankings, and cross-filtering by region.

## Findings
Based on three comparable years (2024–2026), 120+ NSW LGAs analysed each year:

- **Affordability is worsening in both regions, at almost exactly the same rate.**
  Sydney's mean price-to-income ratio rose from 10.65 (2024) → 11.19 (2025) →
  11.87 (2026); Regional NSW rose from 7.48 → 8.03 → 8.69 over the same period.
  **The gap between them has stayed essentially flat — 3.17, 3.16, then 3.18** —
  meaning Regional NSW is not "catching up" or "falling further behind" Sydney;
  both markets are deteriorating in lockstep. This is a more precise and more
  defensible finding than "Sydney is less affordable," which a single-quarter
  snapshot could only gesture at.
- **Rental stress is rising too, and rising faster in Regional NSW.** Mean
  rent-to-income ratio moved from 0.324 → 0.354 in Sydney (a 9% increase) but
  0.319 → 0.364 in Regional NSW (a 14% increase) over the same three years —
  regional renters are being squeezed somewhat faster than Sydney renters,
  even though regional buying remains comparatively cheaper.
- **97 of 120 LGAs (81%) are in rental stress** and **107 of 120 (89%) are
  "severely unaffordable"** by 2026 — these thresholds have become close to
  universal across NSW rather than useful filters.
- **Lifestyle-driven regional markets remain the standout exception**: Byron
  (17.1x) and Tweed (17.4x) rank among the least affordable LGAs in the
  entire state in 2026 — ahead of Northern Beaches (16.1x) and just behind
  Woollahra (18.8x, the state's least affordable LGA). Regional does not
  automatically mean affordable.
- **Best-value LGAs are concentrated in far-west/inland NSW**: Cobar (3.2x),
  Warren (3.8x), Broken Hill (3.9x), Moree Plains (3.9x), Hay (4.1x) — all
  Regional NSW, all with limited population/job bases, which is itself worth
  raising as a caveat in an interview.

## Business recommendation
The "Sydney vs Regional" framing understates the real story: **affordability
is deteriorating everywhere at a similar pace**, so relocating from Sydney to
"regional NSW" broadly is not, on its own, a hedge against the trend — it
mainly just resets the starting point lower. The exceptions matter more than
the average: lifestyle-coast markets (Byron, Tweed) now carry a premium
rivaling inner Sydney, while inland regional centres (Cobar, Broken Hill,
and mid-sized centres like Wagga Wagga, Orange) offer a materially better
affordability trajectory — with the tradeoff of a thinner local job market.

## Known data limitations
- **Income is static across all three years** — the ABS only refreshes
  small-area income data every 5 years (last Census: 2021), so the same
  income figure is applied to 2024, 2025, and 2026. This means the entire
  upward trend in both ratios is driven by price/rent movement, not income
  change — and since incomes have likely grown at least somewhat since 2021,
  the ratios probably slightly overstate the true worsening in affordability.
  The relative comparison (Sydney vs Regional, and the gap between them) is
  unaffected by this, since the same income figure is applied to both groups.
- Rent and sales are one quarter apart within each year (DCJ's own reporting
  convention) — a small inconsistency, treated as negligible at annual granularity.
- Cootamundra-Gundagai Regional (a 2021-amalgamated LGA) is matched to DCJ's
  "Gundagai" entry as the closest available proxy, since DCJ still reports it
  at the pre-amalgamation level in places.
- LGA coverage varies slightly year to year (122 in 2024, 118 in 2025, 120 in
  2026) due to DCJ suppressing low-volume LGAs in some quarters for data
  reliability — trend comparisons use whichever LGAs are present in both years
  being compared.
