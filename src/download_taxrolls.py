"""Download all 7 annual secured tax rolls (2019-2020 .. 2025-2026).

Each roll is a full county snapshot (~490k rows). Per-roll checkpoints so a
restart resumes the current roll. Correct ArcGIS paging throughout.
"""
import json, os, time, urllib.request, urllib.parse

BASE = ("https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/"
        "Assessor_Office_Secured_Tax_Roll_{y}/FeatureServer/0/query")
YEARS = ["2019_to_2020", "2020_to_2021", "2021_to_2022", "2022_to_2023",
         "2023_to_2024", "2024_to_2025", "2025_to_2026"]
FIELDS = ("OBJECTID,Sort_Parcel,Print_Parcel,TRA_Primary,TRA_Secondary,"
          "Situs_Zip,Land,Imps,Total_Net_Value,HOEX,OTEX,Use_Code")
PAGE = 2000
DATADIR = os.path.join(os.path.dirname(__file__), "..", "data")

def fetch(year, offset):
    q = urllib.parse.urlencode({
        "where": "1=1", "outFields": FIELDS, "orderByFields": "OBJECTID",
        "resultOffset": offset, "resultRecordCount": PAGE,
        "returnGeometry": "false", "f": "json",
    })
    req = urllib.request.Request(BASE.format(y=year) + "?" + q,
                                 headers={"User-Agent": "alameda-assessment/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    for year in YEARS:
        out = os.path.join(DATADIR, f"taxroll_{year}.jsonl")
        ckpt = os.path.join(DATADIR, f"taxroll_{year}.ckpt")
        offset = int(open(ckpt).read()) if os.path.exists(ckpt) else 0
        mode = "a" if offset else "w"
        total = 0
        with open(out, mode) as f:
            while True:
                for attempt in range(5):
                    try:
                        d = fetch(year, offset); break
                    except Exception as e:
                        print(f"{year} offset {offset}: retry {attempt+1} ({e})", flush=True)
                        time.sleep(2 * (attempt + 1))
                else:
                    print(f"FAILED {year} at offset {offset}", flush=True); raise SystemExit(1)
                feats = d.get("features", [])
                if not feats:
                    print(f"{year}: done at offset {offset}, +{total} rows", flush=True); break
                for ft in feats:
                    f.write(json.dumps(ft["attributes"], separators=(",", ":")) + "\n")
                n = len(feats); total += n; offset += n
                open(ckpt, "w").write(str(offset))
                if total % 100000 == 0:
                    print(f"{year}: ... {total} rows", flush=True)
        print(f"COMPLETE {year}: {total} rows", flush=True)

if __name__ == "__main__":
    main()
