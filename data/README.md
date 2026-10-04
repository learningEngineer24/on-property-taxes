# Data

Bulk data files are intentionally **not** in this repo (hundreds of MB).
Everything is reproducible from public sources with the scripts in `../src/`:

```bash
python3 ../src/download_parcels.py        # parcels.jsonl — 489,628 parcels
python3 ../src/download_transfers.py      # transfers.jsonl — 187,908 transfer rows
python3 ../src/download_tax_rates.py      # tax_rates_2025.jsonl
python3 ../src/download_tax_rates_2024.py # tax_rates_2024.jsonl
python3 ../src/download_taxrolls.py       # taxroll_YYYY_to_YYYY.jsonl (7 annual rolls)
```

All downloads use correct ArcGIS REST paging (offset advanced by rows
returned, stop on empty page) with per-dataset checkpoints — safe to resume.

Small reference files that *are* committed here:

- `usecode_lookup.md` — Assessor's official UseCode table (from
  propinfo.acgov.org), validated against observed codes.
- `tra_rates_combined.json` — per-TRA ad-valorem rates, preferring 2025 rows
  and filling 74 missing TRAs from 2024. Key format `"TRA_PRIM:TRA_SEC"`
  with integer normalization (parcel secondaries are zero-padded).
- `fred_mortgage30us.csv` — FRED 30-year fixed mortgage rates, weekly
  1971–present (no API key needed via fredgraph.csv).
