from base.action import BaseActionProtected
from ..schemas import ConfigResponse

class GetConfigAction(BaseActionProtected):
    def get(self):        
        pairs = self.config.PAIRS
        predict_days = self.config.PREDICT_DAYS
        interval = self.config.INTERVAL
        window_days = self.config.WINDOW_DAYS
        return ConfigResponse(
            pairs = pairs,
            predict_days = predict_days,
            interval = interval,
            window_days = window_days
        )