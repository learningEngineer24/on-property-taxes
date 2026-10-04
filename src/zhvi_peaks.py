"""ZIP-level price peaks from Zillow ZHVI (smoothed, seasonally adjusted, monthly).

Shows the 2021-22 peak directly: for each Alameda County ZIP, finds the
post-2019 peak month and the drawdown since. Cross-checks the county
transfer-price ZIP divergence found in cohort_gaps_v3.
"""
import csv, json
from datetime import date

SRC = "data/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
OUT_SUMMARY = "outputs/zhvi_zip_peaks.json"
OUT_SERIES = "outputs/zhvi_zip_series.json"

def parse(v):
    v = v.strip()
    return float(v) if v else None

with open(SRC, newline="") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    date_cols = [i for i, h in enumerate(header) if h[:4].isdigit()]
    dates = [header[i] for i in date_cols]
    rows = [r for r in rdr if len(r) > 9 and r[8] == "Alameda County"]

print(f"Alameda ZIPs: {len(rows)}; months: {dates[0]}..{dates[-1]}")

summary, series = [], {}
for r in rows:
    zipc, city = r[2], r[6]
    vals = [(dates[k], parse(r[i])) for k, i in enumerate(date_cols) if i < len(r)]
    vals = [(d, v) for d, v in vals if v]
    if not vals:
        continue
    # post-2019 peak
    recent = [(d, v) for d, v in vals if d >= "2019-01-31"]
    peak_d, peak_v = max(recent, key=lambda t: t[1])
    last_d, last_v = vals[-1]
    # 2022-06 and 2024-12 reference points
    def at(target):
        c = [(d, v) for d, v in vals if d <= target]
        return c[-1] if c else (None, None)
    d22, v22 = at("2022-06-30")
    d24, v24 = at("2024-12-31")
    summary.append({
        "zip": zipc, "city": city,
        "peak_date": peak_d, "peak_value": round(peak_v),
        "latest_date": last_d, "latest_value": round(last_v),
        "drawdown_from_peak_pct": round((last_v - peak_v) / peak_v * 100, 1),
        "jun2022_value": round(v22) if v22 else None,
        "dec2024_value": round(v24) if v24 else None,
        "dec2024_vs_jun2022_pct": round((v24 - v22) / v22 * 100, 1) if v22 and v24 else None,
    })
    series[zipc] = {"city": city, "dates": [d for d, _ in vals],
                    "values": [round(v) for _, v in vals]}

summary.sort(key=lambda s: s["drawdown_from_peak_pct"])
with open(OUT_SUMMARY, "w") as f:
    json.dump(summary, f, indent=1)
with open(OUT_SERIES, "w") as f:
    json.dump(series, f)

# headline stats
n = len(summary)
peaked_2022 = sum(1 for s in summary if s["peak_date"] and s["peak_date"].startswith("2022"))
med_dd = sorted(s["drawdown_from_peak_pct"] for s in summary)[n // 2]
print(f"ZIPs peaking in 2022: {peaked_2022}/{n}; median drawdown from peak: {med_dd}%")
print("\nDeepest drawdowns:")
for s in summary[:8]:
    print(f"  {s['zip']} ({s['city']}): peak {s['peak_date']} ${s['peak_value']:,}, "
          f"now ${s['latest_value']:,} ({s['drawdown_from_peak_pct']}%)")
print("\nSmallest drawdowns / still rising:")
for s in summary[-6:]:
    print(f"  {s['zip']} ({s['city']}): peak {s['peak_date']} ${s['peak_value']:,}, "
          f"now ${s['latest_value']:,} ({s['drawdown_from_peak_pct']}%)")
# spotlight ZIPs from the transfer analysis
for z in ["94705", "94609", "94610", "94611", "94539", "94555"]:
    s = next((x for x in summary if x["zip"] == z), None)
    if s:
        print(f"\n{z}: peak {s['peak_date']} ${s['peak_value']:,}; "
              f"Jun22->Dec24 {s['dec2024_vs_jun2022_pct']}%; drawdown {s['drawdown_from_peak_pct']}%")
