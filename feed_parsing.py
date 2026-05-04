import requests
import feedparser
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

OUTPUT_PATH = "data/input.json"

def fetch_data():
    rss_urls = {
        "Opinion": "https://www.bhaskar.com/rss-v1--category-1944.xml",
        "Bollywood": "https://www.bhaskar.com/rss-v1--category-11215.xml",
        "Auto": "https://www.bhaskar.com/rss-v1--category-10711.xml",
        "Jobs": "https://www.bhaskar.com/rss-v1--category-11945.xml",
        "Women": "https://www.bhaskar.com/rss-v1--category-1532.xml",
        "Tech": "https://www.bhaskar.com/rss-v1--category-5707.xml",
        "Lifestyle": "https://www.bhaskar.com/rss-v1--category-7911.xml",
        "Utility": "https://www.bhaskar.com/rss-v1--category-11616.xml",
        "International": "https://www.bhaskar.com/rss-v1--category-1125.xml",
        "Politics": "https://www.bhaskar.com/rss-v1--category-1061.xml",
        "Business": "https://www.bhaskar.com/rss-v1--category-1051.xml",
        "Sports": "https://www.bhaskar.com/rss-v1--category-1053.xml",
        "Magazine": "https://www.bhaskar.com/rss-v1--category-1057.xml",
        "Spiritual": "https://www.bhaskar.com/rss-v1--category-3379.xml",
        "Entertainment": "https://www.bhaskar.com/rss-v1--category-3998.xml",
        "Original": "https://www.bhaskar.com/rss-v1--category-4587.xml"
    }

    news_data = []

    for category, url in rss_urls.items():
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            feed = feedparser.parse(response.content)

            for entry in feed.entries:
                description = BeautifulSoup(entry.summary, "html.parser").text

                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    dt = datetime(*entry.published_parsed[:6])
                    iso_time = dt.isoformat()
                else:
                    continue

                news_data.append({
                    "TITLE": entry.title,
                    "DESCRIPTION": description,
                    "TIME": iso_time
                })

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    seen_titles = set()
    unique_news = []

    for item in news_data:
        if item["TITLE"] not in seen_titles:
            unique_news.append(item)
            seen_titles.add(item["TITLE"])

    unique_news.sort(key=lambda x: x["TIME"], reverse=True)
    final_news = unique_news[:30]

    for item in final_news:
        item.pop("TIME", None)
        
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_news, f, ensure_ascii=False, indent=2)

    return OUTPUT_PATH