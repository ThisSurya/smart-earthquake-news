import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Ensure .env is loaded even when this module is imported before other modules.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _get_client() -> genai.Client:
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set. Configure it in environment or fastAPI/.env")
  return genai.Client(api_key=api_key)


def get_summary_api(text):
  client = _get_client()
  print("start recommendation.....")
  response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=f"""
        Berikut adalah berita terkini seputar gempa bumi di lokasi tertentu:
        {text}
        Tolong berikan apa yang harus lakukan jika terjadi gempa bumi di lokasi tersebut, dengan langkah-langkah yang jelas dan mudah dipahami. Sertakan juga informasi penting lainnya yang relevan dengan situasi gempa bumi di lokasi tersebut. pada data 'dirasakan' semakin tinggi angka nya maka akan semakin berdampak pada daerah tersebut.
      """,
    
  )
  return response.text

  # return "yatta!"