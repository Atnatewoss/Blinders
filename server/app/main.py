"""FastAPI server for the neuro-symbolic governance system."""

from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

from .api import router as api_router

app = FastAPI(
    title="AI Fantasy League Commissioner API",
    description="Symbolic constitutional guardrail for autonomous agents.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "online", "engine": "neuro-symbolic-G1"}