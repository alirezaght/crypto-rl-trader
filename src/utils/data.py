import pandas as pd
import datetime
import ta
from binance.client import Client
import asyncio
import numpy as np
from utils.redis_cache import redis_cache
import yfinance as yf
from typing import Literal
from base.schemas import MarketType

spinner = ["-", "\\", "|", "/"]
spinner_index = 0

def get_candle_count(days: int, interval: str, type: MarketType) -> int:
    interval_map = {
        "1h": 24, "4h": 6, "1d": 1
    } if type == "crypto" else {
        "1h": 6, "1d": 1
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

def chunk_dict(d, chunk_size):
    items = list(d.items())
    for i in range(0, len(items), chunk_size):
        yield dict(items[i:i + chunk_size])

def add_technical_indicators(df):
    df = df.copy()
    close = df["close"]

    # Momentum
    df["rsi"] = ta.momentum.RSIIndicator(close=close).rsi()
    df["roc"] = ta.momentum.ROCIndicator(close=close).roc()
    df["stoch_k"] = ta.momentum.StochasticOscillator(high=df["high"], low=df["low"], close=close).stoch()
    df["stoch_d"] = ta.momentum.StochasticOscillator(high=df["high"], low=df["low"], close=close).stoch_signal()

    # Trend
    macd = ta.trend.MACD(close=close)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["ema_20"] = ta.trend.EMAIndicator(close=close, window=20).ema_indicator()
    df["ema_50"] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
    df["adx"] = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=close).adx()

    # Volatility
    bb = ta.volatility.BollingerBands(close=close)
    df["bollinger_mavg"] = bb.bollinger_mavg()
    df["bollinger_hband"] = bb.bollinger_hband()
    df["bollinger_lband"] = bb.bollinger_lband()
    df["atr"] = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=close).average_true_range()

    # Volume
    df["obv"] = ta.volume.OnBalanceVolumeIndicator(close=close, volume=df["volume"]).on_balance_volume()

    df = df.bfill().ffill()
    return df

def get_binance_client():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    return Client(api_key=None, api_secret=None, tld="us")

def clamp_to_hour(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


@redis_cache(ttl=3600 * 24)
def fetch_data(
    symbol="BTC/USD",
    interval="4h",
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    lookback_days=500
):
    
    print_spinner()
        
    end_time = datetime.datetime.now() if end_date is None else end_date
    start_time = start_date if start_date else end_time - datetime.timedelta(days=lookback_days)
    
    if "/" in symbol:

        symbol = symbol.replace("/", "").replace("USD","USDT").upper()
        client = get_binance_client()
        

        klines = client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_time.strftime("%d %b %Y %H:%M:%S"),
            end_str=end_time.strftime("%d %b %Y %H:%M:%S")
        )

        if not klines:
            raise ValueError("No data returned from Binance.")

        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df
    else:
        yf_interval = interval if interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "1wk", "1mo"} else "1h"
        df = yf.download(symbol, start=start_time, end=end_time, interval=yf_interval)
        if df.empty:
            raise ValueError(f"No data returned from Yahoo Finance for {symbol}.")

        df.reset_index(inplace=True)        
        
        df.rename(columns={"Datetime": "timestamp", "Date": "timestamp", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]        
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df



def get_recent_data(symbol, interval, days=7):
    dt_to = datetime.datetime.now()
    dt_from = dt_to - datetime.timedelta(days=days)
    return fetch_data(symbol, interval=interval, start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to))

def get_pair_volume(symbol, interval, days=7):
    df = get_recent_data(symbol, interval, days)
    return df["volume"].sum()

def get_pair_volatility(symbol, interval, days=7):
    df = get_recent_data(symbol, interval, days)
    return df["close"].pct_change().std()

def get_recent_return(symbol, interval, days=7):
    df = get_recent_data(symbol, interval, days)
    return (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]


def rank_hot_pairs(pairs, interval, days=7):
    scores = []
    metrics = []    
    for symbol in pairs:
        try:
            volume = get_pair_volume(symbol, interval, days)
            volatility = get_pair_volatility(symbol, interval, days)
            recent_return = get_recent_return(symbol, interval, days)
            metrics.append((symbol, volume, volatility, recent_return))
        except Exception as e:
            print(f"Skipping {symbol} due to error: {e}")

    if not metrics:
        return []

    # Convert to NumPy arrays for normalization
    symbols, volumes, volatilities, returns = zip(*metrics)
    volumes = np.array(volumes)
    volatilities = np.array(volatilities)
    returns = np.array(returns)

    # Normalize using min-max scaling
    def normalize(arr):
        return (arr - np.min(arr)) / (np.ptp(arr) + 1e-8)

    vol_norm = normalize(volumes)
    vola_norm = normalize(volatilities)
    ret_norm = normalize(returns)

    # Compute final score
    for i, symbol in enumerate(symbols):
        score = 0.4 * vol_norm[i] + 0.3 * vola_norm[i] + 0.3 * ret_norm[i]
        scores.append((symbol, score))

    return [s[0] for s in sorted(scores, key=lambda x: x[1], reverse=True)]


