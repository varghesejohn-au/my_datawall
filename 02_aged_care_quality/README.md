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
   target care minutes against quality measure outcomes, at the facility
   level, for 2024–2026.
4. **Compliance-vs-outcome analysis**: same approach as #3, but using the
   aggregate Compliance star rating. Note: the raw data also includes 7
   individual compliance "Standard" columns (new in the 2026 extract), but
   they're populated for essentially 1 facility nationally per quarter —
   they appear to log a value only when a specific audit event occurred that
   exact quarter, not as a persistent status. A standard-by-standard
   breakdown was attempted and dropped as unsupportable with this data;
   the aggregate Compliance star (well populated throughout) is used instead.
5. **Weakest-link diagnostic**: for each facility, identify which of the 4
   sub-ratings (Residents' Experience, Compliance, Staffing, Quality
   Measures) is lowest — both nationally and restricted to facilities rated
   ≤3 stars overall.
6. **Resident-experience dimension ranking**: the 12 survey dimensions (each
   reported as % Always/Most/Some/Never) are reshaped into long format and
   ranked by mean "% Always" nationally. Friendly dimension labels (e.g.
   "Food quality" for the raw "Food" column) are this analysis's own
   plain-language interpretation of each dimension's short column name, not
   official wording from the survey instrument.
7. **Audit-vs-lived-experience cross-check**: correlate aggregate Compliance
   star rating against residents' own reported "dignity" measures (mean of
   the Respect, Feel Heard, and Feels Like Home dimensions).
8. **Facility drill-down**: an interactive Tableau view where a single
   facility can be selected and compared against state/national benchmarks.

## A note on methodology validation
Several findings in this analysis (the matched-facility trend, the state
rank divergence, the specific risk-flag counts, the staffing-vs-medication
correlations) were cross-checked against an independent parallel analysis of
the same source data, run separately. Where our numbers matched closely
(e.g. the +0.21★ matched-facility improvement, the 3 facilities with 5-star
overall but poor Quality Measures, RN minutes vs antipsychotic use at
0.085 vs an independent 0.08), that's treated as a real confirmation. Where
they diverged — most notably, the parallel analysis described Quality
Measures as showing "no significant improvement" while our matched-facility
calculation shows a clear **decline** (-0.48 stars), and our
"persistent food failure" count (191) is much lower than a parallel estimate
(707), because we required two consecutive low-scoring years rather than
one — this analysis reports its own number with its methodology stated
explicitly, rather than adopting an external claim without being able to
verify its exact definition.

## Findings

**On the original staffing question:**
- **Staffing minutes barely predict quality outcomes.** Correlation between a
  facility's care-minutes gap (actual minus target) and its Quality Measures
  star rating is just **0.06** nationally (2026), and stays weak (0.09–0.14)
  across all three provider types.
- **Staffing target compliance has improved sharply** (53% → 77% of
  facilities meeting RN targets, 2024→2026) without a matching improvement
  in outcomes.

**Extending into compliance and resident experience:**
- **Compliance ratings don't predict outcomes either.** Compliance stars vs
  Quality Measures stars: 0.067. Compliance stars vs falls %: -0.021. Combined
  with the staffing finding, **none of the standard regulatory inputs
  (staffing minutes, compliance audit results) meaningfully predict actual
  resident outcomes** at the facility level — a consistent pattern across
  the whole analysis, not an isolated result.
- **Audit outcomes and resident-reported experience are almost totally
  disconnected.** Correlation between a facility's Compliance star rating and
  residents' own reports of feeling respected, heard, and "at home":
  **0.028** — essentially zero (n=2,337 facilities). A facility can pass its
  compliance audit while residents report not feeling heard, or the reverse.
  This is arguably the most interesting finding in the whole project: the
  regulatory audit and the lived resident experience appear to be measuring
  almost entirely different things.
- **Staffing is disproportionately the weak link for struggling facilities.**
  Nationally, Staffing is a facility's lowest-scoring sub-rating 37.7% of the
  time. Restricted to facilities rated ≤3 stars overall, that jumps to
  **56.9%** — for facilities that are genuinely struggling, staffing is by
  far the most likely culprit. Compliance is almost never the weak link
  (0.4% of the time), since nearly all facilities pass it.
- **Staffing's relationship with outcomes is selective, not uniformly
  zero.** RN minutes vs falls %: 0.000 (nothing); vs polypharmacy %: 0.179;
  vs antipsychotic use %: 0.085. Staffing shows a modest positive
  association with reduced medication-related measures specifically, but
  essentially none with falls — "does staffing predict quality" doesn't have
  one single answer across every quality measure.
- **Food quality is the clearest, most specific weak point nationally.**
  Ranking all 12 resident-experience survey dimensions by "% Always" response
  rate: Food quality is lowest at **28.2%**, a full 50 points behind the
  strongest dimension, Feeling Safe (78.3%). Staff competence (43.6%),
  service operations (45.6%), and clear communication (45.9%) also lag well
  behind dimensions like feeling heard (72.2%) and staff caring (69.3%).

**Sector-level trends (matched-facility basis — more rigorous than raw yearly averages):**
Raw yearly national averages mix in facilities entering/exiting the sector
between years. Restricting to the ~1,700-1,816 facilities present in **both**
2024 and 2026 gives a fairer trend, and it tells a more interesting story
than a simple "everything improved":

| Sub-rating | 2024 | 2026 | Change |
|---|---|---|---|
| Overall | 3.64 | 3.85 | +0.21 |
| Residents' Experience | 3.44 | 3.65 | +0.21 |
| Compliance | 4.52 | 4.91 | +0.39 |
| Staffing | 2.83 | 3.24 | +0.40 |
| **Quality Measures** | **3.56** | **3.08** | **-0.48** |

**Every sub-rating improved except Quality Measures, which declined
meaningfully** — the fraction of facilities scoring 5-star QM dropped from
22.6% to 11.6% of the matched set. Overall, Compliance, Staffing, and
Resident Experience all moved up over the same period. This is a genuinely
important nuance: the headline "ratings have improved" story is being driven
by everything **except** the one sub-rating that's actually shown to track
real clinical measures. Whether this reflects real outcome deterioration or
a recalibration of the QM methodology can't be determined from this data
alone, but it's the opposite direction from what the other four sub-ratings
suggest, which is itself worth flagging rather than smoothing over.
- Total facility count has declined every year (2,620 → ~2,591), consistent
  with known sector consolidation.
- Government-run facilities rate highest on official rating (4.21★ avg, 2026)
  vs Not for Profit (3.85★) and Private for Profit (3.71★) — but see the
  eta-squared finding below, which shows this gap is much smaller once you
  look at actual outcomes rather than the official rating.

## Do the star ratings actually mean what people assume they mean?

This deserves its own section, because it's arguably the most useful output
of this entire analysis for anyone actually choosing a facility.

**Finding 1 — three of the four sub-ratings barely discriminate between
facilities at all.** Measuring the spread (standard deviation) of each
sub-rating across all facilities nationally (2026):

| Sub-rating | Most common band | Std dev | Discriminating power |
|---|---|---|---|
| Compliance | 83.2% of facilities score 5★ | 0.40 | Almost none — nearly everyone passes |
| Overall | 71.9% score 4★ | 0.51 | Weak — heavily compressed |
| Residents' Experience | 92.5% sit at 3-4★ | 0.62 | Weak — compressed in the middle |
| **Staffing** | Spread fairly evenly 1★–5★ | **1.17** | **Good** |
| **Quality Measures** | Spread fairly evenly 1★–5★ | **1.03** | **Good** |

A rating where 83% of facilities land in the same single band cannot
meaningfully separate a "good" facility from a "great" one — it can really
only separate "failed" from "passed."

**Finding 2 — the Quality Measures star is the one rating that's internally
valid.** It's well-spread *and* it actually correlates with its own
underlying clinical numbers (QM star vs falls %: -0.36, vs restrictive
practices %: -0.48). Compliance and Staffing don't show this same coherence
with outcomes (see Findings section above) — so QM is the most trustworthy
single rating in the whole system.

**Finding 3 — falls and pressure injury rates barely differ across
Compliance star bands.** 5-star compliance facilities average 30.9% falls;
4-star average 31.3%; 3-star average 32.6% (n=14, small sample). A 5-star
and a 4-star compliance facility are statistically almost indistinguishable
on actual falls outcomes.

**Finding 4 — provider type explains over twice as much variance in the
official rating as it does in actual outcomes.** Using eta-squared (the
standard one-way ANOVA effect size — what fraction of total variance is
explained by group membership):
- Provider type's effect on the **official overall rating**: η² = 0.059
- Provider type's effect on the **actual clinical outcome composite**: η² = 0.026

In plain terms: whether a facility is Government, Not for Profit, or
Private for Profit predicts its official star rating more than twice as
strongly as it predicts its actual resident outcomes. Government facilities
score meaningfully higher on the badge than the underlying numbers alone
would justify.

**Finding 5 — roughly 1 in 7 facilities' ratings meaningfully disagree with
their actual outcomes, in both directions.** A simple regression of the
clinical outcome composite against official overall star rating, with
facilities flagged where their actual residual sits more than 1 standard
deviation from what their rating alone predicts:
- **73.3%** of facilities: rating and outcome are reasonably aligned
- **13.4%**: potentially **under-rated** — actual outcomes better than the
  official rating would suggest
- **13.3%**: potentially **over-rated** — actual outcomes worse than the
  official rating would suggest
- **26 facilities** are statistical outliers (residual beyond 3 standard
  deviations) — the most extreme, most audit-worthy disagreements between
  badge and reality

**Finding 6 — NSW is the most under-rated state in the country.** Comparing
each state's official mean-rating rank against its actual-outcome-composite
rank:

| State | Official rank | Outcome rank | Divergence |
|---|---|---|---|
| NSW | 5th | **2nd** | **+3 (most under-rated)** |
| SA | 8th | 6th | +2 |
| TAS | 2nd | 1st | +1 |
| ACT | 3rd | 4th | -1 |
| QLD | 4th | 5th | -1 |
| VIC | 6th | 7th | -1 |
| WA | 7th | 8th | -1 |
| NT | 1st | 3rd | -2 (most over-rated) |

NSW ranks only 5th on official star rating but 2nd on actual clinical
outcomes nationally — the largest positive divergence of any state. NT sits
at the opposite end: rated 1st officially but only 3rd on actual outcomes.

## Where does the badge disagree with reality? Facility-level audit flags

Five explicit, self-defined risk categories (thresholds are our own choices,
documented here — not inherited from any external source), computed on the
2026 data:

| Risk flag | Facilities | % | Definition |
|---|---|---|---|
| Adequately staffed, poor outcomes | 498 | 19.2% | Met RN care-minute target AND Quality Measures rated 1-2 stars |
| High compliance, resident dignity gap | 478 | 18.4% | Compliance = 5 stars AND bottom-quartile resident-reported dignity (Respect/Feel Heard/Feels Like Home) |
| Persistent food failure | 191 | 7.4% | Bottom-quartile Food score in **both** 2025 and 2026 (two consecutive low scores, not one) |
| Understaffed, good outcomes | 90 | 3.5% | Missed RN care-minute target AND Quality Measures rated 4-5 stars |
| 5-star overall, poor Quality Measures | 3 | 0.1% | The most direct "badge disagrees with clinical data" case |

The 3 facilities carrying a 5-star overall badge alongside a 1-2 star
Quality Measures rating are the sharpest, most concrete example of the
badge/reality gap in the entire dataset.

### Practical guide: what should actually matter to a prospective customer (or an auditor)

1. **Quality Measures star + the raw percentages underneath it** — the most
   trustworthy single signal, since it's both well-spread and internally
   coherent. Check the raw falls/pressure-injury/restrictive-practice
   percentages directly rather than relying on the star bucket alone, since
   a bucket can hide where a borderline facility actually sits.
2. **Individual Residents' Experience dimension scores, not the composite
   star.** The composite is compressed and uninformative on its own, but the
   raw dimension scores (Food, Feels Like Home, Feels Heard) capture the
   dignity/quality-of-life side that neither the compliance audit nor
   staffing minutes touch at all (near-zero correlation between Compliance
   stars and resident-reported dignity measures — see Findings above).
3. **Staffing minutes — a resourcing check, not a safety proxy.** Useful for
   spotting a facility that's meaningfully under-resourced relative to
   target, but it does not predict falls or injury outcomes, so don't treat
   it as one.
4. **Compliance star — a pass/fail floor, not a comparison tool.** With 83%
   of facilities at 5 stars, it has almost no power to distinguish between
   facilities that have all cleared the bar.
5. **Overall star rating — a coarse first filter only.** Useful for
   excluding clearly low performers, but the sub-ratings show it doesn't
   reliably track actual resident safety — don't let it substitute for
   points 1 and 2 above.

**The broader, more structural point**: since 3 of the 4 sub-ratings are
ceiling-compressed and don't predict clinical outcomes, the current Star
Ratings system's real discriminating power rests almost entirely on Staffing
and Quality Measures. The other two components (Compliance, Residents'
Experience composite) currently add reassurance more than they add genuine
differentiation between facilities. This is a legitimate critique of the
measurement system's design, not just a finding about individual facilities.

## Finding real benchmark facilities (not just 5-star badges)

Rather than trusting the overall star rating, a composite "actual
performance" score was built directly from the underlying numbers: real
adverse-event percentages (falls, pressure injuries, restrictive practices,
unplanned weight loss, antipsychotic use, polypharmacy — all inverted so
lower is better), RN staffing minutes, and average resident-reported "Always"
satisfaction across all 12 experience dimensions — combined as a simple
average of z-scores. Restricted to Medium/Large facilities only, since Small
facilities can show 0% falls purely from having very few residents, which
isn't a statistically reliable signal at that scale.

**The result is striking: of the national top 20 facilities by actual
composite performance, 16 are rated 4-star overall, only 3 are 5-star**
(one has no published overall rating). The facilities genuinely excelling on
real outcomes and real staffing are disproportionately sitting one tier
below the "official" top badge — concrete, quantified confirmation of the
measurement-validity point above.

**Top facility nationally by actual performance**: *Anthem* (TBG Senior
Living Services, NSW, Private for Profit, Large) — 16% falls, 0% pressure
injuries, despite being officially rated 4-star, not 5-star.

**Best performer identified per state** (Medium/Large facilities only):

| State | Facility | Provider type | Official rating |
|---|---|---|---|
| NSW | Anthem (TBG Senior Living Services) | Private for Profit | 4★ |
| VIC | Gibson Street Complex (Bendigo Health Care Group) | Government | 4★ |
| QLD | Carinity Brownesholme Manor | Not for Profit | 4★ |
| SA | Romani (RSL Care SA) | Not for Profit | 4★ |
| WA | Regents Garden Four Seasons Booragoon | Private for Profit | 4★ |
| TAS | Bishop Davies Court (OneCare) | Not for Profit | 4★ |
| ACT | Goodwin Ainslie | Not for Profit | 4★ |
| NT | Terrace Gardens | Not for Profit | 4★ |

Every single state's top actual performer is rated 4-star, not 5-star — the
pattern holds nationally, not just as a national-average artifact.

These facilities are worth treating as genuine **benchmarks to study**: what
are they doing operationally that translates into real outcomes, rather than
just a high badge? That's a question this public data can point to but can't
answer on its own — it would need direct engagement with these providers'
practices to actually learn from them.

**Caveat**: this composite score is one reasonable way to combine these
measures, not the only one — different weightings would shift the exact
ranking. The *qualitative* pattern (best actual performers skew toward
4-star, not 5-star) is robust to reasonable variations in the weighting;
the exact facility at #1 is more sensitive to it.

### Hidden Champions — the 3-star facilities quietly outperforming almost everyone

A related but distinct cut: facilities rated **3 stars or below overall**,
but sitting in the **top quartile of actual clinical outcomes** nationally
(Medium/Large facilities only). **47 facilities** meet this bar — officially
mediocre, actually excellent. Top example: **Maranatha House** (NSW,
3-star overall), whose actual outcome composite outranks the vast majority
of 4- and 5-star facilities in the country. These are arguably the most
interesting facilities in the whole dataset to study directly — whatever
they're doing operationally isn't showing up in their badge.

## Business recommendation
For a facility (or the sector) trying to move its rating, this data suggests
prioritising staffing levels first if overall rating is a genuine weak point
(most predictive single lever for low performers), while treating passing a
compliance audit as necessary but not remotely sufficient for resident
satisfaction — resident experience needs to be measured and acted on
directly, since it's not something a compliance pass guarantees. Food
quality is the single dimension most residents nationally are unhappy with
(28.2% "Always" — a full 50 points behind the strongest dimension), and it's
consistently the weakest dimension in every state without exception — an
unusually specific, actionable finding. Notably, food quality holds flat
across provider types but varies clearly by facility size (Small 32.0% vs
Large 25.2%), suggesting scale itself, not ownership structure, is a driver
worth investigating further.

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
   - `staffing_quality_detail.csv` (2024–2026, care minutes + quality measure
     detail + weakest-link diagnostic)
   - `re_dimension_detail.csv` (2024–2026, long format, 12 resident-experience
     dimensions x facilities x years)
   - `benchmark_facilities.csv` (2026, composite actual-performance score,
     Medium/Large facilities only)
   - `matched_trend.csv` (2024→2026 matched-facility sub-rating changes)
   - `facility_audit_intelligence.csv` (2026, one row per facility: rating
     vs outcome residual, rating classification, all 5 risk flags, hidden
     champion flag)
   - `state_rank_divergence.csv` (official rating rank vs actual outcome
     rank, all 8 states/territories)
3. Open all three CSVs in Tableau Public — see `tableau_dashboard_notes.md` for the build plan
