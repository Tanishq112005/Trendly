from fastapi import FastAPI
from app.modules.chat.router import chat_router
from app.core.database import db_manager

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trendly Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB and Redis on startup
    await db_manager.init_db()
    
    from app.core.redis_client import redis_manager
    await redis_manager.connect()


# Include Routers
app.include_router(chat_router)
from app.modules.admin.router import admin_router
app.include_router(admin_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
