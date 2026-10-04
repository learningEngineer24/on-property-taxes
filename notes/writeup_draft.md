# On Property Taxes — DRAFT (Oct 3, 2026)

*Status: draft (revised with full tax-roll trajectories and ZHVI peak series,
Oct 3, 2026). Pending: Nebo's red pen. All numbers below are from Alameda
County's own open data unless noted.*

---

## 1. Where this started

In August 2026 I filed a property tax appeal on my home at 7001 Exeter Dr,
Oakland (appeal no. 2026-100748-1). The county assessed it at $1,664,640 for
2026–27; I argued it's worth $1,480,000 — $185,000 less, about 11% below the
assessment. The assessor's informal review denied me in September.

I didn't set out to write about tax policy. I set out to check whether my
number was right. But the deeper I got into the county's own data — every
parcel, every sale, every tax rate area — the more I realized my appeal was
one instance of something much bigger. This is what I found.

## 2. The claim

California's Proposition 13 was written to protect homeowners from runaway
property taxes. Nearly fifty years later, it does something its authors never
intended: it runs a two-sided distortion. Longtime owners are taxed on a
sliver of their homes' value, while buyers from the 2021–2023 peak are taxed
on value that no longer exists. Two identical houses on the same street can
carry tax bills that differ by a factor of four — determined entirely by *when*
each owner bought.

## 3. The analysis

**The data.** Alameda County publishes an extraordinary amount of open data:
489,628 parcels (assessed values, last recorded document, property type, tax
rate area), the ad-valorem tax rate for each of 1,416 tax rate areas, an
ownership transfer list with 23,633 priced sales from 2023 to 2025 (sale
prices backed out from the documentary transfer tax), and — the piece that
made verification possible — the annual secured tax rolls for 2019 through
2026, giving per-parcel assessed values for seven straight years. Under
Prop 13, a sale forces reassessment at the sale price, so the county's data
contains its own market anchors. For the price-peak question I used Zillow's
ZHVI ZIP-level series (smoothed, seasonally adjusted, monthly): 41 of 46
Alameda County ZIPs peaked in the spring of 2022, with a median drawdown of
13% since. No other outside data was needed.

**The tenure gradient.** Among Alameda County single-family homes, the median
assessed value for homes held 31+ years is $238,000. For homes bought in the
last two years: $822,000. Same county, same property type — a 3.5x gap,
produced entirely by the 2%-per-year cap compounding over decades. (In
Oakland, the gradient runs steeper: 4.2x.)

**Effective tax rates.** Convert to what people actually pay as a share of
market value (assessed value × local tax rate ÷ market value, with market
value from the county's own 2024–25 sale prices by ZIP):

| Bought | Median effective rate |
|---|---|
| Before 1990 | 0.20% |
| 1990s | 0.33% |
| 2000s | 0.49% |
| 2010s | 0.62% |
| 2024 | 0.94% |

A pre-1990 buyer pays less than a quarter the effective rate of a 2024 buyer
on an equivalent home — a 4.6x multiple on ZIP-median market proxies
(plausibly 3–4x if longtime owners' homes sit below their ZIP median, as
older homes tend to). (The statutory rate is about 1.17%; even recent buyers
land below it here because the comparison uses neighborhood medians — the
cohort medians are the robust unit.)

**Peak buyers are over-assessed.** Take 5,113 homes bought in 2023 — true
purchase prices from the transfer records — and compare each home's assessed
value today against its Prop 13 trajectory. One thing the rolls taught me:
the 2% inflation factor isn't applied at the first lien date for everyone —
January–June buyers enrolled at ×1.02, July–December buyers at ×1.00. With
buyer-specific trajectories, the median home sits at 100% of its trajectory:
the machinery works as designed. But **22% are assessed below what the owner
paid** — the market fell out from under them, and the assessment hasn't
caught up. As a group, 2023 buyers' factored values sit **$42,000 (+3.5%)
above 2024–25 sale prices** (95% CI: +$7k to +$48k, sampling noise only).

**Verified in the tax rolls.** The annual rolls let me trace those 2023
buyers parcel by parcel, 2019 through 2026. **22% have received a Prop 8
decline-in-value reduction** — a strictly post-purchase year-over-year cut
in assessed value, median cut 8.6%. The timing is the story: barely 2% had
relief through the January 2025 roll; a ~20% wave arrived in the 2026 cycle.
The safety valve exists and it is being used. It is years late: nearly eight
in ten peak buyers are still riding the full trajectory on value the market
took away.

**Why it varies by ZIP.** Prop 13's trajectory rises no matter what the
market does, so a neighborhood's over-assessment gap is approximately its
factored growth (~4–5% for the typical buyer) minus its actual price change —
which means the gap ranking follows the price-drop ranking *by construction*.
The genuine finding is the divergence itself: county transfer records show
ZIP-level price changes from 2023 to 2024–25 ranging from **−15.5% to
+11.4%**, independently corroborated by ZHVI. The hardest-hit: 94705
(Berkeley hills, +23.1% over-assessed), 94609 (+23.0%), 94610 (+14.4%). The
Tri-Valley kept climbing and its 2023 buyers remain under-assessed. One pair
tells the story: 94705 and 94539 (Fremont) both sat near $2.3–2.4M in 2023 —
the same price tier — then one fell 15.5% and the other rose 9.8%. It isn't
about price level (the correlation is 0.12); it's about local market dynamics.

**My appeal, in context.** My ZIP code (94611) measures +$165,000 (+11.0%)
over-assessed for 2023 buyers. My appeal argues −$185,000. The county's
own data and my requested value agree almost to the dollar. And my parcel's
own trajectory tells the story in miniature: bought in 2021, reassessed to
$1,706,600, growing at 2% a year — until the assessor granted a Prop 8 cut
to $1,600,000 in 2024, an 8% reduction. The office has already agreed with
me once, in effect. I'm arguing the market fell further than that cut
acknowledged.

**How I checked myself.** The gold-standard design here is a repeat-sales
study: same house, purchase price vs. resale price. I couldn't run it — the
county publishes no bulk sale-history file (three specific reasons are
documented in the methodology notes), so I used the closest feasible design:
true 2023 purchase prices against Prop 13 trajectories, and true 2024–25
sale prices as the market benchmark, both from county records. An early
version of this analysis was contaminated by the 2021 refinance boom on both
sides; I caught it, struck those numbers, and rebuilt on transfer-record
prices. The results above are the clean ones.

## 4. What this means — against the original intent

In the mid-1970s, Bay Area home values were exploding and assessments with
them — the LA County assessor warned of 100% valuation jumps in a single
year. Homeowners, especially elderly ones on fixed incomes, faced being taxed
out of houses they'd owned for decades: a tax on unrealized gains they had no
cash to pay. Proposition 13 (June 1978, passed roughly 2-to-1) answered with
three things: a 1% rate cap, a 2%-per-year cap on assessment growth, and an
acquisition-value system — your assessment is your purchase price until you
sell. The courts upheld it as fairer than what came before; the U.S. Supreme
Court (1992) found a legitimate state interest in neighborhood stability, with
Justice Blackmun writing that new buyers "don't require the same protection"
as longtime owners.

The intent was a shield. Compounded over 48 years, the shield became a
tenure lottery. Nothing in 1978 contemplated a buyer paying tax at four times
the effective rate of his neighbor — or a buyer being taxed on $185,000 of
value that evaporated when mortgage rates doubled from 3% to 7%. The law's
one downside protection, Proposition 8 (decline-in-value reassessment, also
1978), does get used — my parcel-level trace found Prop 8 cuts for 22% of
2023 buyers — but the burden of discovery still sits entirely on the
homeowner, and the assessor's office does not come looking. More than seven
in ten peak buyers are still assessed on the full trajectory. How many of
them know they can ask for a reduction?

## 5. What the county should do

Three concrete, low-cost steps for the Assessor's office — no legislation
required:

1. **Proactive decline-in-value reviews.** When a neighborhood's sale prices
   fall materially below factored trajectories — a condition the office can
   detect from its own transfer records — initiate Prop 8 reviews instead of
   waiting for owners to discover the provision and file. The data to trigger
   this already exists inside the office.
2. **Notify owners.** When county records indicate a parcel's market value has
   likely fallen below its assessed value, tell the owner — a line on the tax
   bill, a letter, anything. Awareness is currently the whole ballgame.
3. **Publish an annual assessment-vs-market report by neighborhood.** The
   county already publishes the raw ingredients; a short yearly synthesis
   would let every homeowner see where they stand without filing a public
   records request or building this analysis themselves.

None of this weakens Proposition 13. It finishes a job the law started in
1978: making sure people are taxed on what their homes are actually worth.

---

*Methodology appendix, charts, and per-parcel data to follow. All analysis
code and county data sources documented in the project repository.*
