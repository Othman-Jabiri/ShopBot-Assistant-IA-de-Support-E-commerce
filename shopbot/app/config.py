# ═══════════════════════════════════════════════════
# app/config.py — Configuration Mistral AI
# ═══════════════════════════════════════════════════

import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings

# Charge les variables depuis le fichier .env
load_dotenv()

# ── Vérification de la clé API ─────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError(
        "❌ MISTRAL_API_KEY manquante !\n"
        "Créez un fichier .env avec : MISTRAL_API_KEY=sk-votre-cle\n"
        "Obtenez votre clé sur : https://console.mistral.ai"
    )

# ── Configuration LLM ─────────────────────────────
# mistral-large-latest  → le plus capable, recommandé pour la production
# mistral-small-latest  → plus rapide/moins cher, bon pour les tests
LLM_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

llm = ChatMistralAI(
    model=LLM_MODEL,
    temperature=0,       # 0 = réponses déterministes et fiables
    max_tokens=600,      # Limite la longueur des réponses
    api_key=MISTRAL_API_KEY,
)

# ── Configuration Embeddings ──────────────────────
# mistral-embed est le modèle dédié pour vectoriser les textes (FAQ)
embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=MISTRAL_API_KEY,
)

# ── Chemins ───────────────────────────────────────
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/orders.db")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./indexing/faq_db")
DOCS_FOLDER = os.getenv("DOCS_FOLDER", "./data/docs")

print(f"✅ Configuration chargée — Modèle : {LLM_MODEL}")
