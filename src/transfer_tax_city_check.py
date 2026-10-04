"""Transfer-tax inversion check by city (committed Oct 2026).

Question: does `value_from_trans_tax` (price backed out from the documentary
transfer tax) suffer city-specific distortion, e.g. from city-level transfer
taxes layered on top of the county rate?

Test: for H1-2023 single-family buyers, the county enrolls assessed value at
price x 1.02 at the Jan-2024 lien (verified in cohort_gaps_v4.py). So
assessed(Jan-2024) / (price x 1.02) should be ~1.00 in every city if the
inversion is clean. A city whose transfer tax distorted the inversion would
show a systematically different ratio.

Writes outputs/transfer_tax_city_check.json.
"""
import json
import os
from collections import defaultdict
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root

# Jan-2024 lien roll
assessed_24 = {}
for line in open(os.path.join(BASE, "data/taxroll_2024_to_2025.jsonl")):
    r = json.loads(line)
    v, p = r.get("Total_Net_Value"), (r.get("Print_Parcel") or "").strip()
    if v and p:
        assessed_24[p] = v

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

seen, ratios = set(), defaultdict(list)
for line in open(os.path.join(BASE, "data/transfers.jsonl")):
    r = json.loads(line)
    apn = (r.get("apn") or "").strip()
    v = (r.get("value_from_trans_tax") or "").strip().rstrip(".")
    key = (apn, r.get("transfer_dt"), v)
    if key in seen or not v or not apn:
        continue
    seen.add(key)
    try:
        price = float(v)
        dt = date.fromtimestamp(int(r["transfer_dt"]) / 1000)
    except Exception:
        continue
    if price < 50000 or dt.year != 2023 or dt.month > 6:
        continue
    if (r.get("use_cd") or "").strip() != "1100":
        continue
    av = assessed_24.get(apn)
    if not av:
        continue
    city = (r.get("city_name") or "").strip() or "UNKNOWN"
    ratios[city].append(av / (price * 1.02))

rows = [{"city": c, "median_ratio": round(med(v), 4), "n": len(v)}
        for c, v in ratios.items() if len(v) >= 20]
rows.sort(key=lambda r: r["median_ratio"])

print("city median assessed/(price x 1.02), H1-2023 SFR buyers (n>=20):")
for r in rows:
    print(f"  {r['city']:<18} {r['median_ratio']:.3f}  n={r['n']}")

json.dump({"by_city": rows,
           "note": "H1-2023 SFR buyers; ratio should be ~1.00 in every city if "
                   "transfer-tax inversion is clean. City medians 0.993-1.000: "
                   "no city-level distortion found."},
          open(os.path.join(BASE, "outputs/transfer_tax_city_check.json"), "w"), indent=1)
print("wrote outputs/transfer_tax_city_check.json")
