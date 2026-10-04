"""Diagnostic: cut-year distribution + 2025-roll vs current-parcel-feed for 2023 buyers."""
import json
from collections import Counter
from datetime import date

BASE = "/home/hatch/workspace/alameda-assessment"
YEARS = ["2019_to_2020", "2020_to_2021", "2021_to_2022", "2022_to_2023",
         "2023_to_2024", "2024_to_2025", "2025_to_2026"]
YL = {"2019_to_2020": "2019", "2020_to_2021": "2020", "2021_to_2022": "2021",
      "2022_to_2023": "2022", "2023_to_2024": "2023", "2024_to_2025": "2024",
      "2025_to_2026": "2025"}

rolls = {}
for y in YEARS:
    d = {}
    for line in open(f"{BASE}/data/taxroll_{y}.jsonl"):
        r = json.loads(line)
        v, p = r.get("Total_Net_Value"), (r.get("Print_Parcel") or "").strip()
        if v and p:
            d[p] = v
    rolls[y] = d

cur = {}
for line in open(f"{BASE}/data/parcels.jsonl"):
    r = json.loads(line)
    a = (r.get("APN") or "").strip()
    v = r.get("TotalNetValue")
    if a and v:
        cur[a] = v

seen, buyers = set(), []
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
    if price >= 50000 and y == 2023 and (r.get("use_cd") or "").strip() == "1100":
        if apn in cur:
            buyers.append((apn, price))

cut_years = Counter()
below_2025, below_cur, n = 0, 0, 0
chg = []
for apn, price in buyers:
    traj = [(YL[y], rolls[y].get(apn)) for y in YEARS]
    vals = [vv for _, vv in traj if vv]
    if len(vals) < 5:
        continue
    n += 1
    for i in range(1, len(traj)):
        if traj[i][1] and traj[i-1][1] and traj[i][1] < traj[i-1][1]:
            cut_years[traj[i][0]] += 1
    v25 = traj[-1][1]
    vc = cur.get(apn)
    if v25 and v25 < price:
        below_2025 += 1
    if vc and vc < price:
        below_cur += 1
    if v25 and vc:
        chg.append(vc / v25 - 1)

chg.sort()
print(f"buyers with full traj: {n:,}")
print("cut-year distribution:", dict(sorted(cut_years.items())))
print(f"below price in 2025 roll: {below_2025:,} ({100*below_2025/n:.1f}%)")
print(f"below price in current parcel feed: {below_cur:,} ({100*below_cur/n:.1f}%)")
print(f"parcel-feed vs 2025-roll change: p50={100*chg[len(chg)//2]:+.1f}%, "
      f"p25={100*chg[len(chg)//4]:+.1f}%, p75={100*chg[3*len(chg)//4]:+.1f}%")
# how many got a NEW cut between 2025 roll and parcel feed?
newcut = sum(1 for apn, price in buyers
             if (lambda v25, vc: v25 and vc and vc < v25 * 0.99)(
                 rolls["2025_to_2026"].get(apn), cur.get(apn)))
print(f"parcel-feed value >1% below 2025-roll value: {newcut:,}")
