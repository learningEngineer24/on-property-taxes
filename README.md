# On Property Taxes

Who overpays and who underpays property tax in Alameda County, California —
measured from the county's own open data.

**Thesis:** Proposition 13 was written to protect homeowners from runaway
property taxes. Nearly fifty years later, it runs a two-sided distortion.
Longtime owners are taxed on a sliver of their homes' value, while buyers
from the 2021–2023 peak are taxed on value that no longer exists. Two
identical houses on the same street can carry tax bills differing by a factor
of four — determined entirely by *when* each owner bought.

## Findings (Oct 2026)

- **Tenure gradient:** Oakland single-family homes held 31+ years are assessed
  at a median $158k vs $661k for homes bought in the last two years — 4.2x.
- **Effective tax rates:** pre-1990 buyers pay a median **0.20%** of market
  value; 2022 buyers pay **0.93%** — a 4.6x multiple (statutory rate ≈ 1.17%).
- **Peak buyers over-assessed:** 2023 buyers' factored values sit **+$52k
  (+4.4%)** above today's market prices (95% bootstrap CI: +$19k to +$73k),
  measured against true sale prices from county transfer records.
- **The safety valve fires, but only for some:** 22% of 2023 buyers (1,134 of
  5,113) are already assessed *below* their purchase price — Prop 8
  decline-in-value reductions. The rest must discover the provision and
  appeal on their own.
- **It's geographic:** ZIP-level price changes from 2023 to 2024–25 range
  from −15.5% (94705, Berkeley hills) to +11.4% (94555, Fremont), and the
  over-assessment map mirrors the price-drop map. 94705 buyers are +25.5%
  over-assessed; Tri-Valley buyers remain under-assessed.

## Data sources

All from public records — no scraping:

| Source | What | Rows |
|---|---|---|
| Alameda County Open Data Hub — Parcels FeatureService | 489,628 parcels: assessed values, last recorded document, use codes, tax rate areas, centroids | 489,628 |
| Assessor's Ownership Transfer List | Priced sales 2023–2025 (price from documentary transfer tax) | 23,633 unique |
| Property Tax Rates 2025 + 2024 | Ad-valorem rate per tax rate area (combined: 1,416 TRAs) | 20,311 |
| Secured Tax Rolls 2019–2026 | Annual per-parcel assessed values | ~3.4M (in progress) |
| FRED MORTGAGE30US | 30-yr fixed mortgage rates (the rate-shock evidence) | weekly, 1971– |

Raw bulk files are too large for git — see `data/README.md` for reproduction
with the scripts in `src/`.

## Method

1. **Market anchors from the county itself.** Under Prop 13 a sale forces
   reassessment at the sale price, so recent transfer-list prices *are* market
   prices. No external price data needed for the core results.
2. **Paired 2023 test:** each 2023 buyer's assessed value today vs. its Prop 13
   trajectory (price × 1.02³). Median ratio 0.98 — the machinery works; the
   22% below purchase price are Prop 8 cuts.
3. **Cohort gaps:** 2023 buyers' factored values vs. true 2024–25 sale
   prices, by ZIP, with bootstrap confidence intervals.
4. **Effective rates:** (assessed × TRA rate) ÷ ZIP-median market value, per
   parcel, by purchase cohort.

The gold-standard design (repeat-sales: same house, both prices) wasn't
possible — the county publishes no bulk sale-history file. `notes/`
documents the three reasons and why the transfer-record design is the
closest feasible alternative. An early cohort analysis was contaminated by
the 2021 refinance boom on both sides; it was struck and rebuilt on
transfer-record prices (`cohort_gaps.py` superseded by `cohort_gaps_v3.py` —
kept in repo for transparency).

## Caveats

- `LatestDocumentDate` is the last *recorded* document, not necessarily a
  purchase — refinances don't reset Prop 13 basis. Parcel-document cohorts
  are refinance-contaminated (notably 2021); transfer-record prices are not.
- Market value per parcel uses ZIP medians — cohort medians are the robust
  unit, not individual parcels.
- Tax computed as assessed × TRA rate covers ad-valorem tax only; parcel
  taxes and special assessments are excluded.
- Prop 19 intergenerational transfers (UseCode 9999) are excluded from
  market-anchor cohorts — they aren't arm's-length sales.

## Reproduce

```bash
python3 src/download_parcels.py        # 489k parcels, resumable
python3 src/download_transfers.py      # ownership transfers w/ prices
python3 src/download_tax_rates.py      # 2025 TRA rates
python3 src/download_tax_rates_2024.py # 2024 TRA rates (fills gaps)
python3 src/validate_parcels.py
python3 src/cohort_gaps_v3.py          # clean gap analysis
python3 src/effective_rates.py         # per-parcel effective rates
```

## Contents

- `src/` — download + analysis scripts (Python 3, stdlib only)
- `notes/` — methodology notes, write-up draft, ZIP analysis
- `outputs/` — result summaries (JSON)
- `data/` — small reference files; bulk data excluded (see `data/README.md`)

## License

MIT — see LICENSE.
