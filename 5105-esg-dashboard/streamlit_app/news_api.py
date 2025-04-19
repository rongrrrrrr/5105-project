# apis/news_api.py
# ✅ 实时 ESG 新闻拉取模块（GNews API）

import requests

GNEWS_API_KEY = "cdc38426e16a367f3035ce4998d977ed"  # 请替换为你自己的 API key
BASE_URL = "https://gnews.io/api/v4/search"

def fetch_company_esg_news(company, query="ESG OR emission OR diversity", lang="en", max_results=10):
    """
    拉取指定公司相关的 ESG 新闻（默认关键词：emission、diversity、ESG）
    """
    q = f"{company} {query}"
    params = {
        "q": q,
        "lang": lang,
        "max": max_results,
        "token": GNEWS_API_KEY
    }
    try:
        res = requests.get(BASE_URL, params=params)
        res.raise_for_status()
        data = res.json()
        articles = data.get("articles", [])
        simplified = [
            {
                "title": a["title"],
                "published": a["publishedAt"],
                "source": a["source"]["name"],
                "url": a["url"],
                "content": a.get("content", "")
            }
            for a in articles
        ]
        return simplified
    except Exception as e:
        print("❌ Error fetching news:", e)
        return []
