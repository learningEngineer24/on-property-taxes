"""Per-parcel effective property tax rates, v1.

effective_rate = (TotalNetValue * TRA_advalorem_rate) / market_value
market_value  = ZIP-level median 2024-25 transfer price, matched on property
                type (SFR=1100 uses 1100 medians; others use type medians;
                fallback: ZIP overall -> county median).
Prop 8 flags come from the paired 2023 analysis (assessed < purchase price).

Writes outputs/effective_rates.json (cohort aggregates) and
outputs/parcel_effective_rates.jsonl (SFR parcels only).
"""
import json
import os
from collections import defaultdict
from datetime import date

# ---------- transfer medians by (zip, type) ----------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
seen = set()
px = defaultdict(list)
for line in open(BASE + "/data/transfers.jsonl"):
    r = json.loads(line)
    apn = (r.get("apn") or "").strip()
    v = (r.get("value_from_trans_tax") or "").strip().rstrip(".")
    key = (apn, r.get("transfer_dt"), v)
    if key in seen:
        continue
    seen.add(key)
    if not v:
        continue
    try:
        p = float(v)
        y = date.fromtimestamp(int(r["transfer_dt"]) / 1000).year
    except Exception:
        continue
    if p < 50000 or y not in (2024, 2025):
        continue
    z = (r.get("zip_cd") or "").strip()
    uc = (r.get("use_cd") or "").strip()
    if z:
        px[(z, uc)].append(p)
        px[(z, "*")].append(p)

def med(s):
    s = sorted(s)
    return s[len(s) // 2] if s else None

med_by_zt = {k: med(v) for k, v in px.items() if len(v) >= 10}
allp = [p for (z, u), ps in px.items() if u != "*" for p in ps]
county_med = med(allp)
print(f"county 2024-25 transfer median: ${county_med:,.0f}")

# ---------- TRA rates (int-normalized keys: '26:023' -> '26:23') ----------
tra_raw = json.load(open(BASE + "/data/tra_rates_combined.json"))["combined"]
tra = {}
for k, v in tra_raw.items():
    p, s = k.split(":")
    tra[f"{int(p)}:{int(s)}"] = v

# ---------- Prop 8 flags (paired 2023) ----------
seen2 = set()
buy2023 = {}
for line in open(BASE + "/data/transfers.jsonl"):
    r = json.loads(line)
    apn = (r.get("apn") or "").strip()
    v = (r.get("value_from_trans_tax") or "").strip().rstrip(".")
    key = (apn, r.get("transfer_dt"), v)
    if key in seen2:
        continue
    seen2.add(key)
    if not v:
        continue
    try:
        p = float(v)
        y = date.fromtimestamp(int(r["transfer_dt"]) / 1000).year
    except Exception:
        continue
    if p >= 50000 and y == 2023 and (r.get("use_cd") or "").strip() == "1100":
        buy2023[apn] = p

# ---------- per-parcel rates ----------
cohort_rates = defaultdict(list)
n, n_nomarket, n_norate = 0, 0, 0
prop8_flags = []
out = open(BASE + "/outputs/parcel_effective_rates.jsonl", "w")
for line in open(BASE + "/data/parcels.jsonl"):
    r = json.loads(line)
    if r.get("UseCode") != "1100":
        continue
    av = r.get("TotalNetValue")
    if not av:
        continue
    z = (r.get("SitusZip") or "").strip()
    mkt = med_by_zt.get((z, "1100")) or med_by_zt.get((z, "*")) or county_med
    if not mkt:
        n_nomarket += 1
        continue
    try:
        p, s = r.get("TRAPrimary"), r.get("TRASecondary")
        rate = tra.get(f"{int(p)}:{int(s)}") if p is not None and s is not None else None
    except (ValueError, TypeError):
        rate = None
    if not rate:
        n_norate += 1
        continue
    eff = av * rate / mkt
    n += 1
    d = r.get("LatestDocumentDate")
    try:
        y = date.fromtimestamp(int(d) / 1000).year if d else None
    except Exception:
        y = None
    coh = "pre1990" if y and y < 1990 else f"{y//10*10}s" if y else "unknown"
    if y and y >= 2020:
        coh = str(y)
    cohort_rates[coh].append(eff)
    apn = (r.get("APN") or "").strip()
    p8 = apn in buy2023 and av < buy2023[apn]
    if p8:
        prop8_flags.append(apn)
    out.write(json.dumps({"apn": apn, "zip": z, "assessed": av,
                          "tra_rate": rate, "market": mkt,
                          "eff_rate": round(eff, 5), "doc_year": y,
                          "prop8": p8}, separators=(",", ":")) + "\n")
out.close()

print(f"\nSFR parcels rated: {n:,} (no market: {n_nomarket}, no TRA rate: {n_norate})")
print(f"Prop 8 flags: {len(prop8_flags):,}")
print("\nmedian effective rate by cohort:")
for c in sorted(cohort_rates):
    s = sorted(cohort_rates[c])
    print(f"  {c:>8}: n={len(s):>7,}  median={100*s[len(s)//2]:.3f}%  "
          f"p90={100*s[int(len(s)*0.9)]:.3f}%")

json.dump({
    "n_rated": n,
    "prop8_flags": len(prop8_flags),
    "by_cohort": {c: {"n": len(v), "median": sorted(v)[len(v)//2],
                      "p90": sorted(v)[int(len(v)*0.9)]}
                  for c, v in sorted(cohort_rates.items())},
}, open(BASE + "/outputs/effective_rates.json", "w"), indent=1)
print("wrote outputs/effective_rates.json + parcel_effective_rates.jsonl")
