"""Effective-rate sensitivity to within-ZIP market-value differences (committed Oct 2026).

The effective-rate analysis proxies each parcel's market value with its ZIP's
median 2024-25 sale price. But longtime owners may own systematically smaller/
older homes worth less than the ZIP median, and recent buyers larger ones worth
more -- which would compress the measured gradient.

This script perturbs the market-value proxy by +/-20% and recomputes the
gradient between the oldest (pre-1990) and newest (2024) cohorts:
  - base:      as published (ZIP-median proxy for everyone)
  - compress:  old homes worth 20% LESS  (rate / 0.8), new homes 20% MORE (rate / 1.2)
  - widen:     old homes worth 20% MORE  (rate / 1.2), new homes 20% LESS (rate / 0.8)

Writes outputs/effective_rate_sensitivity.json.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root

er = json.load(open(os.path.join(BASE, "outputs/effective_rates.json")))["by_cohort"]
old = er["pre1990"]["median"]
new = er["2024"]["median"]

out = {
    "base": {"old_rate": old, "new_rate": new, "gradient": new / old},
    "compress_old_low_new_high": {
        "old_rate": old / 0.8, "new_rate": new / 1.2,
        "gradient": (new / 1.2) / (old / 0.8),
        "note": "longtime owners' homes worth 20% less than ZIP median; "
                "recent buyers' worth 20% more -- the plausible direction",
    },
    "widen_old_high_new_low": {
        "old_rate": old / 1.2, "new_rate": new / 0.8,
        "gradient": (new / 0.8) / (old / 1.2),
        "note": "opposite perturbation; implausible direction, bounds the range",
    },
}
for k, v in out.items():
    print(f"{k}: old {100*v['old_rate']:.3f}%  new {100*v['new_rate']:.3f}%  "
          f"gradient {v['gradient']:.1f}x")

json.dump(out, open(os.path.join(BASE, "outputs/effective_rate_sensitivity.json"), "w"), indent=1)
print("wrote outputs/effective_rate_sensitivity.json")
