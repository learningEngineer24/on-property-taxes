"""SUPERSEDED — DO NOT CITE. Buyer side still refinance-contaminated
(see notes/methodology_gold_standard.md). Rebuilt as cohort_gaps_v3.py
and corrected in cohort_gaps_v4.py. Kept for transparency.

Re-run the cohort-gap analysis anchored on TRUE sale prices from the
Assessor's ownership transfer list (instead of median assessed of the
recent-document cohort).

- Transfers deduped: each appears twice (TRANSFEROR + TRANSFEREE rows).
- Priced transfers only (blank value_from_trans_tax => exempt/non-sale).
- Benchmark: median transfer-list sale price 2024-2025, SFR (use_cd 1100), by ZIP.
- 2021-22 buyer cohort: median assessed today, SFR, by ZIP (from parcels).
- Repeat sales: APNs with 2+ priced transfers -> sale2 vs sale1 * 1.02^yrs.
"""
import json
import os
from collections import defaultdict
from datetime import date

# ---------- load transfers ----------
seen = set()
sales = []  # (apn, year, price, zip, use_cd)
for line in open(BASE + "/data/transfers.jsonl"):
    r = json.loads(line)
    apn = (r.get("apn") or "").strip()
    v = (r.get("value_from_trans_tax") or "").strip().rstrip(".")
    key = (apn, r.get("transfer_dt"), v)
    if key in seen:
        continue
    seen.add(key)
    if not v or not apn:
        continue
    try:
        price = float(v)
        y = date.fromtimestamp(int(r["transfer_dt"]) / 1000).year
    except Exception:
        continue
    if price <= 0 or y not in (2023, 2024, 2025):
        continue
    sales.append((apn, y, price, (r.get("zip_cd") or "").strip(),
                  (r.get("use_cd") or "").strip()))

print(f"unique priced transfers: {len(sales):,}")

# ---------- parcel APN set + 2021-22 cohort ----------
parcel_apns = set()
c2122 = defaultdict(list)   # zip -> [assessed]
for line in open(BASE + "/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    if a:
        parcel_apns.add(a)
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
    if y in (2021, 2022):
        c2122[(r.get("SitusZip") or "").strip()].append(v)

sale_apns = {s[0] for s in sales}
print(f"transfer APNs joining to parcels: {len(sale_apns & parcel_apns):,} / {len(sale_apns):,} "
      f"({100*len(sale_apns & parcel_apns)/max(1,len(sale_apns)):.1f}%)")

# ---------- benchmark: true sale prices 2024-2025, SFR ----------
bench = defaultdict(list)
for apn, y, price, z, uc in sales:
    if y in (2024, 2025) and uc == "1100" and z:
        bench[z].append(price)

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

print("\nZIP-level gaps, 2021-22 buyers' assessed vs TRUE 2024-25 sale prices (min 25 each):")
rows = []
for z, assessed in c2122.items():
    b = bench.get(z, [])
    if len(assessed) >= 25 and len(b) >= 25:
        ma, mb = med(assessed), med(b)
        rows.append((ma - mb, z, len(assessed), len(b), ma, mb))
rows.sort(reverse=True)
for g, z, n1, n2, ma, mb in rows[:12]:
    print(f"  {z}: gap=${g:+,.0f} ({100*g/mb:+.1f}%)  assessed21-22 n={n1} med=${ma:,.0f} | sales24-25 n={n2} med=${mb:,.0f}")
print("  ...")
for g, z, n1, n2, ma, mb in rows[-5:]:
    print(f"  {z}: gap=${g:+,.0f} ({100*g/mb:+.1f}%)  assessed21-22 n={n1} med=${ma:,.0f} | sales24-25 n={n2} med=${mb:,.0f}")

# pooled with bootstrap CI
import random
random.seed(11)
A = [v for vs in c2122.values() for v in vs]
B = [p for _, y, p, z, uc in sales if y in (2024, 2025) and uc == "1100"]
g0 = med(A) - med(B)
ds = []
for _ in range(1000):
    ds.append(med([random.choice(A) for _ in range(len(A))])
              - med([random.choice(B) for _ in range(len(B))]))
ds.sort()
print(f"\npooled 2021-22 buyers (n={len(A):,}) vs true 2024-25 sales (n={len(B):,}): "
      f"gap=${g0:+,.0f} ({100*g0/med(B):+.1f}%), 95% CI [${ds[25]:+,.0f}, ${ds[975]:+,.0f}]")

# ---------- repeat sales ----------
by_apn = defaultdict(list)
for apn, y, price, z, uc in sales:
    by_apn[apn].append((y, price))
rep = {a: sorted(v) for a, v in by_apn.items() if len(v) >= 2 and v[0][0] != v[-1][0]}
print(f"\nAPNs with 2+ priced transfers in different years: {len(rep):,}")
lag = 0; tot = 0
for a, v in rep.items():
    (y1, p1), (y2, p2) = v[0], v[-1]
    traj = p1 * (1.02 ** (y2 - y1))
    tot += 1
    if p2 < traj:
        lag += 1
print(f"pairs where resale lagged the 2%-trajectory: {lag}/{tot} ({100*lag/max(1,tot):.1f}%)")

json.dump({
    "n_priced_transfers": len(sales),
    "n_2021_22_buyers": len(A), "n_benchmark_sales": len(B),
    "pooled_gap": g0, "pooled_gap_ci95": [ds[25], ds[975]],
    "by_zip": [{"zip": z, "gap": g, "n_buy": n1, "n_sales": n2,
                "med_assessed": ma, "med_sale": mb} for g, z, n1, n2, ma, mb in rows],
    "repeat_sale_pairs": tot, "pairs_lagging_trajectory": lag,
}, open(BASE + "/outputs/cohort_gaps_v2.json", "w"), indent=1)
print("wrote outputs/cohort_gaps_v2.json")
