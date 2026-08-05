# Varghese John — Data Portfolio

ICT Systems Support Professional (8+ years across aged care systems, enterprise ICT,
and IT support) transitioning into data analytics roles in Australia. This repo
documents five hands-on projects built with real Australian datasets, each one
covering the full workflow: data sourcing → cleaning → analysis → interactive
dashboard → documented findings.

**Location**: Wollongong, NSW 

**Core skills**: SQL, Python (pandas), Power BI, Tableau, IBM Cognos, Excel/Power
Query, requirements elicitation, stakeholder management

**Credentials**: MBA (Lean Operations & Systems) · BTech Computer Science ·
IBM Certified Data Scientist · Certificate III in Individual Support

---

## Projects

| # | Project | Focus | Status | Links |
|---|---|---|---|---|
| 1 | **Sydney vs Regional NSW Housing Affordability** | Data cleaning, SQL-style joins, Tableau dashboard, geo-comparison | ✅ Complete | [Code](./01_housing_affordability) · [Live Dashboard](https://public.tableau.com/app/profile/varghese.john4878/viz/Rentalproject_17858981785590/Dashboard1) |
| 2 | **NSW Public Transport Delay Analysis** | Time-series analysis, operational analytics | 🔜 In progress | — |
| 3 | **Healthcare Access Dashboard (AIHW)** | Public-sector data storytelling, Tableau | 🔜 Planned | — |
| 4 | **Retail Sales Forecasting** | Python, simple predictive modelling | 🔜 Planned | — |
| 5 | **End-to-End Mini ETL Pipeline** | SQL database, Python ETL, deployed dashboard | 🔜 Planned | — |

---

## Project 1 highlights

**Question**: Is Regional NSW actually more affordable than Sydney — for both
renters and buyers?

Analysed 120 NSW LGAs combining DCJ rent/sales data with 2021 Census household
income to compute price-to-income and rent-to-income affordability ratios.

**Key finding**: Regional NSW isn't uniformly affordable — lifestyle-driven
markets like Byron and Tweed rank among the *least* affordable LGAs in the
state, rivaling inner Sydney suburbs. Best value is concentrated in inland
regional centres (Cobar, Broken Hill, Moree Plains), with the caveat that
low prices there often reflect a thin local job market.

[Full write-up →](./01_housing_affordability/README.md)

---

## How these projects were built

Each project follows the same repeatable process:
1. Source real Australian data (data.gov.au, ABS, AIHW, state open data portals)
2. Clean and merge with Python (pandas) — every transformation documented
3. Compute a business-relevant metric, not just a summary statistic
4. Build an interactive Tableau or Power BI dashboard
5. Write up findings, a business recommendation, and known data limitations

More projects will be added here as they're completed — check back or watch
this repo for updates.
