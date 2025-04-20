from base.action import BaseActionProtected
from ..schemas import ConfigResponse

class GetConfigAction(BaseActionProtected):
    
    def get(self):        
        symbols = self.db_config.PAIRS + self.db_config.STOCKS
        predict_days = self.db_config.PREDICT_DAYS
        predict_days_stock = self.db_config.PREDICT_DAYS_STOCK
        interval = self.db_config.INTERVAL
        interval_stock = self.db_config.INTERVAL_STOCK
        window_days = self.db_config.WINDOW_DAYS
        window_days_stock = self.db_config.WINDOW_DAYS_STOCK
        return ConfigResponse(
            symbols=symbols,
            predict_days=predict_days,
            predict_days_stock=predict_days_stock,
            interval=interval,
            interval_stock=interval_stock,
            window_days=window_days,
            window_days_stock=window_days_stock
        )