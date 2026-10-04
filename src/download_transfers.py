"""Download the Assessor's ownership transfer list (188k rows).

Fields: apn, doc_dt, transfer_dt, doc_prefix, doc_series,
value_from_trans_tax (sale price implied by documentary transfer tax;
blank => exempt / non-arm's-length), doc_parcel_count, use_cd, city.
Correct ArcGIS paging: advance by rows returned, stop on empty page.
"""
import json, os, time, urllib.request, urllib.parse

BASE = ("https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/"
        "Assessor_Office_Ownership_Transfer_List/FeatureServer/0/query")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "transfers.jsonl")
FIELDS = ("OBJECTID,sort_apn,apn,use_cd,use_name,street_num,pre_dir,street_name,"
          "street_suffix,post_dir,unit_num,city_name,zip_cd,doc_dt,transfer_dt,"
          "doc_prefix,doc_series,value_from_trans_tax,doc_parcel_count,name_type")
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
    with open(OUT, "w") as f:
        while True:
            for attempt in range(5):
                try:
                    d = fetch(offset); break
                except Exception as e:
                    print(f"offset {offset}: retry {attempt+1} ({e})", flush=True)
                    time.sleep(2 * (attempt + 1))
            else:
                print(f"FAILED at offset {offset}", flush=True); raise SystemExit(1)
            feats = d.get("features", [])
            if not feats:
                print(f"done: empty page at offset {offset}", flush=True); break
            for ft in feats:
                f.write(json.dumps(ft["attributes"], separators=(",", ":")) + "\n")
            n = len(feats); total += n; offset += n
            if total % 20000 == 0:
                print(f"... {total} rows", flush=True)
    print(f"COMPLETE: {total} rows -> {OUT}")

if __name__ == "__main__":
    main()
