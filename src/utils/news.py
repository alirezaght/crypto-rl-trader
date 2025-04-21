import feedparser
import requests
from utils.secret_manager import get_cryptopanic_key
from newspaper import Article
from utils.redis_cache import redis_cache

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

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

STOCK_RSS_FEEDS = {
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "NASDAQ": "https://www.nasdaq.com/feed/rssoutbound?category=Stock%20Market%20News",
    "Yahoo Finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,TSLA,GOOGL&region=US&lang=en-US",
    "Seeking Alpha": "https://seekingalpha.com/market-news/all.xml",
}

CRYPTOPANIC_API_KEY = get_cryptopanic_key().strip()
CRYPTOPANIC_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&filter=hot"


def extract_article_text(url):
    try:
        article = Article(url)
        article.download(input_html=requests.get(
            url,
            headers=HEADERS
        ).text)
        article.parse()
        return article.title, article.text
    except Exception as e:
        print(f"Failed to extract article: {e}")
        return None, None

# @redis_cache(ttl=3600 * 4)  
def fetch_rss(feed_url, source_name, items):
    response = requests.get(feed_url, headers=HEADERS, allow_redirects=True)
    if response.status_code != 200:
        print(f"Failed to fetch RSS from {source_name} - Status {response.status_code}")
        return []
    feed = feedparser.parse(response.content)
    articles = []
    for entry in feed.entries[:items]: 
        articles.append({
            "source": source_name,
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "content": extract_article_text(entry.link)[1] if entry.link else None,
        })
    return articles

@redis_cache(ttl=3600 * 4)
def fetch_cryptopanic(items):
    response = requests.get(CRYPTOPANIC_URL)
    data = response.json()
    articles = []
    for item in data.get("results", [])[:items]:
        articles.append({
            "source": "CryptoPanic",
            "title": item.get("title"),
            "link": item.get("url"),
            "published": item.get("published_at"),            
        })
    return articles

def get_all_crypto_news():
    all_news = []

    for name, url in RSS_FEEDS.items():
        all_news.extend(fetch_rss(url, name, 2))

    all_news.extend(fetch_cryptopanic(5))
    return all_news


def get_all_stock_news():
    all_news = []

    for name, url in STOCK_RSS_FEEDS.items():
        all_news.extend(fetch_rss(url, name, 2))

    return all_news


