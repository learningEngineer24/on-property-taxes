"""Per-parcel assessment trajectories from annual secured tax rolls.

For 2023 single-family buyers (priced transfers): trace Total_Net_Value
across tax-roll years, detect Prop 8 decline-in-value reductions
(year-over-year nominal cuts, or assessed below purchase price).

Also traces the user's own parcel for the write-up.
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
YEARS = ["2019_to_2020", "2020_to_2021", "2021_to_2022", "2022_to_2023",
         "2023_to_2024", "2024_to_2025", "2025_to_2026"]
YEAR_LABEL = {"2019_to_2020": "2019", "2020_to_2021": "2020", "2021_to_2022": "2021",
              "2022_to_2023": "2022", "2023_to_2024": "2023", "2024_to_2025": "2024",
              "2025_to_2026": "2025"}

# APN -> OBJECTID (for parcel-file lookups)
apn2oid = {}
for line in open(f"{BASE}/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    if a:
        apn2oid.setdefault(a, r.get("OBJECTID"))

# tax rolls -> {year: {apn: total_net_value}}  (join key: APN == Print_Parcel)
rolls = {}
have_years = []
for y in YEARS:
    vals = {}
    try:
        f = open(f"{BASE}/data/taxroll_{y}.jsonl")
    except FileNotFoundError:
        continue
    n = 0
    for line in f:
        r = json.loads(line)
        v = r.get("Total_Net_Value")
        p = (r.get("Print_Parcel") or "").strip()
        if v and p:
            vals[p] = v
            n += 1
    f.close()
    rolls[y] = vals
    have_years.append(y)
    print(f"{y}: {n:,} parcel values")

# 2023 SFR priced transfers (same filter as cohort_gaps_v3)
from datetime import date as _date
seen = set()
buyers = []
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
        y = _date.fromtimestamp(int(r["transfer_dt"]) / 1000).year
    except Exception:
        continue
    if price < 50000:
        continue
    if y == 2023 and (r.get("use_cd") or "").strip() == "1100":
        if apn in apn2oid:  # parcel-file match (same check as v3)
            buyers.append({"apn": apn, "price": price,
                           "zip": (r.get("zip_cd") or "").strip()})
print(f"2023 SFR buyers with parcel match: {len(buyers):,}")

# trajectories
trajs, n_cut, n_below_price, cut_depths = [], 0, 0, []
for b in buyers:
    traj = [(YEAR_LABEL[y], rolls[y].get(b["apn"])) for y in have_years]
    vals = [v for _, v in traj if v]
    if len(vals) < 3:
        continue
    # Prop 8: any year-over-year nominal decline
    cuts = [traj[i][0] for i in range(1, len(traj))
            if traj[i][1] and traj[i-1][1] and traj[i][1] < traj[i-1][1]]
    if cuts:
        n_cut += 1
        for i in range(1, len(traj)):
            if traj[i][1] and traj[i-1][1] and traj[i][1] < traj[i-1][1]:
                cut_depths.append((traj[i-1][1] - traj[i][1]) / traj[i-1][1])
    latest = vals[-1]
    if latest < b["price"]:
        n_below_price += 1
    trajs.append({"apn": b["apn"], "price": b["price"], "zip": b["zip"],
                  "traj": traj, "cut_years": cuts})

n = len(trajs)
cut_depths.sort()
print(f"\ntrajectories: {n:,}")
print(f"with >=1 YoY nominal cut (Prop 8): {n_cut:,} ({100*n_cut/n:.1f}%)")
if cut_depths:
    print(f"median cut depth: {100*cut_depths[len(cut_depths)//2]:.1f}%")
print(f"latest assessed below purchase price: {n_below_price:,} ({100*n_below_price/n:.1f}%)")

# user's own parcel
my_traj = [(YEAR_LABEL[y], rolls[y].get("48D-7298-17-2")) for y in have_years]
print(f"\nuser parcel 48D-7298-17-2: {my_traj}")

json.dump({"years": [YEAR_LABEL[y] for y in have_years],
           "n": n, "prop8_share": n_cut / n if n else 0,
           "below_price_share": n_below_price / n if n else 0,
           "median_cut_depth": cut_depths[len(cut_depths)//2] if cut_depths else None,
           "my_traj": my_traj,
           "sample_trajs": trajs[:200]},
          open(f"{BASE}/outputs/trajectories.json", "w"))
print("wrote outputs/trajectories.json")
