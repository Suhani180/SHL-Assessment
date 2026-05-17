"""
Production-ready FastAPI backend
for SHL Conversational Assessment Recommender.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
# -----------------------------------------------------
# LOGGING
# -----------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------
# APP LIFECYCLE
# -----------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


# -----------------------------------------------------
# FASTAPI APP
# -----------------------------------------------------

app = FastAPI(
    title="SHL Assessment Recommender",
    version="1.0.0",
    lifespan=lifespan
)

# -----------------------------------------------------
# CORS
# -----------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# ROUTES
# -----------------------------------------------------

app.include_router(health_router)
app.include_router(chat_router)