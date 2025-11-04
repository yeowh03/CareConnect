"""Community Clubs Service for CareConnect Backend.

This module handles fetching and parsing community club data
from Singapore's open data API.
"""

import requests
import os, html, re, time, uuid

def parse_desc_table(desc_html: str) -> dict:
    """Parse HTML description table from API data.
    
    Args:
        desc_html (str): HTML description from API.
        
    Returns:
        dict: Parsed key-value pairs from the table.
    """
    if not desc_html: return {}
    
    # Decode HTML entities
    text = html.unescape(desc_html)
    
    # Extract table rows with th/td pairs
    pairs = re.findall(r"<th>(.*?)</th>\s*<td>(.*?)</td>", text, flags=re.I | re.S)
    data = {}
    tag_re = re.compile(r"<[^>]+>")  # Regex to remove HTML tags
    
    # Process each key-value pair
    for k, v in pairs:
        key = str(k).strip().upper()  # Normalize key to uppercase
        val = tag_re.sub("", v).strip()  # Remove HTML tags from value
        data[key] = val
    return data

def feat_to_marker(feat):
    """Convert GeoJSON feature to marker data.
    
    Args:
        feat (dict): GeoJSON feature object.
        
    Returns:
        dict: Marker data with name, coordinates, address, and link.
    """
    geom = (feat or {}).get("geometry") or {}
    props = (feat or {}).get("properties") or {}
    
    # Only process Point geometries
    if geom.get("type") != "Point": return None
    
    # Extract coordinates (longitude, latitude)
    coords = geom.get("coordinates") or []
    if len(coords) < 2: return None
    lng, lat = float(coords[0]), float(coords[1])
    
    # Parse description table for detailed information
    table = parse_desc_table(props.get("Description") or props.get("description") or "")
    
    # Extract name with fallbacks
    name = table.get("NAME") or props.get("Name") or props.get("name") or "Community Club"
    
    # Construct address from components
    address = " ".join([t for t in [
        table.get("ADDRESSBLOCKHOUSENUMBER") or "",
        table.get("ADDRESSSTREETNAME") or "",
        table.get("ADDRESSPOSTALCODE") or "",
    ] if t]).strip() or None
    
    # Extract website link if available
    link = table.get("HYPERLINK") or None
    
    return {"name": name, "lat": lat, "lng": lng, "address": address, "link": link}

def fetch_cc_markers_from_api(DATASET_ID: str):
    """Fetch community club markers from Singapore open data API.
    
    Args:
        DATASET_ID (str): Dataset ID for the API request.
        
    Returns:
        list: List of community club marker objects.
        
    Raises:
        RuntimeError: If API request fails.
    """
    # Step 1: Poll the API to get download URL
    POLL_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/poll-download"
    j = requests.get(POLL_URL, timeout=20).json()
    
    # Check if poll request was successful
    if j.get("code") != 0 or "data" not in j or "url" not in j["data"]:
        raise RuntimeError(f"Poll Download failed: {j}")
    
    # Step 2: Download the actual GeoJSON data
    gj = requests.get(j["data"]["url"], timeout=60).json()
    features = (gj or {}).get("features") or []
    
    # Step 3: Convert GeoJSON features to marker objects
    markers = []
    for f in features:
        m = feat_to_marker(f)
        if m: markers.append(m)  # Only add valid markers
    
    return markers