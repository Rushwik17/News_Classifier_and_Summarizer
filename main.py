import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from summarize import get_summaries_batch
from huggingface_hub import hf_hub_download
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "saved_models/l3cube_news"
SUMMARY_PATH = "summaries/summaries.txt"
LABEL_MAP = {
    "automobile": "Automobile",
    "business": "Business",
    "crime-news-hindi": "Crime",
    "education": "Education",
    "entertainment": "Entertainment",
    "health-news-hindi": "Health",
    "international": "International",
    "khel": "Sports",
    "national": "National",
    "politics": "Politics",
    "technology-news": "Technology"
}
All = []
Classified = {}
HF_MODEL_NAME = "Rushwik/l3cube_news"

def load_model():
    os.makedirs(MODEL_PATH, exist_ok=True)

    config_exists = os.path.exists(os.path.join(MODEL_PATH, "config.json"))
    label_map_exists = os.path.exists(os.path.join(MODEL_PATH, "label_map.json"))

    if config_exists and label_map_exists:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    else:
        print("Downloading model from Hugging Face...")

        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL_NAME)

        tokenizer.save_pretrained(MODEL_PATH)
        model.save_pretrained(MODEL_PATH)

        label_map_path = hf_hub_download(
            repo_id=HF_MODEL_NAME,
            filename="label_map.json"
        )

        with open(label_map_path, "r") as src:
            label_map_data = json.load(src)

        with open(os.path.join(MODEL_PATH, "label_map.json"), "w") as dst:
            json.dump(label_map_data, dst, ensure_ascii=False, indent=2)

    model = model.to(DEVICE)
    model.eval()
    with open(f"{MODEL_PATH}/label_map.json", "r") as f:
        label2id = json.load(f)
    id2label = {int(v): k for k, v in label2id.items()}
    return tokenizer, model, id2label

tokenizer, model, id2label = load_model()

def classify_batch(data):
    texts = [item.get("DESCRIPTION", "") for item in data]

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True
    )

    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()

    labels = []
    for p in preds:
        label = id2label[int(p)]
        label = LABEL_MAP.get(label, label)
        labels.append(label)

    return labels

def classify_and_summarize(data_path):
    global All, Classified

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    labels = classify_batch(data)
    summaries = get_summaries_batch(data)

    All = []
    Classified = {}
    
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        for idx in range(len(data)):
            label = labels[idx]
            summary = summaries[idx]
            All.append((label, summary))

            if label not in Classified:
                Classified[label] = []
            Classified[label].append(summary)

            f.write(f"{idx+1} : {label}\n")
            f.write(f"Summary : {summary}\n\n")

    return All, Classified