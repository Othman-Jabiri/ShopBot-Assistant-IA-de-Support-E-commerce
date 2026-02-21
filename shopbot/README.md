# 🛒 ShopBot — Assistant IA de Support E-commerce

> Chatbot intelligent de support client propulsé par **Mistral AI + LangChain + RAG**  
> Architecture complète : REST API · LLM · RAG · Agent ReAct · Vector Database · SQL · Audio

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Mistral AI](https://img.shields.io/badge/Mistral_AI-LLM-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green?style=flat-square&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-Agent-yellow?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-purple?style=flat-square)

---

## 📌 Description

ShopBot est un assistant IA de support client pour boutique en ligne. Il combine plusieurs technologies modernes pour offrir une expérience conversationnelle intelligente :

- **RAG** (Retrieval-Augmented Generation) : répond à partir de vos vrais documents FAQ
- **Agent ReAct** : raisonne et utilise des outils en temps réel (commandes, stock, web)
- **Mémoire conversationnelle** : garde le contexte de la conversation
- **API REST** : exposé via FastAPI, consommable par n'importe quel frontend
- **Interface chat** : style Spotify avec micro (STT) et lecture vocale (TTS)

---

## 🏗️ Architecture

```
Client (navigateur)
        ↓ HTTP POST /api/chat
API REST — FastAPI (app/main.py)
        ↓
Agent ReAct (app/agent.py)
        ↓
┌─────────────────────────────────────┐
│  LLM — Mistral AI (mistral-large)   │
│  RAG — FAISS (recherche FAQ)        │
│  Tool 1 — check_order (SQLite)      │
│  Tool 2 — check_stock (inventaire)  │
│  Tool 3 — web_search (Tavily)       │
└─────────────────────────────────────┘
```

---

## 🚀 Installation rapide

### Prérequis
- Python 3.9+
- Clé API Mistral → [console.mistral.ai](https://console.mistral.ai)
- Google Chrome ou Microsoft Edge

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/shopbot.git
cd shopbot
```

### 2. Environnement virtuel
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install --upgrade pip
pip install langchain==0.2.17
pip install langchain-core==0.2.43
pip install langchain-community==0.2.19
pip install langchain-mistralai==0.1.8
pip install aiohttp==3.9.5
pip install faiss-cpu==1.7.4
pip install python-dotenv fastapi uvicorn pypdf pydantic
pip install tavily-python  # optionnel — recherche web
```

### 4. Configuration
```bash
# Copiez le fichier exemple
cp .env.example .env
```

Éditez `.env` :
```env
MISTRAL_API_KEY=sk-votre-cle-mistral
TAVILY_API_KEY=tvly-votre-cle-tavily   # optionnel
DATABASE_PATH=./data/orders.db
CHROMA_DB_PATH=./indexing/faq_db
```

### 5. Préparer les données
```bash
# Créer la base de données des commandes (avec données de test)
python data/setup_db.py

# Créer une FAQ de démonstration et l'indexer
python indexing/indexer.py --create-demo
python indexing/indexer.py
```

### 6. Lancer ShopBot
```bash
uvicorn app.main:app --reload --port 8000
```

Ouvrez **http://localhost:8000** dans Chrome ou Edge 🎉

---

## 📁 Structure du projet

```
shopbot/
├── .env.example              # Template de configuration
├── requirements.txt          # Dépendances Python
├── README.md
│
├── app/
│   ├── config.py             # Configuration Mistral AI + embeddings
│   ├── tools.py              # 3 outils : check_order, check_stock, web_search
│   ├── agent.py              # Agent ReAct — appel direct API Mistral
│   └── main.py               # API REST FastAPI + serveur interface web
│
├── indexing/
│   └── indexer.py            # Indexation FAQ → FAISS (RAG)
│
├── static/
│   └── index.html            # Interface chat (style Spotify, audio STT/TTS)
│
├── data/
│   ├── setup_db.py           # Création base SQLite des commandes
│   └── docs/                 # Placez vos PDFs / TXTs FAQ ici
│
└── indexing/
    └── faq_db/               # Base vectorielle FAISS (générée automatiquement)
```

---

## 🧪 Tests

### Mode interactif (terminal)
```bash
python test.py
```

### Tests automatiques
```bash
python test.py --auto
```

### Via l'API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ma commande #4521 est en retard", "session_id": "test"}'
```

### Interface Swagger
Ouvrez **http://localhost:8000/docs**

---

## 🎙️ Fonctionnalités Audio

L'interface web intègre la **Web Speech API** du navigateur (Chrome/Edge requis) :

| Fonctionnalité | Description |
|---|---|
| 🎤 Speech-to-Text | Parlez au bot en maintenant le bouton micro |
| 🔊 Text-to-Speech | Le bot répond à voix haute automatiquement |
| ⚡ Vitesse réglable | 0.8× · 1× · 1.3× |
| 🔧 Diagnostic | Bouton de test pour vérifier micro et voix |

> ⚠️ Le micro nécessite d'ouvrir via `http://localhost:8000` (pas en double-cliquant le fichier HTML)

---

## 🛠️ Stack technique

| Catégorie | Technologie |
|---|---|
| Langage | Python 3.9+ |
| LLM | Mistral AI (mistral-large-latest) |
| Architecture IA | RAG · Agent ReAct |
| Framework IA | LangChain 0.2 |
| Vector Database | FAISS (Facebook AI) |
| REST API | FastAPI + Uvicorn |
| Base de données | SQLite |
| Recherche web | Tavily API |
| Frontend | HTML · CSS · JavaScript (Web Speech API) |

---

## 🔧 Variables d'environnement

| Variable | Description | Requis |
|---|---|---|
| `MISTRAL_API_KEY` | Clé API Mistral AI | ✅ Oui |
| `TAVILY_API_KEY` | Clé API Tavily (recherche web) | ❌ Optionnel |
| `DATABASE_PATH` | Chemin base SQLite commandes | ✅ Oui |
| `CHROMA_DB_PATH` | Chemin base vectorielle FAISS | ✅ Oui |
| `MISTRAL_MODEL` | Modèle Mistral à utiliser | ❌ Défaut : mistral-large-latest |

---

## 📈 Améliorations possibles

- [ ] Remplacer la simulation de stock par une vraie API d'inventaire
- [ ] Ajouter Redis pour la persistance des sessions entre redémarrages
- [ ] Dockeriser l'application pour le déploiement
- [ ] Ajouter un dashboard admin pour monitorer les conversations
- [ ] Intégrer OpenAI Whisper pour un STT de meilleure qualité
- [ ] Déployer sur un serveur cloud (Railway, Render, AWS)

---

## 👤 Auteur

Projet réalisé dans le cadre d'un apprentissage pratique du développement IA avec LangChain et les LLMs.

**Stack maîtrisée :** Python · LangChain · Mistral AI · RAG · FAISS · FastAPI · Agent ReAct

---

## 📄 Licence

MIT License — libre d'utilisation et de modification.
