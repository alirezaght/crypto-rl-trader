from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging
from db.firestore import init_firebase
from base.middleware.request import RequestContextMiddleware
from routes.config.route import router as config_router
from routes.predict.route import router as predict_router
from routes.suggest.route import router as suggest_router
from routes.train.route import router as train_router
from exception.validation import register_validation_handlers
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up...")
    init_firebase()
    yield
    logger.info("💤 Shutting down...")
    


app = FastAPI(    
    docs_url=None,    
    redoc_url=None,    
    openapi_url=None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(config_router)
app.include_router(predict_router)
app.include_router(suggest_router)
app.include_router(train_router)


register_validation_handlers(app)

@app.get("/health")
def health():
    return {"status": "ok"}
