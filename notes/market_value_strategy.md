# Market-value identification strategy (notes, Oct 3 2026)

## The problem
Effective tax rate = (assessed value × TRA rate) / market value. Market value is
unobserved; we need anchors. Plan idea: recent transfers ≈ market value at transfer
(Prop 13 reassesses on sale).

## What the parcel data gives us
- `LatestDocumentDate`: latest *recorded document* — NOT necessarily a sale.
  Refinances record documents but do NOT reset the Prop 13 basis.
- `LatestDocument_Prefix` / `LatestDocumentSeries` (checked Oct 3, n=2000 sample):
  prefix is mostly the recording YEAR (2021, 2025, ...), series is a serial number.
  Neither encodes document type. A `TRAN` prefix value appears (~3.6%) — possibly
  "transfer", unverified. Empty prefix + `000000` series on ~3.6%.
- **Conclusion: these fields do NOT distinguish deeds from refinances.**

## Usable filters from UseCode
- `9999` = "P19 - Intergenerational Transfers" (Prop 19 parent-child transfers,
  excluded from reassessment). NOT arm's-length — exclude from anchor cohort.
- "First Sale" codes (1420/1520/7320-series etc.) = new-construction first sales —
  natural market-value anchors.

## Recommended stance
Use recent-document parcels (excluding 9999, including first-sales) as the anchor
cohort, and treat contamination explicitly:
- Refinanced parcels keep their OLD (low) assessed value, so they bias the
  recent-cohort effective rate DOWNWARD — the measured tenure gradient is a
  conservative LOWER BOUND on the true Prop 13 effect.
- Report the gradient with this caveat, not as a point estimate of the truth.

## Next-session investigation
- Does the County Recorder publish a recorded-documents dataset WITH document
  types (grant deed vs deed of trust)? That would give a clean sale flag.
- Check what `TRAN` prefix means (sample those parcels).
- Historical assessed-value layers (2020–2026 by TRA) are TRA-level, not parcel —
  can't detect parcel-level reassessment jumps from them.
