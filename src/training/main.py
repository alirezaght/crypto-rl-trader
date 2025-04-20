import argparse
from training.basket import Basket
import json
from datetime import datetime
from dotenv import load_dotenv
from config_manager.config import get_config
from db.firestore import init_firebase
load_dotenv()




def main():
    
    crypto_config = get_config("crypto")
    stock_config = get_config("stock")
    
    symbols = stock_config.symbols
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtrack", action="store_true", default=False, help="Backtrack mode")
    parser.add_argument("--start", type=str, default=datetime.now(), help="Start date (e.g. 2025-01-01)")
    parser.add_argument("--end", type=str, default=datetime.now(), help="End date (e.g. 2025-03-28)")
    parser.add_argument("--deposit", type=float, help="Initial deposit in USD")
    args = parser.parse_args()    
    
    if args.backtrack:
        if not (args.start and args.end and args.deposit is not None):
            parser.error("--backtrack requires --start, --end, and --deposit.")
            
    
    basket = Basket(symbols, crypto_config, stock_config, train=True)
    
    if args.backtrack:        
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")        
        results = basket.backtrack(from_date=start_date, to_date=end_date, deposit=args.deposit)
        print("")
        print(f"Backtracking results:{json.dumps(results, indent=4)}")
    else:        
        results = basket.get_signals(datetime.now())
        print("")
        print("Signals for current date:")
        print(json.dumps(results, indent=4))

if __name__ == "__main__":   
    init_firebase()
    main()


