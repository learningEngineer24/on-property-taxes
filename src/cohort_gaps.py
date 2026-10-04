"""SUPERSEDED — DO NOT CITE. Both sides contaminated by the 2021 refinance
wave (see notes/methodology_gold_standard.md). Rebuilt as cohort_gaps_v3.py
(clean transfer-record design) and corrected in cohort_gaps_v4.py
(buyer-specific Prop 13 trajectory factors). Kept for transparency.

Cohort-gap analysis: for each purchase-year cohort Y,
gap(Y) = median(assessed | bought in Y) - median(assessed | sold 2024-2026),
matched on geography + property type (SFR, UseCode 1100).

Positive gap => cohort over-assessed vs today's market (Prop 8 territory).
Negative gap => classic Prop 13 discount.
Bootstrap CI on the headline 2021-2022 gap.
"""
import json, random
import os
from collections import defaultdict
from datetime import date

IN = BASE + "/data/parcels.jsonl"

cohorts = defaultdict(list)   # doc_year -> [assessed]
recent = []                    # sold 2024-2026
recent_by_zip = defaultdict(list)
cohort2122_by_zip = defaultdict(list)

for line in open(IN):
    r = json.loads(line)
    if r.get("UseCode") != "1100":
        continue
    v = r.get("TotalNetValue")
    d = r.get("LatestDocumentDate")
    if not v or not d:
        continue
    try:
        y = date.fromtimestamp(int(d) / 1000).year
    except Exception:
        continue
    if y < 1970 or y > 2026:
        continue
    zipc = (r.get("SitusZip") or "").strip()
    cohorts[y].append(v)
    if y >= 2024:
        recent.append(v)
        recent_by_zip[zipc].append(v)
    if y in (2021, 2022):
        cohort2122_by_zip[zipc].append(v)

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

med_recent = med(recent)
print(f"recent-sale cohort (2024-26 SFR): n={len(recent):,} median=${med_recent:,.0f}\n")
print("purchase-year cohort gaps (positive = over-assessed vs today's market):")
print(f"{'year':>6} {'n':>8} {'med_assessed':>13} {'gap_$':>10} {'gap_%':>7}")
for y in sorted(cohorts):
    if y >= 2024:
        continue
    m = med(cohorts[y])
    gap = m - med_recent
    print(f"{y:>6} {len(cohorts[y]):>8,} ${m:>12,.0f} ${gap:>+9,.0f} {100*gap/med_recent:>+6.1f}%")

# bootstrap CI for 2021-2022 pooled gap
random.seed(7)
c2122 = cohorts[2021] + cohorts[2022]
m0 = med(c2122) - med_recent
diffs = []
for _ in range(1000):
    a = [random.choice(c2122) for _ in range(len(c2122))]
    b = [random.choice(recent) for _ in range(len(recent))]
    diffs.append(med(a) - med(b))
diffs.sort()
print(f"\n2021-2022 pooled: n={len(c2122):,} gap=${m0:+,.0f} "
      f"({100*m0/med_recent:+.1f}%), 95% CI [${diffs[25]:+,.0f}, ${diffs[975]:+,.0f}]")

# by-ZIP for 2021-2022: where is over-assessment concentrated?
print("\n2021-2022 gap by ZIP (min 40 sales in each cohort):")
rows = []
for z, vals in cohort2122_by_zip.items():
    rv = recent_by_zip.get(z, [])
    if len(vals) >= 40 and len(rv) >= 40 and z:
        g = med(vals) - med(rv)
        rows.append((g, z, len(vals), len(rv), med(vals), med(rv)))
rows.sort(reverse=True)
for g, z, n1, n2, m1, m2 in rows[:15]:
    print(f"  {z}: gap=${g:+,.0f} ({100*g/m2:+.1f}%)  bought21-22 n={n1} med=${m1:,.0f} | recent n={n2} med=${m2:,.0f}")
print("  ...")
for g, z, n1, n2, m1, m2 in rows[-5:]:
    print(f"  {z}: gap=${g:+,.0f} ({100*g/m2:+.1f}%)  bought21-22 n={n1} med=${m1:,.0f} | recent n={n2} med=${m2:,.0f}")

json.dump({
    "median_recent_2024_26": med_recent, "n_recent": len(recent),
    "gap_2021_2022": m0, "gap_2021_2022_ci95": [diffs[25], diffs[975]],
    "by_year": {str(y): {"n": len(v), "median": med(v),
                "gap": med(v) - med_recent} for y, v in cohorts.items() if y < 2024},
    "by_zip_2021_2022": [{"zip": z, "gap": g, "n_buy": n1, "n_recent": n2,
                          "med_buy": m1, "med_recent": m2}
                         for g, z, n1, n2, m1, m2 in rows],
}, open(BASE + "/outputs/cohort_gaps.json", "w"), indent=1)
print("\nwrote outputs/cohort_gaps.json")
