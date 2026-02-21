# ═══════════════════════════════════════════════════
# test.py — Script de test interactif pour ShopBot
# ═══════════════════════════════════════════════════
#
# Usage :
#   python test.py           → Mode interactif (chat en direct)
#   python test.py --auto    → Tests automatiques prédéfinis
#
# ═══════════════════════════════════════════════════

import sys
import argparse
import time


def run_auto_tests():
    """Lance une série de tests automatiques pour valider le bot."""
    from app.agent import chat, reset_conversation

    print("=" * 55)
    print("  ShopBot — Tests automatiques")
    print("=" * 55)

    tests = [
        {
            "description": "Test 1 — Question sur une commande existante",
            "question":    "Bonjour, ma commande #4521 est en retard. Que se passe-t-il ?",
        },
        {
            "description": "Test 2 — Vérification de stock",
            "question":    "Est-ce que la taille L est encore disponible ?",
        },
        {
            "description": "Test 3 — Mémoire conversationnelle (suite du Test 2)",
            "question":    "Et en taille XL ?",
        },
        {
            "description": "Test 4 — Commande introuvable",
            "question":    "Ma commande numéro 9999 n'arrive pas.",
        },
        {
            "description": "Test 5 — Question sur la politique de retour (RAG)",
            "question":    "Quelle est votre politique de remboursement ?",
        },
    ]

    passed = 0
    for i, test in enumerate(tests):
        print(f"\n{'─' * 55}")
        print(f"📝 {test['description']}")
        print(f"👤 Client : {test['question']}")
        print(f"⏳ Traitement...")

        start = time.time()
        try:
            response = chat(test["question"])
            elapsed  = time.time() - start
            print(f"🤖 ShopBot ({elapsed:.1f}s) : {response}")
            passed += 1
        except Exception as e:
            print(f"❌ ERREUR : {str(e)}")

    print(f"\n{'=' * 55}")
    print(f"✅ Tests terminés : {passed}/{len(tests)} réussis")

    if passed < len(tests):
        print("\n⚠️  Vérifiez :")
        print("   1. Votre clé API Mistral dans .env")
        print("   2. La base de données : python data/setup_db.py")
        print("   3. La FAQ indexée : python indexing/indexer.py --create-demo")


def run_interactive():
    """Lance le mode chat interactif en ligne de commande."""
    from app.agent import chat, reset_conversation

    print("=" * 55)
    print("  ShopBot — Mode Interactif")
    print("  Tapez 'exit' pour quitter")
    print("  Tapez 'reset' pour effacer l'historique")
    print("  Tapez 'help' pour les commandes disponibles")
    print("=" * 55)
    print()

    while True:
        try:
            user_input = input("👤 Vous : ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("👋 Au revoir !")
                break

            elif user_input.lower() == "reset":
                reset_conversation()
                print("🔄 Conversation réinitialisée.\n")
                continue

            elif user_input.lower() == "help":
                print("\nCommandes disponibles :")
                print("  exit  → Quitter le programme")
                print("  reset → Effacer l'historique de conversation")
                print("  help  → Afficher cette aide\n")
                continue

            print("⏳ ShopBot réfléchit...", end="\r")
            start    = time.time()
            response = chat(user_input)
            elapsed  = time.time() - start

            print(f"🤖 ShopBot ({elapsed:.1f}s) : {response}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {str(e)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tester ShopBot")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Lancer les tests automatiques prédéfinis"
    )
    args = parser.parse_args()

    if args.auto:
        run_auto_tests()
    else:
        run_interactive()
