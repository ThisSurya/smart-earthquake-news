import chromadb
from rapidfuzz import fuzz

from .helper import parse_time, prepare_eventembedding_text, prepare_semanticembedding_text, get_embedding, calculate_distance
client = chromadb.Client()
collection_events = client.create_collection("events")
collection_semantic = client.create_collection("semantic")


def storeEvent(item):
    text = prepare_eventembedding_text(item)
    embedding = get_embedding(text)
    # DEDUP CHECK
    if is_duplicate_event(item, embedding):
        return

    collection_events.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "id": item["id"],
            "source": item["source"],
            "title": item["title"],
            "description": item.get("description", ""),
            "datetime": item["datetime"],
            "location": item["location"]["text"],
            "latitude": str(item["location"].get("lat")) if item["location"].get("lat") is not None else "none",
            "longitude": str(item["location"].get("lon")) if item["location"].get("lon") is not None else "none",
            "isOfficial": item["isOfficial"],
            "type": item["type"],
            "magnitude": item.get("severity"),
            "source": item["source"]
        }],
        ids=[f"{item['source']}-{item['id']}"]
    )

def storeSemantic(item):
    text = prepare_semanticembedding_text(item)
    embedding = get_embedding(text)
    # DEDUP CHECK
    if is_duplicate_semantic(item, embedding):
        return
    collection_semantic.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "id": item["id"],
            "source": item["source"],
            "datetime": item["datetime"],
            "location": item["location"]["text"],
            "latitude": str(item["location"].get("lat")) if item["location"].get("lat") is not None else "none",
            "longitude": str(item["location"].get("lon")) if item["location"].get("lon") is not None else "none"
        }],
        ids=[f"{item['source']}-{item['id']}"]
    )

def is_duplicate_event(item, embedding):
    results = collection_events.query(
        query_embeddings=[embedding],
        n_results=5
    )

    if not results["ids"]:
        return False

    for i, distance in enumerate(results["distances"][0]):
        metadata = results["metadatas"][0][i]

        # threshold similarity
        if distance < 0.15:
            # cek lokasi
            if metadata["location"] == item["location"]["text"]:
                
                # cek waktu (toleransi 1 jam)
                t1 = parse_time(metadata["datetime"])
                t2 = parse_time(item["datetime"])

                if t1 and t2:
                    if abs((t1 - t2).total_seconds()) < 3600:
                        return True

    return False

def is_duplicate_semantic(item, embedding):
    results = collection_semantic.query(
        query_embeddings=[embedding],
        n_results=3
    )

    for distance in results["distances"][0]:
        if distance < 0.05:
            return True

    return False

def search_events(query, n_results=20):
    embedding = get_embedding(query)

    results = collection_events.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results

def cluster(results, geo_radius_km=100, fuzzy_threshold=40):
    """
    Cluster items by geographic location.
    - BMKG items (with lat/lon) form geographic cluster anchors.
    - CNN/Kumparan items are matched to clusters via fuzzy location text matching.
    - Unmatched news items are grouped into text-only clusters.

    Returns a list of clusters, where each cluster is a list of items
    belonging to the same earthquake event/location.
    """
    # Transform ChromaDB results into list of items
    items = []
    if results["ids"] and len(results["ids"]) > 0:
        for i in range(len(results["ids"][0])):
            items.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

    # Separate BMKG items (have real coordinates) from news items
    bmkg_items = [
        item for item in items
        if item["metadata"].get("source") == "bmkg"
        and item["metadata"].get("latitude", "none") not in ("none", None, "")
        and item["metadata"].get("longitude", "none") not in ("none", None, "")
    ]
    news_items = [item for item in items if item not in bmkg_items]

    # Build geo-clusters anchored on BMKG events (group by proximity)
    # Each entry: {"lat": float, "lon": float, "location": str, "items": [...]}
    geo_clusters = []

    for item in bmkg_items:
        lat = float(item["metadata"]["latitude"])
        lon = float(item["metadata"]["longitude"])
        placed = False

        for gc in geo_clusters:
            dist = calculate_distance(lat, lon, gc["lat"], gc["lon"])
            if dist <= geo_radius_km:
                gc["items"].append(item)
                placed = True
                break

        if not placed:
            geo_clusters.append({
                "lat": lat,
                "lon": lon,
                "location": item["metadata"].get("location", ""),
                "items": [item]
            })

    # Match news items (CNN/Kumparan) to geo-clusters via fuzzy location text
    unmatched_news = []
    for news in news_items:
        news_loc = news["metadata"].get("location", "").lower()
        best_score = 0
        best_gc = None

        for gc in geo_clusters:
            score = fuzz.partial_ratio(news_loc, gc["location"].lower())
            if score > best_score:
                best_score = score
                best_gc = gc

        if best_gc and best_score >= fuzzy_threshold:
            best_gc["items"].append(news)
            print(f"Matched news '{news_loc}' to cluster '{best_gc['location']}' (score: {best_score})")  # Debug
        else:
            unmatched_news.append(news)
            print(f"No match for news '{news_loc}' (best score: {best_score})")  # Debug

    # Group remaining unmatched news by location text similarity to each other
    for news in unmatched_news:
        news_loc = news["metadata"].get("location", "").lower()
        placed = False

        for gc in geo_clusters:
            if gc["lat"] is None:  # text-only cluster
                score = fuzz.partial_ratio(news_loc, gc["location"].lower())
                if score >= 60:
                    gc["items"].append(news)
                    placed = True
                    break

        if not placed:
            geo_clusters.append({
                "lat": None,
                "lon": None,
                "location": news["metadata"].get("location", ""),
                "items": [news]
            })

    return [gc["items"] for gc in geo_clusters if gc["items"]]