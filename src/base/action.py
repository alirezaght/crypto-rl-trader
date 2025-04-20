from fastapi import Depends, Request
from fastapi.params import Depends as DependsType
from typing import Optional
from utils.security import get_current_user
from config_manager.config import get_db_config
from db.firestore import get_db
from config_manager.config import DBConfig
from .middleware.request import get_current_request
from utils.ip import get_client_ip
from firebase_admin.firestore import firestore
import logging

logging.basicConfig(level=logging.INFO)


class BaseAction:
    def __init__(self, db: firestore.Client = Depends(get_db), request: Optional[Request] = Depends(get_current_request), db_config: DBConfig = Depends(get_db_config)):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = db
        if isinstance(self.db, DependsType):
            self.db = get_db()        
            
        self.db_config = db_config
        if isinstance(self.db_config, DependsType):
            self.db_config = get_db_config()
        
        self.request = request
        if isinstance(self.request, DependsType):
            self.request = get_current_request()
        
        if self.request is not None:
            self.ip = get_client_ip(self.request)
    
    
class BaseActionProtected(BaseAction):
    def __init__(self, user=Depends(get_current_user), db_config: DBConfig = Depends(get_db_config), db: firestore.Client = Depends(get_db), request: Optional[Request] = Depends(get_current_request)):
        super().__init__(db = db, request=request, db_config=db_config)
        self.user = user
        if isinstance(self.user, DependsType):
            self.user = get_current_user()
        
        