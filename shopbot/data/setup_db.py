# ═══════════════════════════════════════════════════
# data/setup_db.py — Création de la base de données SQLite
# ═══════════════════════════════════════════════════
#
# Crée la base de données des commandes avec des données
# de test pour pouvoir tester ShopBot immédiatement.
#
# Usage :
#   python data/setup_db.py
#
# ═══════════════════════════════════════════════════

import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/orders.db")


def setup_database():
    """Crée la base de données et insère des commandes de test."""

    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cur  = conn.cursor()

    # ── Création de la table commandes ────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id            TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            status        TEXT NOT NULL,
            shipped_at    TEXT,
            eta           TEXT,
            carrier       TEXT,
            total_amount  REAL,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Données de test ───────────────────────────
    # Statuts possibles : processing, shipped, delivered, cancelled
    test_orders = [
        ("4521", "Karim Benali",   "karim@example.com",   "shipped",     "2025-02-18", "2025-02-21", "Colissimo", 89.99),
        ("4520", "Sarah Martin",   "sarah@example.com",   "delivered",   "2025-02-15", "2025-02-18", "DHL",       45.50),
        ("4519", "Lucas Dupont",   "lucas@example.com",   "processing",  None,         None,          None,        120.00),
        ("4518", "Emma Lefebvre",  "emma@example.com",    "shipped",     "2025-02-17", "2025-02-20", "UPS",       67.80),
        ("4517", "Thomas Bernard", "thomas@example.com",  "cancelled",   None,         None,          None,        34.99),
        ("4516", "Julie Moreau",   "julie@example.com",   "delivered",   "2025-02-10", "2025-02-13", "Colissimo", 210.50),
        ("4515", "Nicolas Petit",  "nicolas@example.com", "shipped",     "2025-02-19", "2025-02-22", "DHL",       78.00),
        ("1000", "Test Client",    "test@example.com",    "processing",  None,         None,          None,        50.00),
    ]

    # Insère les données de test (ignore si déjà présentes)
    cur.executemany("""
        INSERT OR IGNORE INTO orders
            (id, customer_name, customer_email, status, shipped_at, eta, carrier, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, test_orders)

    conn.commit()

    # ── Vérification ──────────────────────────────
    cur.execute("SELECT COUNT(*) FROM orders")
    count = cur.fetchone()[0]
    conn.close()

    print("=" * 55)
    print("  ShopBot — Base de données créée")
    print("=" * 55)
    print(f"\n✅ Base de données : {DATABASE_PATH}")
    print(f"   {count} commandes disponibles\n")
    print("   Commandes de test disponibles :")
    print("   ┌──────────┬──────────────────┬─────────────┐")
    print("   │ N°       │ Client           │ Statut      │")
    print("   ├──────────┼──────────────────┼─────────────┤")
    for order in test_orders:
        print(f"   │ #{order[0]:<8}│ {order[1]:<16} │ {order[3]:<11} │")
    print("   └──────────┴──────────────────┴─────────────┘")
    print(f"\n💡 Testez avec : 'Ma commande #4521 est en retard'")


if __name__ == "__main__":
    setup_database()
