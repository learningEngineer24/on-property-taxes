# On Property Taxes — technical project page (DRAFT)

Companion to the essay. This page documents the data, the pipeline, and the
analysis design — including the approaches I tried, the contamination I caught,
and the gold-standard design I couldn't run.

## The question

California's Prop 13 ties a home's assessed value to its purchase price plus
max 2% annual growth. So two identical houses on the same street can carry
wildly different tax bills depending on *when* they were bought — and buyers
who purchased at the 2021–22 price peak may now be assessed above what their
homes are actually worth. I set out to measure both effects in Alameda County
from the county's own open data.

## Data sources

All data is public, published by the Alameda County Assessor's office
(ArcGIS FeatureServer endpoints), plus one federal series:

| Source | What | Size / coverage | Endpoint |
|---|---|---|---|
| Parcel bulk feed | All 489,628 parcels: APN, address, assessed values, UseCode, TRA, latest document date | 489,628 rows, downloaded Oct 3 2026 | `services5.arcgis.com/ROBnTHSNjoZ2Wm1P/.../Parcels/FeatureServer/0/query` |
| Property tax rates 2025 | Ad-valorem fund rates by Tax Rate Area | 10,000 rows (hard-truncated by the service), 1,342 TRAs | `.../Property_Tax_Rates_2025/FeatureServer/0/query` |
| Property tax rates 2024 | Same, prior year | 10,311 rows, 1,415 TRAs | `.../Property_Tax_Rates_2024/FeatureServer/0/query` |
| Ownership transfer list | Recorded transfers 2023–2025 with transfer-tax-implied sale prices | 187,908 raw rows → 23,633 unique priced transfers | `.../Assessor_Office_Ownership_Transfer_List/FeatureServer/0/query` |
| Annual secured tax rolls 2019–2026 | Per-parcel assessed values, one layer per tax year | 7 layers, downloading | `.../Assessor_Office_Secured_Tax_Roll_{YEAR}/FeatureServer/0/query` |
| FRED 30-yr mortgage rate | Weekly national average | 2021 avg 2.96% → 2023 avg 6.81% | `fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US` |
| Redfin / Zillow ZHVI ZIP series | ZIP-level price history for the 2022-peak proof | In progress | Redfin Data Center, Zillow Research |

Code for every download and analysis step: [github.com/learningEngineer24/on-property-taxes](https://github.com/learningEngineer24/on-property-taxes).

## How the data was pulled

Plain Python + `requests`, paginating with `resultOffset`/`resultRecordCount`
(the parcel feed needed ~490 pages of 1,000). Every script checkpoints to disk
(`.ckpt` files) so a dropped connection resumes instead of restarting — the
seven tax-roll layers take ~2–3 hours total.

Three gotchas worth knowing if you reuse this data:

1. **The 2025 tax-rate layer is truncated at exactly 10,000 rows.** The service
   silently caps responses. 74 TRAs are missing from 2025; I filled them from
   the 2024 layer (which returns all 10,311 rows) to build a combined
   1,416-TRA table, preferring 2025 where available.
2. **TRA join keys need normalizing.** Parcel records store the TRA secondary
   as a zero-padded string; the rate layers use integers. Joining naively
   misses 94% of parcels. Integer-normalize both sides first.
3. **The transfer list is mostly not sales.** 62.4% of rows have blank
   transfer-tax values (exempt/non-arm's-length transfers) and 64.8% are
   duplicate transferor/transferee records. After dedup and priced-sale
   filtering: 23,633 usable sales, 99.7% of which join to the parcel file.
   `UseCode=9999` (Prop 19 intergenerational transfers) must be excluded from
   any arm's-length price benchmark.

## Analysis approach

**Tenure gradient (descriptive).** County single-family homes grouped by
latest-document year: median assessed value runs $822k (0–2 yrs) down to $238k
(31+ yrs) — a 3.5× gradient (4.2× in Oakland). Caveat: document dates include
refinances, so this is tenure-adjacent, not pure tenure.

**Effective tax rates per parcel.** For each of 264,829 single-family parcels:
(rate for its TRA) × (assessed value) ÷ (estimated market value, proxied by
ZIP/property-type median transfer price). Median effective rate: 0.20% for
pre-1990 document cohorts vs 0.93% for 2022 — a 4.6× multiple. Cohort medians
are defensible; individual-parcel rates are approximate because market value
is a ZIP-level proxy, not a parcel comp.

**Clean peak-buyer test (v3, current headline).** Two independent cuts:
- *Paired (v4, corrected):* 5,113 single-family homes with priced 2023 transfers,
  present assessment vs. buyer-specific Prop 13 trajectory (H1 buyers price×1.02³,
  H2 buyers price×1.02² -- the county applies no inflation factor at the first
  lien for H2 buyers, verified in the rolls). Median ratio 1.00; 22.2% assessed
  *below* their purchase price (Prop 8 decline-in-value reductions at work).
- *Cross-section (v4):* 2023 purchase prices factored forward vs. actual 2024–25
  sale prices (5,124 vs 7,909 homes). Gap: **+$41,613 / +3.5%**, bootstrap 95%
  CI **+$7k to +$48k** (sampling noise only). Median ZIP gap +$50k (block CI
  +$30k to +$66k).
- *ZIP ranking:* 2023 factored values vs. actual 2024–25 prices range from
  +23.1% (94705) to −6.6% (94555). ZIP-level 2023→2024–25 price changes range
  −15.5% to +11.4%, with correlation 0.12 against 2023 price levels — a genuine
  divergence story, not just "expensive ZIPs fell."

## Why not the gold standard

The textbook design is a repeat-sales test: for each home, compare its current
assessment against the 2%-factored trajectory of its *previous* purchase price
(the informative counterfactual — comparing against the reassessment created
by the sale itself is mechanical under Prop 13). Three problems blocked it:

1. **No pre-2023 bulk sale history.** The parcel feed carries only the latest
   document, not a sale history. (Partially resolved: the county publishes a
   2023–2025 transfer list and annual rolls back to 2019, enabling the paired
   2023 test above — but not a full pre-2023 history.)
2. **The mechanical comparison trap.** Sale price vs. the reassessment it
   triggers tells you nothing; the right benchmark is the prior trajectory.
3. **Selection in quick resales.** Homes bought in 2021–22 and resold by
   2024–25 are a selected subset, not a random sample of the cohort.

I also caught and fixed a real contamination mid-project: the first cohort
design used latest-document dates as sale proxies, but the 2021 refinance wave
meant the "2021–22 buyer" benchmark (median $822k) was mostly refinances, not
purchases — the true transfer-price median was ~$1.22M. That estimate is
superseded and kept in the repo only for transparency.

## Limitations (honest list)

- Market values are ZIP/property-type medians, not parcel-level comps — the
  county bulk data has no interior square footage, bedrooms, or bathrooms.
  If longtime owners' homes sit ~20% below their ZIP median, the 4.6x
  effective-rate gradient compresses to ~3-4x (still a multiple, not a margin).
- 2025 transfer data is a partial year.
- Latest-document year ≠ ownership tenure (refinances pollute it, biasing
  recent-bucket assessments downward — the tenure gradient is conservative).
- The cross-section gap compares different homes across windows; the CI
  covers sampling noise only, not composition shift.
- Per-ZIP gaps rest on small samples (as few as n=30); rankings are
  approximate.
- Transfer-tax-implied prices verified uniform across cities (median
  assessed/(price×factor) 0.993–1.000) — no city-tax distortion found.
- No Census-demographics join: deliberately out of scope. This is a
  Prop-13-mechanics story, not a demographic-equity story.

## Status (Oct 2026)

Complete: trajectories verified (22.3% of 2023 buyers with Prop 8 relief,
committed in src/prop8_verify.py), ZHVI peak series (41/46 ZIPs peaked spring
2022), final charts. Independent technical review completed Oct 3, 2026
(notes/review_2026-10-03.md) — led to v4's buyer-specific trajectory factors
and the strictly post-purchase Prop 8 definition.
