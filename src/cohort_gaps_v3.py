"""v3 gap analysis with clean identification.

NOTE (Oct 2026): the identification here is correct, but v3 applies a uniform
1.02^3 Prop 13 trajectory to all 2023 buyers. The county's rolls show H1-2023
buyers enroll at x1.02 at the first lien while H2-2023 buyers enroll at x1.00 --
see cohort_gaps_v4.py, which corrects the factor (H1: 1.02^3, H2: 1.02^2) and
supersedes v3's gap numbers. Kept for the audit trail.

(a) PAIRED 2023 (user's design, executable): APNs with a priced 2023 SFR
    transfer -> join parcel assessed value today -> compare against
    price * 1.02^3 (the Prop 13 trajectory). Flags Prop 8 reductions.
(b) CLEAN CROSS-SECTION: 2023 buyers' factored values (price*1.02^3, from the
    transfer list) vs 2024-25 true sale prices (transfer list), by ZIP.
    Both sides are true prices -- no refinance contamination possible.
(c) 2022-only parcel buyer cohort vs 2024-25 true prices (peak question;
    refi contamination biases this DOWN => lower bound on over-assessment).
"""
import json, random
from collections import defaultdict
from datetime import date

# ---------- deduped priced transfers ----------
seen = set()
tr = []  # dicts
for line in open("/home/hatch/workspace/alameda-assessment/data/transfers.jsonl"):
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
    if price < 50000:
        continue
    tr.append({"apn": apn, "y": y, "price": price,
               "zip": (r.get("zip_cd") or "").strip(),
               "uc": (r.get("use_cd") or "").strip()})
print(f"unique priced transfers: {len(tr):,}")

# ---------- parcels: assessed by APN + 2022 buyer cohort ----------
assessed_by_apn = {}
c2022 = defaultdict(list)
for line in open("/home/hatch/workspace/alameda-assessment/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    v = r.get("TotalNetValue")
    if a and v:
        assessed_by_apn[a] = v
    if r.get("UseCode") != "1100" or not v:
        continue
    d = r.get("LatestDocumentDate")
    if not d:
        continue
    try:
        y = date.fromtimestamp(int(d) / 1000).year
    except Exception:
        continue
    if y == 2022:
        c2022[(r.get("SitusZip") or "").strip()].append(v)

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

# ---------- (a) paired 2023 ----------
ratios = []
prop8 = 0
n = 0
for t in tr:
    if t["y"] != 2023 or t["uc"] != "1100":
        continue
    av = assessed_by_apn.get(t["apn"])
    if not av:
        continue
    n += 1
    expected = t["price"] * (1.02 ** 3)
    ratios.append(av / expected)
    if av < t["price"]:
        prop8 += 1
ratios.sort()
print(f"\n(a) PAIRED 2023: {n:,} SFR homes, assessed_today / (price*1.02^3):")
for q in [0.05, 0.25, 0.5, 0.75, 0.95]:
    print(f"    p{int(q*100):>3}: {ratios[int(len(ratios)*q)]:.3f}")
print(f"    assessed BELOW purchase price (Prop 8 cut): {prop8:,} ({100*prop8/n:.1f}%)")

# ---------- (b) clean cross-section ----------
b23 = defaultdict(list)   # zip -> factored 2023 values
b2425 = defaultdict(list) # zip -> true 2024-25 prices
for t in tr:
    if t["uc"] != "1100" or not t["zip"]:
        continue
    if t["y"] == 2023:
        b23[t["zip"]].append(t["price"] * (1.02 ** 3))
    elif t["y"] in (2024, 2025):
        b2425[t["zip"]].append(t["price"])

print("\n(b) 2023 buyers' factored value vs TRUE 2024-25 prices, by ZIP (min 20 each):")
rows = []
for z, v23 in b23.items():
    v25 = b2425.get(z, [])
    if len(v23) >= 20 and len(v25) >= 20:
        m23, m25 = med(v23), med(v25)
        rows.append((m23 - m25, z, len(v23), len(v25), m23, m25))
rows.sort(reverse=True)
for g, z, n1, n2, m1, m2 in rows[:10]:
    print(f"    {z}: gap=${g:+,.0f} ({100*g/m2:+.1f}%)  buy23 n={n1} | sales24-25 n={n2}")
print("    ...")
for g, z, n1, n2, m1, m2 in rows[-5:]:
    print(f"    {z}: gap=${g:+,.0f} ({100*g/m2:+.1f}%)  buy23 n={n1} | sales24-25 n={n2}")

A = [t["price"] * (1.02 ** 3) for t in tr if t["y"] == 2023 and t["uc"] == "1100"]
B = [t["price"] for t in tr if t["y"] in (2024, 2025) and t["uc"] == "1100"]
random.seed(5)
g0 = med(A) - med(B)
ds = sorted(med([random.choice(A) for _ in range(len(A))])
            - med([random.choice(B) for _ in range(len(B))]) for _ in range(1000))
print(f"    pooled: 2023 buyers n={len(A):,} vs 2024-25 sales n={len(B):,}: "
      f"gap=${g0:+,.0f} ({100*g0/med(B):+.1f}%), 95% CI [${ds[25]:+,.0f}, ${ds[975]:+,.0f}]")

# ---------- (c) 2022-only parcel cohort vs true prices ----------
cA = [v for vs in c2022.values() for v in vs]
g1 = med(cA) - med(B)
random.seed(6)
ds1 = sorted(med([random.choice(cA) for _ in range(len(cA))])
             - med([random.choice(B) for _ in range(len(B))]) for _ in range(1000))
print(f"\n(c) 2022 parcel-buyer cohort (n={len(cA):,}, refi-contaminated => lower bound) "
      f"vs true 2024-25 sales: gap=${g1:+,.0f} ({100*g1/med(B):+.1f}%), "
      f"95% CI [${ds1[25]:+,.0f}, ${ds1[975]:+,.0f}]")

json.dump({
    "paired_2023": {"n": n, "ratio_p50": ratios[len(ratios)//2],
                    "prop8_cuts": prop8, "prop8_share": prop8/n},
    "clean_2023_vs_2024_25": {"gap": g0, "ci95": [ds[25], ds[975]],
                              "n_buy": len(A), "n_sales": len(B)},
    "cohort_2022_vs_true": {"gap": g1, "ci95": [ds1[25], ds1[975]], "n_buy": len(cA)},
    "by_zip_b": [{"zip": z, "gap": g, "n23": n1, "n2425": n2} for g, z, n1, n2, m1, m2 in rows],
}, open("/home/hatch/workspace/alameda-assessment/outputs/cohort_gaps_v3.json", "w"), indent=1)
print("\nwrote outputs/cohort_gaps_v3.json")
