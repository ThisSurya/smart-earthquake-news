import requests
from google import genai
client = genai.Client(api_key='AIzaSyB5SMheeL8_hJMRVInKNsNJzKX5JOSOw2E')

def get_embedding_api(text):
    result = client.models.embed_content(
        model='gemini-embedding-001',
        contents=text
    ).embeddings
    # Extract the values from ContentEmbedding object for ChromaDB
    return result[0].values