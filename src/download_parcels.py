"""Download all Alameda County parcels from the ArcGIS Hub FeatureService.

Pages with resultOffset (advancing by rows RETURNED, stopping only on an empty
page — servers clamp page sizes). Resumes from checkpoint. Writes JSONL.
"""
import json, os, sys, time, urllib.request, urllib.parse

BASE = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/Parcels/FeatureServer/0/query"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "parcels.jsonl")
CKPT = os.path.join(os.path.dirname(__file__), "..", "data", "parcels.ckpt")
FIELDS = ("OBJECTID,APN,APN_SORT,SitusAddress,SitusCity,SitusZip,Land,Imps,CLCALand,"
          "CLCAImps,HOEX,OTEX,TotalNetValue,LatestDocumentDate,UseCode,TRAPrimary,"
          "TRASecondary,CENTROID_X,CENTROID_Y,Shape__Area")
PAGE = 2000

def fetch(offset):
    q = urllib.parse.urlencode({
        "where": "1=1", "outFields": FIELDS, "orderByFields": "OBJECTID",
        "resultOffset": offset, "resultRecordCount": PAGE,
        "returnGeometry": "false", "f": "json",
    })
    req = urllib.request.Request(BASE + "?" + q, headers={"User-Agent": "alameda-assessment/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    offset = int(open(CKPT).read()) if os.path.exists(CKPT) else 0
    mode = "a" if offset else "w"
    total = 0
    with open(OUT, mode) as f:
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
                print(f"done: empty page at offset {offset}, total rows ~{total}", flush=True)
                break
            for ft in feats:
                f.write(json.dumps(ft["attributes"], separators=(",", ":")) + "\n")
            n = len(feats); total += n; offset += n
            open(CKPT, "w").write(str(offset))
            if total % 20000 == 0:
                print(f"... {total} rows (offset {offset})", flush=True)
    print(f"COMPLETE: {total} rows -> {OUT}", flush=True)

if __name__ == "__main__":
    main()
