import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Configure it in environment or fastAPI/.env")
    return genai.Client(api_key=api_key)

def get_embedding_api(text):
    client = _get_client()
    result = client.models.embed_content(
        model='gemini-embedding-001',
        contents=text
    ).embeddings
    # Extract the values from ContentEmbedding object for ChromaDB
    return result[0].values