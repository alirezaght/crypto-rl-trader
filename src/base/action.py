from fastapi import Depends, Request
from fastapi.params import Depends as DependsType
from typing import Optional
from utils.security import get_current_user
from config_manager.config import get_config
from db.firestore import get_db
from config_manager.config import Config
from .middleware.request import get_current_request
from utils.ip import get_client_ip
from firebase_admin.firestore import firestore
import logging

logging.basicConfig(level=logging.INFO)


class BaseAction:
    def __init__(self, db: firestore.Client = Depends(get_db), request: Optional[Request] = Depends(get_current_request)):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = db
        if isinstance(self.db, DependsType):
            self.db = get_db()
        self.request = request
        if self.request is not None and not isinstance(db, DependsType):
            self.ip = get_client_ip(self.request)
    
    
class BaseActionProtected(BaseAction):
    def __init__(self, user=Depends(get_current_user), config: Config = Depends(get_config), db: firestore.Client = Depends(get_db), request: Optional[Request] = Depends(get_current_request)):
        super().__init__(db = db, request=request)
        self.user = user
        self.config = config
        