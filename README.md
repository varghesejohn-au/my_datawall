# Varghese John — Data Portfolio

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-E97627?logo=tableau&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-4479A1?logo=postgresql&logoColor=white)

ICT Systems Support Professional (8+ years across aged care systems, enterprise ICT,
and IT support) transitioning into data analytics roles in Australia. This repo
documents five hands-on projects built with real Australian datasets, each one
covering the full workflow: data sourcing → cleaning → analysis → interactive
dashboard → documented findings.

**Location**: Wollongong, NSW | Open to roles in Illawarra, Newcastle, and Sydney

**Core skills**: SQL, Python (pandas), Power BI, Tableau, IBM Cognos, Excel/Power
Query, requirements elicitation, stakeholder management

**Credentials**: MBA (Lean Operations & Systems) · BTech Computer Science ·
IBM Certified Data Scientist · Certificate III in Individual Support

---

## Projects

| # | Project | Focus | Status | Links |
|---|---|---|---|---|
| 1 | **Sydney vs Regional NSW Housing Affordability** | 3-year trend analysis, data cleaning, Tableau dashboard, geo-comparison | ✅ Complete | [Code](./01_housing_affordability) · [Live Dashboard](https://public.tableau.com/app/profile/varghese.john4878/viz/Rentalproject_17858981785590/Dashboard1) |
| 2 | **NSW Public Transport Delay Analysis** | Time-series analysis, operational analytics | 🔜 In progress | — |
| 3 | **Healthcare Access Dashboard (AIHW)** | Public-sector data storytelling, Tableau | 🔜 Planned | — |
| 4 | **Retail Sales Forecasting** | Python, simple predictive modelling | 🔜 Planned | — |
| 5 | **End-to-End Mini ETL Pipeline** | SQL database, Python ETL, deployed dashboard | 🔜 Planned | — |

---

## Project 1 highlights

**Question**: Is the affordability gap between Sydney and Regional NSW widening
or narrowing — for both renters and buyers?

Analysed 120+ NSW LGAs across three years (2024–2026), combining DCJ rent/sales
data with 2021 Census household income to compute price-to-income and
rent-to-income affordability ratios.

**Key finding**: Both regions are becoming less affordable at almost exactly
the same rate — the Sydney/Regional gap has stayed flat (~3.17x) across all
three years — but rental stress is climbing *faster* in Regional NSW (+14%)
than Sydney (+9%). Lifestyle-driven markets like Byron and Tweed remain the
standout exception, ranking among the state's least affordable LGAs and
rivaling inner Sydney.

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
