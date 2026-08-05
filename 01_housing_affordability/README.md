# Sydney vs Regional NSW Housing Affordability Analysis

**Live dashboard**: [View on Tableau Public](https://public.tableau.com/app/profile/varghese.john4878/viz/Rentalproject_17858981785590/Dashboard1)

## Business question

Is the affordability gap between Greater Sydney and Regional NSW widening or narrowing,
and which regions offer the best value relative to local incomes — for renters and buyers?

## Data sources

1. **NSW Rent and Sales Report** (DCJ) — median weekly rent \& median sale price by LGA,
split Greater Sydney / Regional NSW, quarterly since 2011.
https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html
2. **ABS Census / Data Explorer** — median household income by SA3/SA4 region.
https://www.abs.gov.au
3. **(Optional) ABS SEIFA** — socio-economic index by LGA, for context on why some
regions score lower on affordability.

## Methodology

1. **Clean \& merge**: standardise LGA/region names across all three sources (this is
usually the messiest step — NSW datasets don't always use identical naming).
2. **Calculate affordability metrics**:

   * Price-to-income ratio = median sale price / median annual household income
(ratio > 6-7 is generally considered "severely unaffordable" internationally)
   * Rent-to-income ratio = (median weekly rent × 52) / median annual household income
(>30% of income is the standard "rental stress" threshold)
3. **Trend analysis**: track both ratios over time (2011–present) for Sydney vs Regional NSW.
4. **Regional breakdown**: rank LGAs within each group by affordability.
5. **Dashboard**: Tableau Public dashboard with:

   * Time-series of both ratios, Sydney vs Regional
   * LGA-level map/heatmap of current affordability
   * "Best value" regions ranked

## Findings

Based on Q1 2026 rent data, Q4 2025 sales data, and 2021 Census household income
(120 NSW LGAs analysed: 34 Greater Sydney, 86 Regional NSW):

* **Sydney is less affordable on average**: median price-to-income ratio of 11.9x
vs 8.7x for Regional NSW — but the picture is more nuanced than a simple
metro/regional split.
* **Rental stress is widespread, not just a Sydney problem**: 97 of 120 LGAs
(81%) have households spending over 30% of income on rent — including many
regional areas.
* **107 of 120 LGAs (89%) are "severely unaffordable"** by the standard
price-to-income benchmark (>6x annual household income) — this threshold has
effectively stopped being useful as a filter in the current NSW market.
* **Lifestyle-driven regional markets can be less affordable than Sydney**:
Byron (17.1x) and Tweed (17.4x) rank among the least affordable LGAs in the
entire state — both ahead of Northern Beaches (16.1x) and only just behind
Woollahra (18.8x, Sydney's least affordable LGA). This is the standout
counter-intuitive finding — regional does not automatically mean affordable.
* **Best-value LGAs** are concentrated in far-west/inland NSW: Cobar (3.2x),
Warren (3.8x), Broken Hill (3.9x), Moree Plains (3.9x), Hay (4.1x) — all
Regional NSW, all with limited population/job bases, which is itself a
caveat worth raising in an interview (cheap housing isn't automatically
"good value" if local employment is scarce).

## Business recommendation

For someone prioritising affordability with location flexibility, inland
regional centres (Wagga Wagga, Orange, Dubbo/Western Plains) offer a better
balance of affordability and liveability than either Sydney or NSW's
lifestyle-coast regional markets (Byron, Tweed), which now carry a
"lifestyle premium" that rivals inner Sydney.

## Known data limitations

* Rent (Q1 2026) and sales (Q4 2025) are from different quarters — the most
recent available at time of download. Close enough for a snapshot view;
worth noting in interviews.
* Income data is from the 2021 Census (most recent available small-area
income breakdown) and hasn't been inflation-adjusted to 2026 dollars — this
likely overstates price-to-income ratios somewhat since incomes have grown
since 2021 but the ratio still holds directionally.
* Cootamundra-Gundagai Regional (a 2021 amalgamated LGA) is matched to DCJ's
"Gundagai" entry as the closest available proxy, since DCJ still reports it
at the pre-amalgamation level in places.

## 

