from base.action import BaseActionProtected
from ..schemas import PairSuggestion, SuggestResponse
from firebase_admin.firestore import firestore


class SuggestAction(BaseActionProtected):
    
    def store_suggestion(self, data: PairSuggestion) -> SuggestResponse:        
        suggestion_ref = self.db.collection("pair_suggestions").document()
        suggestion_ref.set({
            "pair": data.pair,
            "ip": self.ip,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        return SuggestResponse(status="ok")