import os
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai

CACHE_PATH = "cache/summary_cache.json"
MAX_WORKERS = 5
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------ UTIL ------------------

def hash_text(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def load_cache():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def generate_summary(item, cache):
    full_text = item.get("DESCRIPTION", "").strip()
    if not full_text:
        return "विवरण उपलब्ध नहीं है।"

    key = hash_text(full_text)

    if key in cache:
        return cache[key]

    prompt = f"""
    इस समाचार का 4-5 वाक्यों में सटीक और तथ्यात्मक सारांश लिखें।
    केवल दी गई जानकारी का उपयोग करें और कोई अतिरिक्त जानकारी न जोड़ें।

    समाचार:
    {full_text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        summary = response.text.strip() if response.text else ""

        if not summary:
            summary = "सारांश उपलब्ध नहीं है।"

    except Exception as e:
        print(f"Gemini API error: {e}")
        summary = "सारांश प्राप्त करने में समस्या हुई।"
    cache[key] = summary
    return summary

def get_summaries_batch(data):
    cache = load_cache()
    summaries = [None] * len(data)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_summary, item, cache): idx
            for idx, item in enumerate(data)
        }

        for future in as_completed(futures):
            idx = futures[future]
            summaries[idx] = future.result()

    save_cache(cache)
    return summaries