# ═══════════════════════════════════════════════════
# indexing/indexer.py — Indexation de la FAQ (RAG)
# ═══════════════════════════════════════════════════
#
# À lancer UNE SEULE FOIS avant de démarrer le bot.
# Relancez uniquement si vous mettez à jour les PDFs.
#
# Usage :
#   python indexing/indexer.py
#   python indexing/indexer.py --docs ./data/docs --output ./indexing/faq_db
#
# ═══════════════════════════════════════════════════

import os
import sys
import argparse

# Ajoute le dossier racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Remplacez par :
from langchain_community.vectorstores import FAISS

load_dotenv()


def index_faq(
    docs_folder: str = "./data/docs",
    output_dir:  str = "./indexing/faq_db",
    chunk_size:  int = 500,
    chunk_overlap: int = 50,
) -> None:
    """
    Indexe les documents de la FAQ dans une base vectorielle Chroma.

    Args:
        docs_folder:    Dossier contenant les PDFs/TXTs à indexer
        output_dir:     Dossier de sortie pour la base Chroma
        chunk_size:     Taille maximale d'un chunk en tokens
        chunk_overlap:  Chevauchement entre chunks consécutifs
    """
    from app.config import embeddings

    print("=" * 55)
    print("  ShopBot — Indexation de la FAQ")
    print("=" * 55)

    # ── Vérification du dossier source ────────────
    if not os.path.exists(docs_folder):
        print(f"\n❌ Dossier introuvable : {docs_folder}")
        print(f"   Créez le dossier et placez-y vos fichiers PDF ou TXT.")
        print(f"   Exemple : mkdir -p {docs_folder}")
        sys.exit(1)

    files = os.listdir(docs_folder)
    if not files:
        print(f"\n⚠️  Le dossier {docs_folder} est vide !")
        print(f"   Placez des fichiers .pdf ou .txt dans ce dossier.")
        print(f"\n💡 Pas de FAQ pour l'instant ? Créez un fichier FAQ de démo :")
        print(f"   python indexing/indexer.py --create-demo")
        sys.exit(1)

    print(f"\n📁 Dossier source : {docs_folder}")
    print(f"   Fichiers trouvés : {', '.join(files)}")

    # ── Chargement des documents ──────────────────
    print("\n📚 Chargement des documents...")
    documents = []

    # Charge les PDFs
    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
    if pdf_files:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(docs_folder, pdf_file)
            loader   = PyPDFLoader(pdf_path)
            docs     = loader.load()
            documents.extend(docs)
            print(f"   ✓ {pdf_file} — {len(docs)} pages")

    # Charge les fichiers TXT
    txt_files = [f for f in files if f.lower().endswith(".txt")]
    if txt_files:
        for txt_file in txt_files:
            txt_path = os.path.join(docs_folder, txt_file)
            loader   = TextLoader(txt_path, encoding="utf-8")
            docs     = loader.load()
            documents.extend(docs)
            print(f"   ✓ {txt_file} — {len(docs)} document(s)")

    if not documents:
        print(f"\n❌ Aucun fichier PDF ou TXT lisible trouvé dans {docs_folder}")
        sys.exit(1)

    print(f"\n   → {len(documents)} page(s)/document(s) chargé(s) au total")

    # ── Découpe en chunks ─────────────────────────
    print(f"\n✂️  Découpe en chunks (taille={chunk_size}, overlap={chunk_overlap})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Essaie de couper dans cet ordre : paragraphe, ligne, phrase, mot
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    print(f"   → {len(chunks)} chunks créés")

    # ── Création des embeddings + stockage Chroma ─
    print(f"\n🔮 Création des embeddings avec Mistral (mistral-embed)...")
    print(f"   (Cela peut prendre quelques secondes selon la taille des docs)")

    os.makedirs(output_dir, exist_ok=True)

    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
        
    )
    vectordb.save_local(output_dir)

    print(f"\n✅ Base vectorielle créée avec succès !")
    print(f"   Chemin : {output_dir}")
    print(f"   Vecteurs : {len(chunks)}")

    # ── Test de similarité ────────────────────────
    print(f"\n🧪 Test de recherche sémantique :")
    test_queries = ["retour remboursement", "délai livraison", "commande annulée"]

    for query in test_queries:
        results = vectordb.similarity_search(query, k=1)
        if results:
            preview = results[0].page_content[:80].replace("\n", " ")
            print(f"   '{query}' → {preview}...")
        else:
            print(f"   '{query}' → Aucun résultat")

    print(f"\n🚀 Vous pouvez maintenant lancer ShopBot :")
    print(f"   uvicorn app.main:app --reload --port 8000")
    print("=" * 55)


def create_demo_faq(docs_folder: str = "./data/docs") -> None:
    """Crée un fichier FAQ de démonstration pour tester l'indexation."""
    os.makedirs(docs_folder, exist_ok=True)

    demo_content = """FAQ ModeExpress — Politique de la boutique

LIVRAISONS
---
Délais de livraison standard : 3 à 5 jours ouvrés après expédition.
Livraison express disponible : 1 à 2 jours ouvrés (supplément de 4,99€).
La livraison gratuite est offerte pour toute commande supérieure à 50€.
Un email de confirmation avec le numéro de suivi est envoyé dès l'expédition.
Transporteurs partenaires : Colissimo, DHL, UPS selon la destination.

RETOURS ET REMBOURSEMENTS
---
Vous disposez de 30 jours à compter de la réception pour retourner un article.
Les articles doivent être dans leur état d'origine, non portés, avec les étiquettes.
Retours gratuits pour les clients membres du programme fidélité.
Pour initier un retour, connectez-vous à votre compte et cliquez sur "Retourner".
Le remboursement est effectué sous 5 à 10 jours ouvrés après réception du colis.
Le remboursement est effectué sur le moyen de paiement original.

TAILLES ET GUIDE DES TAILLES
---
Notre guide des tailles est disponible sur chaque fiche produit.
Taille S : tour de poitrine 84-88 cm, tour de taille 64-68 cm
Taille M : tour de poitrine 88-92 cm, tour de taille 68-72 cm
Taille L : tour de poitrine 96-100 cm, tour de taille 76-80 cm
Taille XL : tour de poitrine 104-108 cm, tour de taille 84-88 cm
En cas de doute entre deux tailles, nous recommandons de prendre la taille supérieure.

PAIEMENT
---
Moyens de paiement acceptés : Carte bancaire (Visa, Mastercard), PayPal, Apple Pay.
Les paiements sont sécurisés par le protocole SSL 3D Secure.
Le paiement en 3 fois sans frais est disponible pour les commandes supérieures à 100€.

COMPTE ET FIDÉLITÉ
---
L'inscription au programme fidélité est gratuite.
Vous cumulez 1 point pour chaque euro dépensé.
100 points = 5€ de réduction sur votre prochaine commande.
Les membres fidélité bénéficient des retours gratuits et d'un accès prioritaire aux ventes privées.

CONTACT ET SUPPORT
---
Service client disponible du lundi au vendredi de 9h à 18h.
Email : support@modeexpress.fr
Téléphone : 01 23 45 67 89
Délai de réponse moyen : 24 heures ouvrées.
"""

    demo_path = os.path.join(docs_folder, "faq_demo.txt")
    with open(demo_path, "w", encoding="utf-8") as f:
        f.write(demo_content)

    print(f"✅ FAQ de démonstration créée : {demo_path}")
    print(f"   Lancez maintenant : python indexing/indexer.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexer la FAQ de ShopBot")
    parser.add_argument("--docs",         default="./data/docs",       help="Dossier des documents")
    parser.add_argument("--output",       default="./indexing/faq_db", help="Dossier de sortie Chroma")
    parser.add_argument("--chunk-size",   type=int, default=500,       help="Taille des chunks")
    parser.add_argument("--chunk-overlap",type=int, default=50,        help="Chevauchement des chunks")
    parser.add_argument("--create-demo",  action="store_true",         help="Créer une FAQ de démonstration")
    args = parser.parse_args()

    if args.create_demo:
        create_demo_faq(args.docs)
    else:
        index_faq(
            docs_folder=args.docs,
            output_dir=args.output,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
