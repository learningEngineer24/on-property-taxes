"""v4 gap analysis — corrects v3's uniform 1.02^3 trajectory factor.

CORRECTION (Oct 2026, from independent review, verified against tax rolls):
the county does NOT apply the 2% inflation factor at the first lien date for
all buyers. Measured on 2023 transfers joined to the Jan-2024 roll:
  - transfers recorded Apr-Jun 2023: ~88% enrolled at x1.02
  - transfers recorded Jul-Dec 2023: ~88-96% enrolled at x1.00
(the assessment-roll close, ~Jun 30, determines which base lien date applies).
Correct Prop 13 trajectory to the Jan-2026 lien ("assessed today"):
  - H1-2023 buyers (month <= 6): price x 1.02^3
  - H2-2023 buyers (month >= 7):  price x 1.02^2
v3 applied 1.02^3 to everyone, overstating expected AV ~2% for ~60% of buyers.

Also new in v4: two views of uncertainty. (1) A simple bootstrap of the pooled
medians, which quantifies SAMPLING NOISE ONLY (v3's independent resampling
also ignored within-ZIP correlation). A ZIP-block bootstrap of the pooled
median is deliberately NOT used: ZIP price levels differ enormously, so the
pooled median is not a block-coherent estimand (resampling ZIPs explodes the
CI to +/-$200k). (2) The coherent alternative: the median ZIP-level gap, with
a ZIP-block bootstrap CI -- here ZIPs ARE the units, so block resampling is
valid.
"""
import json, random
import os
from collections import defaultdict
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root

def factor_2023(month):
    return 1.02 ** 3 if month <= 6 else 1.02 ** 2

# ---------- deduped priced transfers ----------
seen = set()
tr = []
for line in open(f"{BASE}/data/transfers.jsonl"):
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
        dt = date.fromtimestamp(int(r["transfer_dt"]) / 1000)
    except Exception:
        continue
    if price < 50000:
        continue
    if (r.get("use_cd") or "").strip() != "1100":
        continue
    tr.append({"apn": apn, "y": dt.year, "m": dt.month, "price": price,
               "zip": (r.get("zip_cd") or "").strip()})
print(f"unique priced SFR transfers: {len(tr):,}")

# ---------- parcels: assessed today by APN ----------
assessed_by_apn = {}
for line in open(f"{BASE}/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    v = r.get("TotalNetValue")
    if a and v:
        assessed_by_apn[a] = v

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

# ---------- (a) paired 2023, corrected factors ----------
ratios, below = [], 0
n = 0
for t in tr:
    if t["y"] != 2023:
        continue
    av = assessed_by_apn.get(t["apn"])
    if not av:
        continue
    n += 1
    ratios.append(av / (t["price"] * factor_2023(t["m"])))
    if av < t["price"]:
        below += 1
ratios.sort()
r50 = ratios[len(ratios) // 2]
print(f"(a) PAIRED 2023 corrected: n={n:,}, median AV/expected={r50:.3f}, "
      f"below price: {below:,} ({100*below/n:.1f}%)")

# ---------- (b) clean cross-section, corrected factors ----------
A_by_zip = defaultdict(list)  # 2023 factored values
B_by_zip = defaultdict(list)  # 2024-25 true prices
for t in tr:
    if not t["zip"]:
        continue
    if t["y"] == 2023:
        A_by_zip[t["zip"]].append(t["price"] * factor_2023(t["m"]))
    elif t["y"] in (2024, 2025):
        B_by_zip[t["zip"]].append(t["price"])

A = [v for vs in A_by_zip.values() for v in vs]
B = [v for vs in B_by_zip.values() for v in vs]
g0 = med(A) - med(B)
print(f"(b) pooled: n_buy={len(A):,}, n_sales={len(B):,}, "
      f"gap=${g0:+,.0f} ({100*g0/med(B):+.1f}%)")

# Uncertainty, two views.
# (1) Simple bootstrap of the pooled medians: quantifies SAMPLING NOISE ONLY.
#     It excludes composition-shift risk (different homes sold in each window)
#     and within-ZIP correlation, so treat it as a lower bound on uncertainty.
#     (A ZIP-block bootstrap of the pooled median explodes to ±$200k because
#     ZIP price levels differ enormously and the resample mixes them — the
#     pooled median is not a block-coherent estimand. See notes.)
random.seed(11)
ds = sorted(med([random.choice(A) for _ in range(len(A))])
             - med([random.choice(B) for _ in range(len(B))]) for _ in range(1000))
print(f"    simple bootstrap 95% CI (sampling noise only): [${ds[25]:+,.0f}, ${ds[975]:+,.0f}]")

# (2) Robustness: median ZIP-level gap, with ZIP-block bootstrap CI.
#     Here ZIPs ARE the units, so block resampling is coherent.
#     (per-ZIP table is computed below; inline the needed values here)
ztmp = []
for z, vs in A_by_zip.items():
    bs = B_by_zip.get(z, [])
    if len(vs) >= 20 and len(bs) >= 20:
        ztmp.append(med(vs) - med(bs))
ztmp.sort()
zgaps_boot = []
for _ in range(1000):
    s = sorted(random.choice(ztmp) for _ in range(len(ztmp)))
    zgaps_boot.append(s[len(s) // 2])
zgaps_boot.sort()
print(f"    median ZIP gap: ${med(ztmp):+,.0f}; "
      f"block-bootstrap 95% CI: [${zgaps_boot[25]:+,.0f}, ${zgaps_boot[975]:+,.0f}]")

# per-ZIP gaps (min 20 each side), corrected factors
rows = []
for z, vs in A_by_zip.items():
    bs = B_by_zip.get(z, [])
    if len(vs) >= 20 and len(bs) >= 20:
        m1, m2 = med(vs), med(bs)
        rows.append({"zip": z, "gap": m1 - m2, "gap_pct": 100 * (m1 - m2) / m2,
                     "n23": len(vs), "n2425": len(bs)})
rows.sort(key=lambda r: r["gap"], reverse=True)
print("(b) top/bottom ZIP gaps:")
for r in rows[:5] + rows[-3:]:
    print(f"    {r['zip']}: ${r['gap']:+,.0f} ({r['gap_pct']:+.1f}%) n23={r['n23']} n2425={r['n2425']}")

json.dump({
    "paired_2023_corrected": {"n": n, "ratio_p50": r50,
                              "below_price": below, "below_price_share": below / n},
    "clean_2023_vs_2024_25": {"gap": g0, "gap_pct": 100 * g0 / med(B),
                              "ci95_simple": [ds[25], ds[975]],
                              "ci95_simple_note": "sampling noise of the medians only; "
                              "excludes composition-shift risk and within-ZIP correlation",
                              "median_zip_gap": med(ztmp),
                              "median_zip_gap_ci95_block": [zgaps_boot[25], zgaps_boot[975]],
                              "n_buy": len(A), "n_sales": len(B)},
    "by_zip": rows,
    "note": "v4 corrects v3's uniform 1.02^3 factor (H1-2023 buyers 1.02^3, "
            "H2-2023 buyers 1.02^2, verified against the Jan-2024 roll); "
            "simple CI covers sampling noise only",
}, open(f"{BASE}/outputs/cohort_gaps_v4.json", "w"), indent=1)
print("wrote outputs/cohort_gaps_v4.json")
