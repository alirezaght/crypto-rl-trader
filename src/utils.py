import requests
import pandas as pd
import datetime
from joblib import Memory
import ta
from secret_manager import get_twelvedata_key


api_key = get_twelvedata_key()

memory = Memory(location='./.cache', verbose=0)

spinner = ["-", "\\", "|", "/"]
spinner_index = 0

def get_candle_count(days: int, interval: str) -> int:
    interval_map = {
        "1h": 24, "4h": 6, "1d": 1
    }
    return days * interval_map[interval]

def interval_to_hours(interval: str) -> int:
    unit = interval[-1]
    num = int(interval[:-1])
    return num * (1 if unit == 'h' else 24 if unit == 'd' else 1)

def print_spinner():
    global spinner_index
    print(f"\r{spinner[spinner_index]}", end="", flush=True)
    spinner_index = (spinner_index + 1) % len(spinner)

def add_technical_indicators(df):
    df = df.copy()
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
    df["macd"] = ta.trend.MACD(close=df["close"]).macd()
    df["macd_signal"] = ta.trend.MACD(close=df["close"]).macd_signal()
    df["ema_20"] = ta.trend.EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["ema_50"] = ta.trend.EMAIndicator(close=df["close"], window=50).ema_indicator()
    df = df.dropna()
    return df

@memory.cache
def fetch_data(
    symbol="BTC/USD",
    interval="4h",
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    lookback_days=500
):
    print_spinner()

    if not api_key:
        raise ValueError("TWELVEDATA_API_KEY not found in environment variables")

    end_time = datetime.datetime.now() if end_date is None else end_date
    start_time = start_date if start_date else end_time - datetime.timedelta(days=lookback_days)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "start_date": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "apikey": api_key,
        "format": "JSON",
        "outputsize": 5000
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if "values" not in data:
        raise ValueError(f"Unexpected response from Twelve Data: {data}")

    df = pd.DataFrame(data["values"])
    df.columns = [col.lower() for col in df.columns]
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.rename(columns={"datetime": "timestamp"})
    df = df[["timestamp", "open", "high", "low", "close"]]
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df