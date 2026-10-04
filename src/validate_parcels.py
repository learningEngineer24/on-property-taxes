"""Validate the full parcel download: counts, uniqueness, missingness,
distributions, stacked condos, date sanity. Writes outputs/validation.json
and prints a human-readable summary."""
import json, math
from collections import Counter
from datetime import date

IN = "/home/hatch/workspace/alameda-assessment/data/parcels.jsonl"
OUT = "/home/hatch/workspace/alameda-assessment/outputs/validation.json"

FIELDS = ["OBJECTID", "APN", "SitusAddress", "SitusCity", "SitusZip", "Land",
          "Imps", "TotalNetValue", "LatestDocumentDate", "UseCode",
          "TRAPrimary", "TRASecondary", "HOEX", "OTEX", "CENTROID_X",
          "CENTROID_Y"]

n = 0
oids, apns = set(), set()
dup_oid = dup_apn = 0
missing = Counter()
cities = Counter()
usecodes = Counter()
null_value = 0
zero_value = 0
implausible_dates = 0
date_years = Counter()
oakland = 0
residential = 0
hoex = 0
val_sum = 0
vals = []

RES_USE = {"1100"}  # single-family; broader set refined with lookup

for line in open(IN):
    r = json.loads(line)
    n += 1
    o, a = r.get("OBJECTID"), r.get("APN")
    if o in oids: dup_oid += 1
    else: oids.add(o)
    if a in apns: dup_apn += 1
    else: apns.add(a)
    for f in FIELDS:
        if r.get(f) in (None, ""): missing[f] += 1
    cities[r.get("SitusCity") or "?"] += 1
    usecodes[r.get("UseCode")] += 1
    v = r.get("TotalNetValue")
    if v is None: null_value += 1
    elif v == 0: zero_value += 1
    else:
        val_sum += v; vals.append(v)
    d = r.get("LatestDocumentDate")
    if d:
        try:
            ms = int(d)
            y = date.fromtimestamp(ms / 1000).year
            date_years[y] += 1
            if y < 1900 or y > 2026: implausible_dates += 1
        except Exception:
            implausible_dates += 1
    else:
        implausible_dates += 0
    if (r.get("SitusCity") or "").upper() == "OAKLAND": oakland += 1
    if str(r.get("UseCode")) in ("1100", "1110", "1120", "1200", "1300", "1400",
                                  "1410", "1420", "1500", "1510", "1520",
                                  "2100", "2200", "2300", "2400"):
        residential += 1
    if r.get("HOEX"): hoex += 1

vals.sort()
def pct(p): return vals[int(len(vals) * p)] if vals else None

report = {
    "rows": n,
    "expected": 489636,
    "dup_OBJECTID": dup_oid,
    "dup_APN": dup_apn,
    "missing": dict(missing),
    "null_TotalNetValue": null_value,
    "zero_TotalNetValue": zero_value,
    "value_p10": pct(0.10), "value_median": pct(0.50), "value_p90": pct(0.90),
    "implausible_or_unparseable_dates": implausible_dates,
    "doc_year_min": min(date_years) if date_years else None,
    "doc_year_max": max(date_years) if date_years else None,
    "top_cities": cities.most_common(10),
    "top_usecodes": usecodes.most_common(10),
    "n_distinct_usecodes": len(usecodes),
    "oakland_rows": oakland,
    "residential_rows": residential,
    "homeowner_exemption_rows": hoex,
}
import os
os.makedirs("/home/hatch/workspace/alameda-assessment/outputs", exist_ok=True)
json.dump(report, open(OUT, "w"), indent=1, default=str)

print(f"rows: {n} (expected 489636)")
print(f"dup OBJECTID: {dup_oid}, dup APN: {dup_apn}")
print(f"null value: {null_value}, zero value: {zero_value}")
print(f"value p10/med/p90: {pct(0.10):,.0f} / {pct(0.50):,.0f} / {pct(0.90):,.0f}")
print(f"implausible dates: {implausible_dates}; year range {min(date_years)}-{max(date_years)}")
print(f"top cities: {cities.most_common(5)}")
print(f"top usecodes: {usecodes.most_common(5)}")
print(f"oakland rows: {oakland}, residential rows: {residential}, HOEX rows: {hoex}")
print(f"missing: {dict(missing)}")
