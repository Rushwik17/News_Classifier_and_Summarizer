from huggingface_hub import InferenceClient
import hashlib
import json
import os

CACHE_PATH = "cache/summary_cache.json"
HF_MODEL_NAME = "csebuetnlp/mT5_multilingual_XLSum"

client = InferenceClient(model=HF_MODEL_NAME)

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

def get_summaries_batch(data):
    cache = load_cache()
    summaries = []

    for item in data:
        full_text = item.get("DESCRIPTION", "").strip()

        if not full_text:
            summaries.append("विवरण उपलब्ध नहीं है।")
            continue

        key = hash_text(full_text)
        if key in cache:
            summaries.append(cache[key])
            continue

        model_text = full_text[:500]
        prompt = (
            "इस समाचार का सटीक और तथ्यात्मक सारांश 4-5 वाक्यों में लिखें। "
            "केवल दी गई जानकारी का उपयोग करें और अधूरा वाक्य न छोड़ें:\n"
            + model_text
        )

        try:
            response = client.text_generation(
                prompt,
                max_new_tokens=200,
                temperature=0.3,
                do_sample=False
            )

            summary = response.strip()

            if not summary:
                summary = "सारांश उपलब्ध नहीं है।"

        except Exception as e:
            print(f"HF API error: {e}")
            summary = "सारांश प्राप्त करने में समस्या हुई।"

        cache[key] = summary
        summaries.append(summary)
    save_cache(cache)

    return summaries