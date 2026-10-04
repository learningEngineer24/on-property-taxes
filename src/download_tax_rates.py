"""Download the Alameda County 2025 property-tax-rate-by-TRA layer.

Pages with resultOffset (advancing by rows RETURNED, stopping only on an empty
page). Tracks exceededTransferLimit as a sanity signal. Writes JSONL.
"""
import json, os, sys, time, urllib.request, urllib.parse

BASE = ("https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/"
        "Property_Tax_Rates_2025/FeatureServer/0/query")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "tax_rates_2025.jsonl")
FIELDS = ("OBJECTID,TAX_RATE_YEAR,TRA_PRIM,TRA_SEC,TAX_RATE,"
          "LEGACY_FUND_NO,LEGACY_FUND_NAME,TRA_LONG_DESC")
PAGE = 2000

def fetch(offset):
    q = urllib.parse.urlencode({
        "where": "1=1", "outFields": FIELDS, "orderByFields": "OBJECTID",
        "resultOffset": offset, "resultRecordCount": PAGE,
        "returnGeometry": "false", "f": "json",
    })
    req = urllib.request.Request(BASE + "?" + q,
                                 headers={"User-Agent": "alameda-assessment/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    offset, total = 0, 0
    saw_limit = False
    with open(OUT, "w") as f:
        while True:
            for attempt in range(5):
                try:
                    d = fetch(offset); break
                except Exception as e:
                    print(f"offset {offset}: retry {attempt+1} ({e})", flush=True)
                    time.sleep(2 * (attempt + 1))
            else:
                print(f"FAILED at offset {offset}", flush=True); sys.exit(1)
            feats = d.get("features", [])
            if not feats:
                print(f"done: empty page at offset {offset}", flush=True); break
            if d.get("exceededTransferLimit"):
                saw_limit = True
            for ft in feats:
                f.write(json.dumps(ft["attributes"], separators=(",", ":")) + "\n")
            n = len(feats); total += n; offset += n
            print(f"... {total} rows (offset {offset})", flush=True)
    print(f"COMPLETE: {total} rows -> {OUT}; exceededTransferLimit seen: {saw_limit}")

if __name__ == "__main__":
    main()
