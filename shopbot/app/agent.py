# ═══════════════════════════════════════════════════
# app/agent.py — ShopBot Agent
# Fix définitif : appel direct API Mistral
# Compatible Python 3.9 + Windows
# ═══════════════════════════════════════════════════

import os
import json
import logging
import warnings
import requests

warnings.filterwarnings("ignore")
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_core").setLevel(logging.ERROR)
logging.getLogger("langchain_community").setLevel(logging.ERROR)

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from app.config import embeddings, CHROMA_DB_PATH, MISTRAL_API_KEY
from app.tools import check_order, check_stock

load_dotenv()

# ═══════════════════════════════════════════════════
# 1. RETRIEVER — FAISS
# ═══════════════════════════════════════════════════

if os.path.exists(CHROMA_DB_PATH):
    vectordb  = FAISS.load_local(
        CHROMA_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    print(f"✅ Base vectorielle chargée depuis : {CHROMA_DB_PATH}")
else:
    print(f"⚠️  Base vectorielle introuvable. Lancez : python indexing/indexer.py")
    retriever = None


def get_faq_context(question: str) -> str:
    if retriever is None:
        return "Base FAQ non disponible."
    try:
        docs = retriever.invoke(question)
        return "\n---\n".join([d.page_content for d in docs]) if docs else ""
    except Exception as e:
        return ""


# ═══════════════════════════════════════════════════
# 2. DÉFINITION DES TOOLS POUR L'API MISTRAL
# ═══════════════════════════════════════════════════

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_order",
            "description": "Vérifie le statut d'une commande client. Utilise cet outil dès qu'un numéro de commande est mentionné (ex: #4521, commande 4521).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Le numéro de la commande, chiffres uniquement (ex: '4521')"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Vérifie la disponibilité d'un produit ou d'une taille en stock. Utilise cet outil quand le client demande si un article est disponible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ref": {
                        "type": "string",
                        "description": "La taille (S, M, L, XL, XXL) ou référence produit"
                    }
                },
                "required": ["product_ref"]
            }
        }
    }
]

# Mapping nom → fonction Python
TOOLS_MAP = {
    "check_order": lambda args: check_order.invoke(args),
    "check_stock": lambda args: check_stock.invoke(args),
}

SYSTEM_PROMPT = """Tu es ShopBot, l'assistant IA de ModeExpress, une boutique de vêtements en ligne.
Tu aides les clients avec leurs questions sur les commandes, le stock, les retours et les promotions.

RÈGLES :
1. Réponds TOUJOURS en français, avec un ton professionnel et chaleureux.
2. Sois concis : 2-4 phrases maximum.
3. Propose toujours une alternative si un produit est indisponible.
4. Si tu ne sais pas, dis-le honnêtement.

Contexte FAQ :
{faq_context}
"""


# ═══════════════════════════════════════════════════
# 3. APPEL DIRECT API MISTRAL (contourne LangChain)
# ═══════════════════════════════════════════════════

def call_mistral(messages: list, use_tools: bool = True) -> dict:
    """Appelle directement l'API Mistral."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-large-latest",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 600,
    }
    if use_tools:
        payload["tools"] = TOOLS_SCHEMA
        payload["tool_choice"] = "auto"

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ═══════════════════════════════════════════════════
# 4. MEMORY SIMPLE (liste de messages par session)
# ═══════════════════════════════════════════════════

def create_memory() -> list:
    """Crée une nouvelle mémoire vide (liste de messages)."""
    return []


def create_agent_executor(memory: list) -> list:
    """Retourne la mémoire — pour compatibilité avec main.py."""
    return memory


# ═══════════════════════════════════════════════════
# 5. FONCTION PRINCIPALE DE CHAT
# ═══════════════════════════════════════════════════

def chat_with_memory(question: str, history: list) -> str:
    """
    Envoie une question à Mistral avec gestion des tools et de l'historique.

    Args:
        question: La question de l'utilisateur
        history:  Liste des messages précédents (modifiée en place)

    Returns:
        La réponse textuelle du bot
    """
    faq_ctx = get_faq_context(question)

    # Construit le system prompt avec le contexte FAQ
    system = SYSTEM_PROMPT.format(faq_context=faq_ctx if faq_ctx else "Aucun contexte FAQ disponible.")

    # Prépare les messages : system + historique + nouvelle question
    messages = [{"role": "system", "content": system}]
    messages += history[-10:]  # Garde les 10 derniers échanges
    messages.append({"role": "user", "content": question})

    # ── Boucle ReAct : max 5 itérations ──────────
    for iteration in range(5):
        result = call_mistral(messages, use_tools=True)
        choice  = result["choices"][0]
        message = choice["message"]

        # Cas 1 : le modèle appelle un ou plusieurs tools
        if choice.get("finish_reason") == "tool_calls" and message.get("tool_calls"):
            # Ajoute le message de l'assistant avec les tool_calls
            messages.append({
                "role":       "assistant",
                "content":    message.get("content") or "",
                "tool_calls": message["tool_calls"],
            })

            # Exécute chaque tool et ajoute le résultat
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                tool_id   = tool_call["id"]

                if tool_name in TOOLS_MAP:
                    tool_result = TOOLS_MAP[tool_name](tool_args)
                else:
                    tool_result = f"Outil '{tool_name}' non trouvé."

                # Ajoute le résultat du tool avec l'ID correct
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_id,
                    "name":         tool_name,
                    "content":      str(tool_result),
                })

            # Continue la boucle pour que Mistral génère la réponse finale
            continue

        # Cas 2 : réponse finale
        final_answer = message.get("content", "Je n'ai pas pu générer une réponse.")

        # Sauvegarde dans l'historique
        history.append({"role": "user",      "content": question})
        history.append({"role": "assistant", "content": final_answer})

        # Garde max 20 messages en historique
        if len(history) > 20:
            history[:] = history[-20:]

        return final_answer

    return "Désolé, je n'ai pas pu traiter votre demande. Réessayez ou contactez notre support."


# ═══════════════════════════════════════════════════
# 6. INTERFACE COMPATIBLE AVEC test.py ET main.py
# ═══════════════════════════════════════════════════

# Session par défaut pour test.py
_default_history = []


def chat(question: str) -> str:
    """Interface simple pour test.py."""
    return chat_with_memory(question, _default_history)


def reset_conversation():
    """Efface l'historique de la session par défaut."""
    global _default_history
    _default_history = []
    print("🔄 Conversation réinitialisée.")