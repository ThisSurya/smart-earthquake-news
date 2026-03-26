import feedparser
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from rapidfuzz import fuzz
import requests
import xmltodict
from util.helper import extract_location_spacy as extract_location
from util.mapping import normalize_cnn, normalize_kumparan, normalize_bmkg

CNN_NEWS_RSS = "https://www.cnnindonesia.com/rss"
KUMPARAN_NEWS_RSS = "https://lapi.kumparan.com/v2.0/rss/"

BMKG_ENDPOINT = {
    "autogempa": "autogempa",
    "gempaterkini": "gempaterkini",
    "gempadirasakan": "gempadirasakan"
}

# =============================
# Utility
# =============================

def replace_query_params(url: str, key: str, value: str):
    if not url:
        return None

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query[key] = value
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


# =============================
# CNN SOURCE
# =============================

def fetch_cnn():
    feed = feedparser.parse(CNN_NEWS_RSS)
    results = []

    for entry in feed.entries:
        enclosure_url = None

        if "links" in entry:
            for link in entry.links:
                if link.get("rel") == "enclosure":
                    enclosure_url = link.get("href")

        image_large = replace_query_params(enclosure_url, "q", "100") if enclosure_url else None

        results.append({
            "id": entry.get("link"),
            "title": entry.get("title"),
            "description": entry.get("summary"),
            "source": "cnn",
            "type": "news",
            "datetime": entry.get("published"),
            "location": {
                "lat": None,
                "lon": None,
                "text": extract_location(entry.get("title", ""))
            },
            "severity": None,
            "confidence": "medium",
            "isOfficial": False,
            "image": {
                "small": enclosure_url,
                "large": image_large
            },
        })

    return results

# =============================
# KUMPARAN SOURCE
# =============================

def fetch_kumparan():
    feed = feedparser.parse(KUMPARAN_NEWS_RSS)
    results = []

    for entry in feed.entries:
        enclosure_url = None

        if "links" in entry:
            for link in entry.links:
                if link.get("rel") == "enclosure":
                    enclosure_url = link.get("href")

        def resize(url, old, new):
            return url.replace(old, new) if url else None

        results.append({
            "id": entry.get("link"),
            "title": entry.get("title"),
            "description": entry.get("summary"),
            "source": "kumparan",
            "type": "news",
            "datetime": entry.get("published"),
            "location": {
                "lat": None,
                "lon": None,
                "text": extract_location(entry.get("title", ""))
            },
            "severity": None,
            "confidence": "medium",
            "isOfficial": False,
            "image": {
                "small": resize(enclosure_url, "w_480", "w_240"),
                "medium": enclosure_url,
                "large": resize(enclosure_url, "w_480", "w_720"),
                "extraLarge": resize(enclosure_url, "w_480", "w_1080"),
            },
        })

    return results

# =============================
# BMKG SOURCE
# =============================
def fetch_bmkg(status="dirasakan"):
    url = f"https://data.bmkg.go.id/DataMKG/TEWS/{BMKG_ENDPOINT[status]}.xml"

    response = requests.get(url)
    data = xmltodict.parse(response.content)

    gempa_data = data.get("Infogempa", {}).get("gempa")

    if not gempa_data:
        return []

    if not isinstance(gempa_data, list):
        gempa_data = [gempa_data]

    results = []

    for item in gempa_data:
        lat, lon = item["point"]["coordinates"].split(",")

        results.append({
            "id": f"bmkg-{item['DateTime']}",
            "title": f"Gempa M{item['Magnitude']} - {item['Wilayah']}",
            "description": f"Kedalaman {item['Kedalaman']}, dirasakan {item.get('Dirasakan')}",
            "source": "bmkg",
            "type": "earthquake",
            "datetime": item["DateTime"],
            "location": {
                "lat": float(lat),
                "lon": float(lon),
                "text": extract_location(item["Wilayah"])
            },
            "severity": float(item["Magnitude"]),
            "confidence": "high",
            "isOfficial": True,
            "image": None,
        })

    return results

# =============================
# SEARCH
# =============================

def search_items(data, query):
    results = []

    for item in data:
        title_score = fuzz.partial_ratio(query, item["title"] or "")
        desc_score = fuzz.partial_ratio(query, item["description"] or "")

        score = max(title_score, desc_score)

        if score > 90:  # threshold
            results.append({
                "item": item,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    news = [r["item"] for r in results]
    return news

