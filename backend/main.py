from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, signals, family, webhooks

import os

app = FastAPI(
    title="Safe & Sound API",
    description="Backend for the Safe & Sound application helping families check on elderly parents.",
    version="1.0.0"
)

# Configurable CORS — restrict in production via FRONTEND_URL env var
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [frontend_url] if frontend_url else ["*"]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(signals.router)
app.include_router(family.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Safe & Sound API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/debug/textbee")
async def debug_textbee():
    """Debug endpoint to check TextBee config. Remove in production."""
    return {
        "TEXTBEE_API_KEY_set": bool(os.getenv("TEXTBEE_API_KEY")),
        "TEXTBEE_DEVICE_ID_set": bool(os.getenv("TEXTBEE_DEVICE_ID")),
        "TEXTBEE_BASE_URL": os.getenv("TEXTBEE_BASE_URL", "https://api.textbee.dev/api/v1"),
        "JWT_SECRET_KEY_length": len(os.getenv("JWT_SECRET_KEY", "")),
    }
