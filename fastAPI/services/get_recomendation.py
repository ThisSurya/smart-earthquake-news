import requests
from google import genai
from google.genai import types
client = genai.Client(api_key='AIzaSyB5SMheeL8_hJMRVInKNsNJzKX5JOSOw2E')

def get_summary_api(text):
    response = client.models.generate_content(
      model="gemini-3-flash-preview",
      contents=f"""
        Berikut adalah berita terkini seputar gempa bumi di lokasi tertentu:
        {text}
        Tolong berikan apa yang harus lakukan jika terjadi gempa bumi di lokasi tersebut, dengan langkah-langkah yang jelas dan mudah dipahami. Sertakan juga informasi penting lainnya yang relevan dengan situasi gempa bumi di lokasi tersebut. pada data 'dirasakan' semakin tinggi angka nya maka akan semakin berdampak pada daerah tersebut.
      """,
        config=types.GenerateContentConfig(
          http_options=types.HttpOptions(timeout=10_000) # 5 menit
      )
    )
    return response.text

    # return "yatta!"