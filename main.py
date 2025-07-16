from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from services.db import init_db_pool, close_db_pool
from routes import session, message, utility

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bridgit AI Voice API", 
    version="2.0.0",
    description="Real-time voice translation and communication platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Initialize CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db_pool()
    logger.info("Startup: DB initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()
    logger.info("Shutdown: DB pool closed.")

app.include_router(session.router)
app.include_router(message.router)
app.include_router(utility.router)