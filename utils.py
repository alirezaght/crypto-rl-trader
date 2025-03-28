import ta
from binance.client import Client
import datetime
import pandas as pd
from joblib import Memory
import os
memory = Memory(location='./.cache', verbose=0)

spinner = ["-", "\\", "|", "/"]
spinner_index = 0

def get_candle_count(days: int, interval: str) -> int:
    interval_map = {
        "1h": 24, "4h": 6, "1d": 1
    }
    return days * interval_map[interval]


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
def fetch_data(symbol="BTCUSDT", interval="4h", start_date: datetime.datetime = None, end_date: datetime.datetime = None, lookback_days=500):
    print_spinner()
    client = Client()
    end_time = datetime.datetime.now() if end_date is None else end_date
    start_time = start_date if start_date else end_time - datetime.timedelta(days=lookback_days)
    
    klines = client.get_historical_klines(
        symbol,
        interval,
        start_time.strftime("%d %b %Y %H:%M:%S"),
        end_time.strftime("%d %b %Y %H:%M:%S")
    )
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ])
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    return df

def interval_to_hours(interval: str) -> int:
        unit = interval[-1]
        num = int(interval[:-1])
        return num * (1 if unit == 'h' else 24 if unit == 'd' else 1)
    
    
def print_spinner():    
    global spinner_index
    print(f"\r{spinner[spinner_index]}", end="", flush=True)
    spinner_index = (spinner_index + 1) % len(spinner)
    