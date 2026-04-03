from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.session import Base, engine
from app.core.config import settings

# Import models (IMPORTANT: ensures tables are registered)
from app.db.models import admin_model, customer_model, worker_model

# Import routers
from app.api import auth_routes, admin_routes, worker_routes, customer_routes
from app.api.contact_controller import router as contact_router
from app.api.settings_routes import router as settings_router
from app.api.api.v1.endpoints import otp


# ---------------- CREATE FASTAPI APP ----------------
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


# ---------------- DATABASE INIT (ASYNC CONTEXT) ----------------
# 🔥 This function runs in async context
# - engine.begin() → async DB connection
# - run_sync() → runs sync SQLAlchemy inside async safely


async def create_tables() -> None:
    """
    Create database tables using async engine.
    This bridges async engine with sync SQLAlchemy metadata.
    """
    async with engine.begin() as conn:  # ✅ async context manager
        await conn.run_sync(Base.metadata.create_all)
        # 🔁 run_sync executes sync code (create_all) inside async


# ---------------- STARTUP EVENT ----------------
# 🔥 FastAPI will call this when server starts
@app.on_event("startup")
async def startup() -> None:
    """
    Startup event runs in async event loop.
    Used for DB initialization, connections, etc.
    """
    await create_tables()  # ✅ awaited async function


# ---------------- CORS MIDDLEWARE ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- STATIC FILES ----------------
# Serve uploaded images (no async needed here)
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


# ---------------- ROOT ENDPOINT ----------------
@app.get("/")
def root() -> dict:
    """
    Simple sync route (no DB, so async not required)
    """
    return {"message": "API is running 🚀"}


# ---------------- ROUTES ----------------
# These routers internally use async endpoints
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(worker_routes.router)
app.include_router(customer_routes.router)
app.include_router(contact_router)
app.include_router(settings_router)
app.include_router(otp.router)
