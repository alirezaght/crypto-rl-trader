# 🧠 Reinforcement Learning Crypto Trader

[![Try Online](https://img.shields.io/badge/Launch%20App-SynapSignal-blue?style=for-the-badge)](https://synapsignal.com)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A Deep Reinforcement Learning system that uses PPO to learn profitable trading strategies across multiple cryptocurrencies using historical OHLCV data. The agent predicts actions like **buy**, **sell**, or **hold** for the next month based on the last 90 days of 4H market data — enhanced with technical indicators.

## 📦 Features

- ✅ Supports multiple assets via `Basket` abstraction (BTC, ETH, etc.)
- ✅ PPO-based trading agents trained per symbol
- ✅ Real-time signal generation
- ✅ Backtesting with profit tracking and logging
- ✅ Persistent model + vector normalization saving/loading
- ✅ **Try it online for free at [Synap Signal](https://synapsignal.com)** 🚀
---

## 🚀 Installation

### 1. Clone the repo

```bash
git clone https://github.com/alirezaght/crypto-rl-trader.git
cd crypto-rl-trader
```

### 2. Install dependencies
It’s recommended to use a virtual environment (conda or venv).

```bash
pip install -r requirements.txt
```
⚠️ Make sure you have Python 3.9+ and an active Binance API connection (for fetching price data).

## Usage
### 📄 Environment Configuration
This project uses a .env file. You’ll define the trading interval, window size, prediction horizon, and the crypto pairs to monitor or train.
```bash
# .env

INTERVAL=4h           # Options: 1h, 4h, 1d
WINDOW_DAYS=90        # How many days of history to use for each observation
PREDICT_DAYS=30       # How far ahead to predict
PAIRS=BTCUSDT,ETHUSDT,BNBUSDT,XRPUSDT,LTCUSDT  # Comma-separated list of trading pairs
```
ℹ️ You can update these values anytime before running the training or main script. The model will re-train if it doesn’t find saved checkpoints for the new config.

### ▶️ Generate real-time trading signals
```
python main.py
```
You’ll get something like:
```json
{
    "BTCUSDT": "BUY (>50%)",
    "ETHUSDT": "HOLD (<5%)",
    "XRPUSDT": "SELL (0-25%)"
}
```
`>50%` means to expect more than 50% price change in the next 30 days.
### 📉 Run backtest over a time window
```bash
python main.py --backtrack --start 2024-01-01 --end 2025-03-28 --deposit 1000
```
Output:
```json
{
    "final_value": 1420.55,
    "profit": 420.55,
    "logs": [
        "2024-01-15 BUY BTCUSDT 50% @ $41200.00",
        "2024-02-20 SELL BTCUSDT 100% @ $52890.00",
        ...
    ]
}
```
## 📌 Notes
- Models and normalization stats are saved as BTCUSDT_90_30_4h.zip and vec_BTCUSDT_90_30_4h.pkl
- Cached training is skipped if these files already exist
- Training takes a few minutes depending on your machine

---

🌐 Try it Online

You can try this project via a friendly UI on **[Synap Signal](https://synapsignal.com)** — no setup required, free to use.

---


## 📜 License
AGPL v3 License


