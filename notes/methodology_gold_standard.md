# Methodology note: the gold standard we couldn't use (for the write-up)

## The gold-standard approach: repeat-sales (paired) design
For each house bought in 2021–2022, take its assessment history after purchase;
for the subset resold since, compare the resale price against the county's
assessed value (equivalently, against the Prop 13 2%-per-year trajectory from
the purchase price). Same house, two prices — controls for size, lot, condition,
micro-location. This is the design behind Case-Shiller-style indices.

## Why we couldn't follow it: three problems
1. **The history doesn't exist in bulk.** Our county feed is a single snapshot:
   one assessed value + one latest-document date per parcel. A resale resets the
   assessed value and erases the 2021–2022 purchase price from anything
   downloadable. Per-parcel sale history exists only in the Assessor's web UI
   (parcel by parcel), not as a bulk dataset. Executable for case studies, not
   for thousands of homes.
2. **The literal test is mechanical under Prop 13.** A resale forces reassessment
   at the sale price, so "does the resale price align with the assessed value"
   answers "yes" by law. The informative comparison is resale price vs. the
   2%-trajectory — i.e., did the market outrun or lag the Prop 13 path — which is
   the same economic question our cohort design answers.
3. **Selection bias cuts against the question.** Homes bought in '21–'22 AND
   resold by '26 are a selected subset (flips, distress, life events), transacting
   below market on average — making assessments look more accurate than they are.
   The population of interest (still holding, still paying on the peak assessment)
   is excluded by construction.

## What we did instead: cohort pseudo-panel
For each purchase-year cohort Y: gap(Y) = median(assessed | bought in Y)
− median(assessed | sold '24–'26), matched on ZIP + property type. Recent sales'
assessed values ARE market prices (Prop 13 resets at sale), so the county data
contains its own anchors — no external scraping. Refinance contamination in the
recent-sale cohort drags its median down, so the gap is an UPPER BOUND on
over-assessment. ## CORRECTION (Oct 3, v2/v3): the v1 gaps are superseded
The v1 cohort analysis (+2.6% for 2021–22) was contaminated on BOTH sides and its
levels should not be cited:
- The "recent sale" benchmark (parcels with 2024–26 documents) was dominated by
  non-sale documents (refis, trust transfers) carrying stale low assessments --
  true 2024–25 SFR sale prices (transfer list) median $1.22M vs v1's $822k.
- The "2021–22 buyer" parcel cohort was heavily polluted by the 2021 refinance
  boom: parcels with 2021–22 documents whose assessed values imply much older
  purchases. v3's 2022-only cohort still shows -$347k, confirming contamination.
The v1 SIGN FLIP shape across cohorts remains suggestive, but cite v4 numbers:
- Paired 2023 (n=5,113): median assessed/expected = 1.00 with buyer-specific
  Prop 13 trajectories (see CORRECTION 2 below); 22.2% assessed BELOW purchase
  price (Prop 8 cuts working).
- Clean cross-section: 2023 buyers' factored values vs true 2024–25 prices:
  pooled +$42k (+3.5%), 95% CI [+$7k, +$48k] (sampling noise only). Both sides
  true prices.
- ZIP ranking: Berkeley/Oakland hills most over-assessed (94705 +23.1%,
  94609 +23.0%, 94611 +11.0%); Tri-Valley still under-assessed.

## CORRECTION 2 (Oct 3, v4): buyer-specific Prop 13 trajectory factors
v3 applied a uniform price*1.02^3 trajectory to all 2023 buyers. The county's
rolls show the 2% inflation factor is NOT applied at the first lien date for
everyone: 2023 transfers recorded Apr–Jun enrolled at x1.02 at the Jan-2024
lien (~88%), while Jul–Dec transfers enrolled at x1.00 (~88–96%) — the
assessment-roll close (~Jun 30) decides which base lien date applies.
Correct trajectories to the Jan-2026 lien: H1-2023 buyers price*1.02^3,
H2-2023 buyers (the majority) price*1.02^2. v3's uniform factor overstated
expected AV ~2% for ~60% of buyers (paired median 0.98 -> 1.00; pooled gap
+$52k -> +$42k). See src/cohort_gaps_v4.py. Independently verified by a
second pass over the rolls.
