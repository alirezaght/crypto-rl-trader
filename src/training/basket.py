import datetime
import pandas as pd
from typing import List, Dict
from training.train import CryptoTrainer
from utils.data import interval_to_hours, print_spinner
from config_manager.schemas import Config



class Basket:
    def __init__(self, symbols: List[str], crypto_config: Config, stock_config: Config, train=True):
        self.assets = {
            symbol: CryptoTrainer(symbol=symbol, crypto_config=crypto_config, stock_config=stock_config, train=train)
            for symbol in symbols
        }
        self.crypto_config = crypto_config
        self.stock_config = stock_config
        self.train = train
        self.stocks = [symbol for symbol in symbols if "/" not in symbol]
        self.cryptos = [symbol for symbol in symbols if "/" in symbol]
        
    def get_signals(self, at_datetime: datetime.datetime) -> Dict[str, str]:
        signal_map = {
            0: "HOLD",
            1: "BUY slight chance of rise",
            2: "BUY moderate chance of rise",
            3: "BUY high chance of rise",
            4: "SELL slight chance of drop",
            5: "SELL moderate chance of drop",
            6: "SELL high chance of drop",
        }
        signals = {}
        for symbol, trainer in self.assets.items():
            try:
                window_days = self.crypto_config.window_days if "/" in symbol else self.stock_config.window_days
                action = trainer.predict(
                    from_date=at_datetime - datetime.timedelta(days=window_days + 14),
                    to_date=at_datetime
                )
                signals[symbol] = signal_map.get(action, "UNKNOWN")
            except Exception as e:
                signals[symbol] = f"ERROR: {str(e)}"
        return signals

    def backtrack(self, from_date: datetime.datetime, to_date: datetime.datetime, deposit: float = 1000.0) -> Dict:
        cash = deposit
        holdings = {symbol: 0.0 for symbol in self.assets.keys()}
        portfolio_log = []

        current_date = from_date
        
        interval = min(self.crypto_config.interval, self.stock_config.interval)
        
        if len(self.cryptos) == 0:
            interval = self.stock_config.interval
        elif len(self.stocks) == 0:
            interval = self.crypto_config.interval
        
        step = datetime.timedelta(hours=interval_to_hours(interval))
        
        predict_days = min(self.crypto_config.predict_days, self.stock_config.predict_days)
        
        if len(self.cryptos) == 0:
            predict_days = self.stock_config.predict_days
        elif len(self.stocks) == 0:
            predict_days = self.crypto_config.predict_days
            
        while current_date + datetime.timedelta(days=predict_days) < to_date:
            print_spinner()
            actions = []

            for symbol, trainer in self.assets.items():
                print_spinner()
                try:
                    window_days = self.crypto_config.window_days if "/" in symbol else self.stock_config.window_days
                    action = trainer.predict(
                        from_date=current_date - datetime.timedelta(days=window_days + 14),
                        to_date=current_date
                    )
                    price_data = trainer.fetch_price_at(current_date)
                    price = price_data["close"]

                    action_scores = {0: 0, 1: 1, 2: 2, 3: 3, 4: -1, 5: -2, 6: -3}
                    score = action_scores.get(action, 0)

                    actions.append({
                        "symbol": symbol,
                        "action": action,
                        "score": score,
                        "price": price
                    })
                except Exception as e:
                    portfolio_log.append(f"{current_date} ERROR {symbol}: {str(e)}")

            actions = sorted(actions, key=lambda x: -abs(x["score"]))

            for a in actions:
                symbol = a["symbol"]
                action = a["action"]
                price = a["price"]

                if action in [1, 2, 3] and cash > 0:
                    fraction = {1: 0.25, 2: 0.5, 3: 1.0}[action]
                    amount_to_spend = cash * fraction
                    holdings[symbol] += amount_to_spend / price
                    cash -= amount_to_spend
                    portfolio_log.append(f"{current_date} BUY {symbol} {fraction*100:.0f}% @ ${price:.2f}")

                elif action in [4, 5, 6] and holdings[symbol] > 0:
                    fraction = {4: 0.25, 5: 0.5, 6: 1.0}[action]
                    amount_to_sell = holdings[symbol] * fraction
                    cash += amount_to_sell * price
                    holdings[symbol] -= amount_to_sell
                    portfolio_log.append(f"{current_date} SELL {symbol} {fraction*100:.0f}% @ ${price:.2f}")

            current_date += step * predict_days

        final_prices = {
            symbol: self.assets[symbol].fetch_price_at(to_date)["close"]
            for symbol in self.assets
        }
        total_value = cash + sum(holdings[symbol] * final_prices[symbol] for symbol in holdings)

        return {
            "final_value": total_value,
            "profit": total_value - deposit,
            "logs": portfolio_log,
            "final_holdings": holdings,
            "final_prices": final_prices
        }


