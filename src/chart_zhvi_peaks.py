"""Chart: the 2022 price peak and ZIP divergence (ZHVI, indexed to Jan 2020 = 100)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
series = json.load(open(os.path.join(BASE, "outputs/zhvi_zip_series.json")))

# spotlight ZIPs: high-drawdown vs kept-rising + Nebo's own
PICKS = ["94705", "94609", "94610", "94611", "94539", "94555"]

fig, ax = plt.subplots(figsize=(10, 5.5))
for z in PICKS:
    s = series[z]
    ds = [datetime.strptime(d, "%Y-%m-%d") for d in s["dates"]]
    vals = s["values"]
    # index to Jan 2020
    base = next(v for d, v in zip(ds, vals) if d >= datetime(2020, 1, 31))
    idx = [v / base * 100 for v in vals]
    mask = [d >= datetime(2019, 1, 1) for d in ds]
    label = f"{z} ({s['city']})" + ("  \u2190 my ZIP" if z == "94611" else "")
    ax.plot([d for d, m in zip(ds, mask) if m],
            [v for v, m in zip(idx, mask) if m],
            label=label, linewidth=2 if z == "94611" else 1.4)

ax.axvline(datetime(2022, 5, 31), color="gray", linestyle="--", linewidth=1)
ax.text(datetime(2022, 7, 1), 86, "Spring 2022 peak", fontsize=9, color="gray")
ax.set_title("Alameda County home values peaked in spring 2022 \u2014 then diverged by ZIP",
             fontsize=13, fontweight="bold")
ax.set_ylabel("ZHVI, indexed (Jan 2020 = 100)")
ax.set_xlabel("")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(fontsize=9, loc="upper left")
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "outputs/charts/zhvi_peak_divergence.png"), dpi=150)
print("wrote outputs/charts/zhvi_peak_divergence.png")
