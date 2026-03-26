import re
from model.model import get_embedding_local
from services.get_embeddings import get_embedding_api
from datetime import datetime
import os
import spacy

nlp = spacy.load("xx_ent_wiki_sm")

USE_API = os.getenv("USE_API", "true").lower() == "true"

def extract_location_spacy(text):
    doc = nlp(text)
    result = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    return result[0] if result else ""

def parse_time(dt_str):
    try:
        return datetime.fromisoformat(dt_str)
    except:
        return None
    
def clean_text(text):
    if not text:
        return ""

    # lowercase (optional, tergantung model)
    text = text.lower()

    # hapus HTML tag
    text = re.sub(r'<.*?>', ' ', text)

    # hapus URL
    text = re.sub(r'http\S+', ' ', text)

    # hapus karakter aneh
    text = re.sub(r'[^a-zA-Z0-9\s.,]', ' ', text)

    # hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def prepare_semanticembedding_text(item):
    text = build_semantic_text(item)
    clean = clean_text(text)
    return clean

def prepare_eventembedding_text(item):
    text = build_event_text(item)
    clean = clean_text(text)
    return clean

def build_semantic_text(item):
    return f"{item['title']}. {item.get('description', '')}"

def build_event_text(item):
    return f"{item['type']} di {item.get('location', {}).get('text')} waktu {item['datetime']}"

def prepare_summary_text(item):
    metadata = item.get("metadata", {})
    title = metadata.get("title", "")
    description = metadata.get("description", "")
    location = metadata.get("location", "")
    datetime = metadata.get("datetime", "")
    magnitude = metadata.get("magnitude", "")
    source = metadata.get("source", "")
    
    return f"{source} - {title}. {description}. Magnitudo: {magnitude}. Lokasi: {location}. Waktu: {datetime}."

def filter_results(result, location=None):
    """
    Filter ChromaDB query results by location.
    result: ChromaDB query result with 'metadatas', 'distances', 'documents'
    location: location string to filter by (optional)
    Returns: list of dicts with metadata and distance
    """
    filtered = []
    
    # ChromaDB returns nested lists, so we need to flatten them
    metadatas = result["metadatas"][0] if result["metadatas"] else []
    distances = result["distances"][0] if result["distances"] else []
    documents = result["documents"][0] if result["documents"] else []
    
    print(f"Filtering results: {len(metadatas)} metadatas, {len(distances)} distances, {len(documents)} documents")  # Debug print

    for i, metadata in enumerate(metadatas):
        # Filter by location if specified
        if location:
            # Check if location string is in the metadata location
            if location.lower() not in metadata.get("location", "").lower():
                continue
        
        # Combine metadata with distance and document
        filtered.append({
            "metadata": metadata,
            "distance": distances[i] if i < len(distances) else 0,
            "document": documents[i] if i < len(documents) else ""
        })
    
    return filtered

def get_embedding(text):
    # switchable backend
    if USE_API:
        return get_embedding_api(text)
    else:
        pass
        # return get_embedding_local(text)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance