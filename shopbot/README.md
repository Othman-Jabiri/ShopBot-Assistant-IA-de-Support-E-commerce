# ShopBot — Assistant Support e-commerce IA
## Propulsé par Mistral AI + LangChain

---

## 🚀 Démarrage rapide (Windows)

### Étape 1 — Configurer l'environnement

```powershell
# Ouvrez PowerShell dans le dossier shopbot
cd C:\shopbot

# Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2 — Configurer les clés API

```powershell
# Copiez le fichier exemple
copy .env.example .env

# Editez .env et remplissez :
# MISTRAL_API_KEY=sk-votre-cle   (https://console.mistral.ai)
# TAVILY_API_KEY=tvly-votre-cle  (https://tavily.com - optionnel)
```

### Étape 3 — Préparer les données

```powershell
# Créer la base de données des commandes (avec données de test)
python data/setup_db.py

# Créer une FAQ de démo et l'indexer
python indexing/indexer.py --create-demo
python indexing/indexer.py
```

### Étape 4 — Lancer et tester

```powershell
# Test en ligne de commande (mode interactif)
python test.py

# Tests automatiques
python test.py --auto

# Lancer l'API REST
uvicorn app.main:app --reload --port 8000
# Interface de test : http://localhost:8000/docs
```

---

## 📁 Structure du projet

```
shopbot/
├── .env.example        → Modèle de configuration (copiez en .env)
├── requirements.txt    → Dépendances Python
├── test.py             → Script de test interactif
│
├── app/
│   ├── config.py       → Configuration Mistral AI
│   ├── tools.py        → Les 3 outils de l'agent
│   ├── agent.py        → Agent LangChain principal
│   └── main.py         → API REST FastAPI
│
├── indexing/
│   └── indexer.py      → Indexation FAQ → base vectorielle Chroma
│
└── data/
    ├── setup_db.py     → Création base SQLite commandes
    └── docs/           → Placez vos PDFs FAQ ici
```

---

## 🛠️ Modèles Mistral disponibles

Modifiez `MISTRAL_MODEL` dans votre `.env` :

| Modèle                  | Vitesse | Coût | Recommandé pour       |
|-------------------------|---------|------|-----------------------|
| `mistral-large-latest`  | Lent    | €€€  | Production            |
| `mistral-small-latest`  | Rapide  | €    | Tests / développement |
| `open-mistral-7b`       | Rapide  | €    | Volume élevé          |
