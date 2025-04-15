import feedparser
import requests
from secret_manager import get_cryptopanic_key
from newspaper import Article
from redis_cache import redis_cache

# RSS feed URLs
RSS_FEEDS = {
    "Decrypt": "https://decrypt.co/feed",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",    
    "CryptoSlate": "https://cryptoslate.com/feed/",    
    "NewsBTC": "https://www.newsbtc.com/feed/",    
    "CryptoPotato": "https://cryptopotato.com/feed/",    
    "AMBCrypto": "https://ambcrypto.com/feed/",
}


CRYPTOPANIC_API_KEY = get_cryptopanic_key().strip()
CRYPTOPANIC_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&filter=hot"


def extract_article_text(url):
    try:
        article = Article(url)
        article.download(input_html=requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
        ).text)
        article.parse()
        return article.title, article.text
    except Exception as e:
        print(f"Failed to extract article: {e}")
        return None, None

@redis_cache(ttl=3600 * 4)  
def fetch_rss(feed_url, source_name):
    response = requests.get(feed_url, allow_redirects=True)
    if response.status_code != 200:
        print(f"Failed to fetch RSS from {source_name} - Status {response.status_code}")
        return []
    feed = feedparser.parse(response.content)
    articles = []
    for entry in feed.entries[:5]: 
        articles.append({
            "source": source_name,
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "content": extract_article_text(entry.link)[1] if entry.link else None,
        })
    return articles

@redis_cache(ttl=3600 * 4)
def fetch_cryptopanic():
    response = requests.get(CRYPTOPANIC_URL)
    data = response.json()
    articles = []
    for item in data.get("results", [])[:5]:
        articles.append({
            "source": "CryptoPanic",
            "title": item.get("title"),
            "link": item.get("url"),
            "published": item.get("published_at"),            
        })
    return articles

def get_all_news():
    all_news = []

    for name, url in RSS_FEEDS.items():
        all_news.extend(fetch_rss(url, name))

    all_news.extend(fetch_cryptopanic())
    return all_news

