# ═══════════════════════════════════════════════════
# app/tools.py — Les 3 outils de l'agent ShopBot
# ═══════════════════════════════════════════════════
#
# IMPORTANT : La docstring de chaque @tool est lue
# par le LLM pour décider QUAND et COMMENT utiliser
# l'outil. Rédigez-la clairement et précisément.
#
# ═══════════════════════════════════════════════════

import os
import sqlite3
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/orders.db")


# ═══════════════════════════════════════════════════
# OUTIL 1 — Vérifier le statut d'une commande
# ═══════════════════════════════════════════════════

@tool
def check_order(order_id: str) -> str:
    """Vérifie le statut d'une commande client dans la base de données.

    Utilise cet outil dès qu'un client mentionne un numéro de commande,
    même sous des formes variées comme : #4521, commande 4521, order 4521,
    numéro 4521, ma commande...

    Args:
        order_id: Le numéro de la commande (chiffres uniquement, ex: "4521")

    Returns:
        Le statut complet : statut actuel, date d'expédition,
        livraison estimée et transporteur.
    """
    # Nettoie l'ID (retire # et espaces si présents)
    order_id = order_id.strip().lstrip("#")

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur  = conn.cursor()
        cur.execute(
            """SELECT id, status, shipped_at, eta, carrier, customer_name
               FROM orders WHERE id = ?""",
            (order_id,)
        )
        row = conn.fetchone() if False else cur.fetchone()
        conn.close()

        if not row:
            return (
                f"Commande #{order_id} introuvable dans notre système. "
                f"Vérifiez le numéro ou demandez au client de le retrouver "
                f"dans son email de confirmation."
            )

        order_id_db, status, shipped_at, eta, carrier, customer = row

        # Construction de la réponse selon le statut
        if status == "delivered":
            return (
                f"Commande #{order_id_db} de {customer} : "
                f"LIVRÉE le {eta}. Transporteur : {carrier}."
            )
        elif status == "shipped":
            return (
                f"Commande #{order_id_db} de {customer} : "
                f"EN TRANSIT — Expédiée le {shipped_at}, "
                f"livraison prévue le {eta}. Transporteur : {carrier}."
            )
        elif status == "processing":
            return (
                f"Commande #{order_id_db} de {customer} : "
                f"EN PRÉPARATION — Elle sera expédiée sous 24-48h."
            )
        elif status == "cancelled":
            return (
                f"Commande #{order_id_db} de {customer} : "
                f"ANNULÉE. Contactez le support pour plus d'informations."
            )
        else:
            return (
                f"Commande #{order_id_db} de {customer} : "
                f"Statut = {status}. Expédiée : {shipped_at}, "
                f"ETA : {eta}, Transporteur : {carrier}."
            )

    except sqlite3.Error as e:
        return f"Erreur base de données : {str(e)}. Veuillez réessayer."
    except Exception as e:
        return f"Erreur inattendue lors de la vérification : {str(e)}"


# ═══════════════════════════════════════════════════
# OUTIL 2 — Vérifier la disponibilité d'un produit
# ═══════════════════════════════════════════════════

@tool
def check_stock(product_ref: str) -> str:
    """Vérifie la disponibilité d'un produit ou d'une taille en stock.

    Utilise cet outil quand un client demande si un article est disponible,
    s'il reste des tailles, ou veut connaître la disponibilité d'un produit.

    Args:
        product_ref: La taille (S, M, L, XL, XXL) ou la référence produit
                     (ex: "L", "XL", "REF-123-BLEU-L")

    Returns:
        La quantité disponible et les alternatives si rupture de stock.
    """
    # ── Simulation d'un vrai inventaire ───────────
    # En production, remplacez ce dict par un appel API réel :
    # response = requests.get(f"{INVENTORY_API_URL}/stock?ref={product_ref}")
    # return response.json()

    stock_simulation = {
        "XS":  2,
        "S":   8,
        "M":   15,
        "L":   3,
        "XL":  0,
        "XXL": 6,
    }

    ref_upper = product_ref.strip().upper()

    # Recherche par taille exacte
    if ref_upper in stock_simulation:
        qty = stock_simulation[ref_upper]

        if qty == 0:
            # Propose des alternatives disponibles
            alternatives = [
                f"{taille} ({stock})"
                for taille, stock in stock_simulation.items()
                if stock > 0
            ]
            alts_str = ", ".join(alternatives)
            return (
                f"Taille {ref_upper} : RUPTURE DE STOCK. "
                f"Tailles disponibles : {alts_str}. "
                f"Vous pouvez activer une alerte de réapprovisionnement sur notre site."
            )
        elif qty <= 3:
            return (
                f"Taille {ref_upper} : {qty} unité(s) disponible(s). "
                f"⚠️ Stock limité — commandez rapidement !"
            )
        else:
            return f"Taille {ref_upper} : {qty} unités disponibles en stock."

    # Recherche par référence produit partielle
    matching = [k for k in stock_simulation if ref_upper in k]
    if matching:
        results = [f"{k}: {stock_simulation[k]} unité(s)" for k in matching]
        return f"Stock pour '{product_ref}' : " + ", ".join(results)

    return (
        f"Référence '{product_ref}' non trouvée dans notre catalogue. "
        f"Vérifiez la référence ou proposez au client de chercher "
        f"sur notre site avec le moteur de recherche."
    )


# ═══════════════════════════════════════════════════
# OUTIL 3 — Recherche web (promotions, actualités)
# ═══════════════════════════════════════════════════

# Tavily est une API de recherche web optimisée pour les LLMs.
# Clé gratuite sur https://tavily.com (1000 recherches/mois)

_tavily_key = os.getenv("TAVILY_API_KEY")

if _tavily_key:
    web_search = TavilySearchResults(
        max_results=2,
        name="web_search",
        description=(
            "Recherche des informations récentes sur internet. "
            "Utilise cet outil UNIQUEMENT pour : les promotions et soldes en cours, "
            "les nouveautés de la boutique, les actualités récentes. "
            "Ne l'utilise PAS pour les questions sur commandes ou stock "
            "(utilise check_order et check_stock à la place)."
        ),
    )
else:
    # Fallback si pas de clé Tavily : outil désactivé
    @tool
    def web_search(query: str) -> str:
        """Recherche des informations récentes sur les promotions.
        (Outil désactivé — configurez TAVILY_API_KEY dans .env pour l'activer)
        """
        return (
            "La recherche web n'est pas configurée. "
            "Pour les promotions en cours, orientez le client vers notre site web."
        )

# ── Liste finale des outils disponibles pour l'agent
tools = [check_order, check_stock, web_search]
