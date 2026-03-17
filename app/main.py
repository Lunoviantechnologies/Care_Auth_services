from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.session import Base, engine
from app.core.config import settings

from app.db.models import admin_model, customer_model, worker_model
from app.api import auth_routes, admin_routes, worker_routes, customer_routes

# ✅ Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 IMPORTANT: Serve uploaded images
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


@app.get("/")
def root():
    return {"message": "API is running 🚀"}


# ✅ ROUTES
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(worker_routes.router)
app.include_router(customer_routes.router)
