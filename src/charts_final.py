"""Final charts for the write-up:
1. Post-purchase assessment trajectories (2023-buyer cohort median+IQR, Prop 13 2% line, user's parcel)
2. Effective tax rate by purchase cohort
3. ZIP price change vs over-assessment gap
"""
import json
import os
from collections import defaultdict
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
plt.rcParams.update({"font.size": 10})

# ---------- 1. trajectories ----------
rolls = {}
for y in ["2024_to_2025", "2025_to_2026"]:
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
    if a and r.get("TotalNetValue"):
        cur[a] = r["TotalNetValue"]

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
        dt = date.fromtimestamp(int(r["transfer_dt"]) / 1000)
    except Exception:
        continue
    if price >= 50000 and dt.year == 2023 and (r.get("use_cd") or "").strip() == "1100":
        buyers.append((apn, price, dt.month))

def pct(vals, q):
    s = sorted(vals); return s[int(len(s) * q)]

# split by transfer half: H1 buyers get the 2% factor at the Jan-2024 lien, H2 don't
series_h1 = defaultdict(list)
series_h2 = defaultdict(list)
for apn, price, m in buyers:
    v24, v25, vc = rolls["2024_to_2025"].get(apn), rolls["2025_to_2026"].get(apn), cur.get(apn)
    if v24 and v25 and vc:
        s = series_h1 if m <= 6 else series_h2
        s["2023 purchase"].append(100.0)
        s["Jan 2024"].append(v24 / price * 100)
        s["Jan 2025"].append(v25 / price * 100)
        s["Jan 2026"].append(vc / price * 100)

labels = ["2023 purchase", "Jan 2024", "Jan 2025", "Jan 2026"]
med_h1 = [pct(series_h1[l], 0.5) for l in labels]
med_h2 = [pct(series_h2[l], 0.5) for l in labels]
p25 = [pct(series_h1[l] + series_h2[l], 0.25) for l in labels]
p75 = [pct(series_h1[l] + series_h2[l], 0.75) for l in labels]
# Prop 13 trajectories as actually applied: H1 -> x1.02 at first lien; H2 -> x1.00
two_h1 = [100, 102, 104.04, 106.12]
two_h2 = [100, 100, 102, 104.04]
# user's parcel, indexed to 2022 reassessed base 1,706,600 (purchase-year proxy).
# x positions on the cohort calendar axis: -1 = 2022 (his purchase year)
nebo = {"2022 purchase": 100.0, "Jan 2023": 1740871/1706600*100,
        "Jan 2024": 1600000/1706600*100, "Jan 2025": 1632000/1706600*100,
        "Jan 2026": 1664640/1706600*100}
nebo_order = ["2022 purchase", "Jan 2023", "Jan 2024", "Jan 2025", "Jan 2026"]
nebo_x = [-1, 0, 1, 2, 3]

fig, ax = plt.subplots(figsize=(10, 5.5))
x = list(range(4))
n_h1, n_h2 = len(series_h1["2023 purchase"]), len(series_h2["2023 purchase"])
ax.fill_between(x, p25, p75, alpha=0.18, label="2023 buyers: interquartile range (pooled)")
ax.plot(x, med_h1, "o-", linewidth=2.2,
        label=f"2023 H1 buyers: median (n={n_h1})")
ax.plot(x, med_h2, "o-", linewidth=2.2,
        label=f"2023 H2 buyers: median (n={n_h2})")
ax.plot(x, two_h1, "--", color="gray",
        label="Prop 13 trajectory as applied: H1 buyers (x1.02 at first lien)")
ax.plot(x, two_h2, ":", color="gray",
        label="Prop 13 trajectory as applied: H2 buyers (x1.00 at first lien)")
ax.plot(nebo_x, [nebo[l] for l in nebo_order], "s-", color="#c0392b",
        linewidth=2, label="Example parcel: 2021 buyer, Prop 8 cut in 2024")
ax.set_xticks([-1, 0, 1, 2, 3])
ax.set_xticklabels(["2022\n(example purchase)", "2023\n(example Jan 2023 /\ncohort purchase)", "Jan 2024", "Jan 2025", "Jan 2026"])
ax.set_ylabel("Assessed value / purchase price × 100")
ax.set_title("What happened after the purchase: assessments vs. the Prop 13 trajectory",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(f"{BASE}/outputs/charts/trajectories.png", dpi=150)
print("wrote trajectories.png",
      {l: (round(a, 1), round(b, 1)) for l, a, b in zip(labels, med_h1, med_h2)})

# ---------- 2. effective rate by cohort ----------
er = json.load(open(f"{BASE}/outputs/effective_rates.json"))["by_cohort"]
order = ["pre-1990" if "pre" in k.lower() else k for k in er]
# normalize known cohort keys; drop 2026 (partial year: document-year proxy
# degrades at the right edge -- dominated by non-reset documents)
cats, vals = [], []
for key, disp in [("pre1990", "pre-1990"), ("1990s", "1990s"), ("2000s", "2000s"),
                  ("2010s", "2010s"), ("2020", "2020"), ("2021", "2021"),
                  ("2022", "2022"), ("2023", "2023"), ("2024", "2024"),
                  ("2025", "2025")]:
    if key in er:
        cats.append(disp); vals.append(er[key]["median"] * 100)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(cats, vals, color="#2c7fb8")
ax.set_ylabel("Median effective tax rate (% of market value)")
ax.set_title("The longer you own, the lower your effective tax rate",
             fontsize=13, fontweight="bold")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.02, f"{v:.2f}%", ha="center", fontsize=9)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(); fig.savefig(f"{BASE}/outputs/charts/effective_rates.png", dpi=150)
print("wrote effective_rates.png")

# ---------- 3. ZIP price change vs over-assessment gap ----------
v3 = json.load(open(f"{BASE}/outputs/cohort_gaps_v3.json"))
ziprows = [r for r in v3["by_zip_b"] if r["n23"] >= 20 and r["n2425"] >= 20]
# price change per ZIP from transfers: recompute quickly from cohort script outputs is heavy;
# use zhvi peaks instead: Jun2022 -> Dec2024 change
zhvi = json.load(open(f"{BASE}/outputs/zhvi_zip_peaks.json"))
zh = {z["zip"]: z for z in zhvi}
xs, ys, lbls = [], [], []
for r in ziprows:
    z = zh.get(r["zip"])
    if z and z["dec2024_vs_jun2022_pct"] is not None:
        xs.append(z["dec2024_vs_jun2022_pct"])
        ys.append(r["gap"] / 1000)  # $k
        lbls.append(r["zip"])
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(xs, ys, s=40, alpha=0.7)
for x0, y0, l in zip(xs, ys, lbls):
    if l in ("94705", "94609", "94610", "94611", "94539", "94555"):
        dx, dy, ha = 4, 4, "left"
        if l == "94539":
            dx, dy, ha = 4, -14, "left"
        ax.annotate(l, (x0, y0), fontsize=9, fontweight="bold",
                    xytext=(dx, dy), textcoords="offset points", ha=ha)
ax.axhline(0, color="gray", linewidth=1); ax.axvline(0, color="gray", linewidth=1)
ax.set_xlabel("ZIP home-value change, Jun 2022 → Dec 2024 (%)  [ZHVI]")
ax.set_ylabel("Over-assessment gap, 2023 buyers vs 2024–25 prices ($k)")
ax.set_title("ZIPs whose prices fell most show the largest over-assessment gaps",
             fontsize=12, fontweight="bold")
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(f"{BASE}/outputs/charts/zip_gap.png", dpi=150)
print(f"wrote zip_gap.png ({len(xs)} ZIPs)")
