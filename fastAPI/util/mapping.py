from datetime import datetime


def normalize_bmkg(item):
    lat, lon = item["point"]["coordinates"].split(",")

    return {
        "id": f"bmkg-{item['DateTime']}",
        "title": f"Gempa M{item['Magnitude']} - {item['Wilayah']}",
        "description": f"Kedalaman {item['Kedalaman']}, dirasakan {item.get('Dirasakan')}",
        "source": "bmkg",
        "type": "earthquake",
        "datetime": item["DateTime"],
        "location": {
            "lat": float(lat),
            "lon": float(lon),
            "text": item["Wilayah"]
        },
        "severity": float(item["Magnitude"]),
        "confidence": "high",
        "isOfficial": True,
        "raw": item
    }

def normalize_cnn(item):
    return {
        "id": item["link"],
        "title": item["title"],
        "description": item.get("contentSnippet"),
        "source": "cnn",
        "type": "news",
        "datetime": item["isoDate"],
        "location": {
            "lat": None,
            "lon": None,
            "text": None
        },
        "severity": None,
        "confidence": "medium",
        "isOfficial": False,
        "raw": item
    }

def normalize_kumparan(item):
    return {
        "id": item["link"],
        "title": item["title"],
        "description": item["description"],
        "source": "kumparan",
        "type": "news",
        "datetime": item["isoDate"],
        "location": {
            "lat": None,
            "lon": None,
            "text": None
        },
        "severity": None,
        "confidence": "medium",
        "isOfficial": False,
        "raw": item
    }
