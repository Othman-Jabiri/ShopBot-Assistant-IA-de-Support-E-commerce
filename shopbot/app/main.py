# ═══════════════════════════════════════════════════
# app/main.py — API REST + Interface Web ShopBot
# ═══════════════════════════════════════════════════

import os
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.agent import chat_with_memory

load_dotenv()

app = FastAPI(title="ShopBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sert l'interface web depuis /static ────────────
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Sessions
sessions: Dict[str, list] = {}

def get_session(sid: str) -> list:
    if sid not in sessions:
        sessions[sid] = []
    return sessions[sid]


# ── MODÈLES ───────────────────────────────────────
class ChatRequest(BaseModel):
    message: str    = Field(..., example="Ma commande #4521 est en retard ?")
    session_id: str = Field(default="default")

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ResetRequest(BaseModel):
    session_id: str = Field(default="default")


# ── ROUTES ────────────────────────────────────────
@app.get("/")
async def home():
    """Sert l'interface chat directement dans le navigateur."""
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "ShopBot API — /docs pour tester, placez index.html dans /static"}

@app.get("/health")
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model": os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
        "active_sessions": len(sessions),
    }

# Route /api/chat pour que le JS appelle /api/chat
@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message vide.")
    try:
        history  = get_session(request.session_id)
        response = chat_with_memory(request.message, history)
        return ChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Compatibilité avec l'ancien /chat
@app.post("/chat", response_model=ChatResponse)
async def chat_legacy(request: ChatRequest):
    return await chat_api(request)

@app.post("/api/reset")
async def reset_api(request: ResetRequest):
    if request.session_id in sessions:
        del sessions[request.session_id]
        return {"message": f"Session '{request.session_id}' réinitialisée."}
    return {"message": "Session introuvable."}

@app.post("/reset")
async def reset_legacy(request: ResetRequest):
    return await reset_api(request)

@app.get("/sessions")
async def list_sessions():
    return {"active_sessions": len(sessions), "session_ids": list(sessions.keys())}