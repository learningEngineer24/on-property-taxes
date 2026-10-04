"""Prop 8 decline-in-value verification, committed and reproducible.

For 2023 single-family buyers (true purchase prices from county transfer
records), detects Prop 8 relief as STRICTLY POST-PURCHASE year-over-year
declines in assessed value:

  1. 2025_to_2026 roll (lien Jan 1, 2025) < 2024_to_2025 roll (lien Jan 1, 2024)
     -- the first roll-to-roll window fully after a 2023 purchase.
  2. Current parcel feed (Oct 2026, ~2026 roll) < 2025_to_2026 roll,
     excluding parcels resold in 2024-25 (a lower value after a resale is a
     transfer reassessment, not Prop 8).

Windows that are NOT counted (and why):
  - 2023_to_2024 roll (lien Jan 1, 2023) predates any 2023 purchase: it shows
    the SELLER's assessed value. A "cut" there means the buyer paid less than
    the seller's old AV -- transfer-driven, not Prop 8.
  - Pre-2023 windows: the seller's history, not the buyer's.

CORRECTS the earlier 27.2% figure (computed in an ephemeral script, never
committed), which swept in transfer-driven and seller-history declines.
"""
import json
import os
from collections import Counter
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
ROLL_24 = "2024_to_2025"   # lien Jan 1, 2024 -- first post-purchase roll for 2023 buyers
ROLL_25 = "2025_to_2026"   # lien Jan 1, 2025

def load_roll(y):
    d = {}
    for line in open(f"{BASE}/data/taxroll_{y}.jsonl"):
        r = json.loads(line)
        v, p = r.get("Total_Net_Value"), (r.get("Print_Parcel") or "").strip()
        if v and p:
            d[p] = v
    return d

r24, r25 = load_roll(ROLL_24), load_roll(ROLL_25)
print(f"roll24: {len(r24):,} values; roll25: {len(r25):,} values")
cur = {}
for line in open(f"{BASE}/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    if a and r.get("TotalNetValue"):
        cur[a] = r["TotalNetValue"]

# 2023 SFR buyers + 2024-25 resales (to exclude)
seen, buyers, resold = set(), {}, set()
for line in open(f"{BASE}/data/transfers.jsonl"):
    r = json.loads(line)
    apn = (r.get("apn") or "").strip()
    v = (r.get("value_from_trans_tax") or "").strip().rstrip(".")
    key = (apn, r.get("transfer_dt"), v)
    if key in seen or not v or not apn:
        continue
    seen.add(key)
    try:
        price = float(v)
        y = date.fromtimestamp(int(r["transfer_dt"]) / 1000).year
    except Exception:
        continue
    if price < 50000 or (r.get("use_cd") or "").strip() != "1100":
        continue
    if y == 2023 and apn in cur:
        buyers[apn] = price
    elif y in (2024, 2025):
        resold.add(apn)
print(f"2023 SFR buyers: {len(buyers):,}")

cut_roll25, cut_2026, depths = set(), set(), []
for apn in buyers:
    v24, v25, vc = r24.get(apn), r25.get(apn), cur.get(apn)
    if v24 and v25 and v25 < v24:
        cut_roll25.add(apn)
        depths.append((v24 - v25) / v24)
    if v25 and vc and vc < v25 * 0.99 and apn not in resold:
        cut_2026.add(apn)
        depths.append((v25 - vc) / v25)

union = cut_roll25 | cut_2026
depths.sort()
n = len(buyers)
print(f"post-purchase cut in 2025 roll (2025<2024): {len(cut_roll25):,} ({100*len(cut_roll25)/n:.1f}%)")
print(f"cut in 2026 cycle (parcel feed < 2025 roll, excl {len(resold & set(buyers))} resales): "
      f"{len(cut_2026):,} ({100*len(cut_2026)/n:.1f}%)")
print(f"UNION with Prop 8 relief: {len(union):,} ({100*len(union)/n:.1f}%)")
if depths:
    print(f"median cut depth: {100*depths[len(depths)//2]:.1f}%")

# sanity: HOEX-band check (a new $7k homeowner exemption reads as a "cut")
hoex_band = sum(1 for apn in cut_2026
                if 5500 <= (r25.get(apn, 0) - cur.get(apn, 0)) <= 8500)
print(f"2026-cycle cuts in the $5.5k-$8.5k HOEX band: {hoex_band} (negligible if ~0)")

json.dump({
    "n_buyers": n,
    "cut_2025_roll": len(cut_roll25),
    "cut_2026_cycle": len(cut_2026),
    "union": len(union),
    "union_share": len(union) / n,
    "median_cut_depth": depths[len(depths) // 2] if depths else None,
    "hoex_band_cuts": hoex_band,
    "definition": "strictly post-purchase YoY declines; 2026 cycle excludes 2024-25 resales",
}, open(f"{BASE}/outputs/prop8_verified.json", "w"), indent=1)
print("wrote outputs/prop8_verified.json")
