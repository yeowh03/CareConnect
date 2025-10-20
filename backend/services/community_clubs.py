import requests
import os, html, re, time, uuid

# ---------- CC dataset helpers ----------
def parse_desc_table(desc_html: str) -> dict:
    if not desc_html: return {}
    text = html.unescape(desc_html)
    pairs = re.findall(r"<th>(.*?)</th>\s*<td>(.*?)</td>", text, flags=re.I | re.S)
    data = {}
    tag_re = re.compile(r"<[^>]+>")
    for k, v in pairs:
        key = str(k).strip().upper()
        val = tag_re.sub("", v).strip()
        data[key] = val
    return data

def feat_to_marker(feat):
    geom = (feat or {}).get("geometry") or {}
    props = (feat or {}).get("properties") or {}
    if geom.get("type") != "Point": return None
    coords = geom.get("coordinates") or []
    if len(coords) < 2: return None
    lng, lat = float(coords[0]), float(coords[1])
    table = parse_desc_table(props.get("Description") or props.get("description") or "")
    name = table.get("NAME") or props.get("Name") or props.get("name") or "Community Club"
    address = " ".join([t for t in [
        table.get("ADDRESSBLOCKHOUSENUMBER") or "",
        table.get("ADDRESSSTREETNAME") or "",
        table.get("ADDRESSPOSTALCODE") or "",
    ] if t]).strip() or None
    link = table.get("HYPERLINK") or None
    return {"name": name, "lat": lat, "lng": lng, "address": address, "link": link}

def fetch_cc_markers_from_api(DATASET_ID: str):
    POLL_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/poll-download"
    j = requests.get(POLL_URL, timeout=20).json()
    if j.get("code") != 0 or "data" not in j or "url" not in j["data"]:
        raise RuntimeError(f"Poll Download failed: {j}")
    gj = requests.get(j["data"]["url"], timeout=60).json()
    features = (gj or {}).get("features") or []
    markers = []
    for f in features:
        m = feat_to_marker(f)
        if m: markers.append(m)
    return markers