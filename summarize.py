from transformers import pipeline
import torch
import hashlib
import json
import os

DEVICE = 0 if torch.cuda.is_available() else -1
CACHE_PATH = "cache/summary_cache.json"
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="csebuetnlp/mT5_multilingual_XLSum",
            device=DEVICE
        )
    return summarizer

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
    summarizer = get_summarizer()
    cache = load_cache()
    keys = []
    uncached_inputs = []
    uncached_indices = []

    for i, item in enumerate(data):
        full_text = item.get("DESCRIPTION", "").strip()

        if not full_text:
            keys.append(None)
            continue

        key = hash_text(full_text)
        keys.append(key)

        if key not in cache:
            model_text = full_text[:500]

            prompt = (
                "इस समाचार का सटीक और तथ्यात्मक सारांश 4-5 वाक्यों में लिखें। "
                "केवल दी गई जानकारी का उपयोग करें और अधूरा वाक्य न छोड़ें:\n"
                + model_text
            )

            uncached_inputs.append(prompt)
            uncached_indices.append(i)

    if uncached_inputs:
        outputs = summarizer(
            uncached_inputs,
            max_length=240,
            min_length=80,
            num_beams=4,
            do_sample=False,
            repetition_penalty=1.2,
            length_penalty=1.2,
            early_stopping=True,
            batch_size=8
        )

        for idx, output in zip(uncached_indices, outputs):
            summary = output["summary_text"]
            cache[keys[idx]] = summary

        save_cache(cache)

    summaries = []
    for key in keys:
        if key is None:
            summaries.append("विवरण उपलब्ध नहीं है।")
        else:
            summaries.append(cache.get(key, "Error"))

    return summaries