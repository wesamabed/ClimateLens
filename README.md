[![ETL CI](https://github.com/wesamabed/ClimateLens/actions/workflows/etl-ci.yml/badge.svg)](https://github.com/wesamabed/ClimateLens/actions/workflows/etl-ci.yml)
[![Node.js CI](https://github.com/wesamabed/ClimateLens/actions/workflows/node-ci.yml/badge.svg)](https://github.com/wesamabed/ClimateLens/actions/workflows/node-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# ClimateLens

**AI-powered Climate Data Explorer**: unifies **NOAA GSOD** historical weather, **World Bank CO₂ emissions**, and **IPCC AR6** report paragraphs—delivering instant, traceable answers via a semantic RAG API.

> “Growing up in Palestine, I’d watch the morning haze settle over my town and wonder: What’s really happening to our climate? Data lives in PDFs, CSVs, siloed APIs—making even simple questions take hours. ClimateLens turns that data into natural-language insight, instantly.”

---

## Table of Contents

1. [Features](#features)  
2. [Architecture](#architecture)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Configuration](#configuration)  
6. [Usage](#usage)  
7. [Deployment](#deployment)  
8. [CI / Tests](#ci--tests)  
9. [Contributing](#contributing)  
10. [License](#license)  
11. [Contact](#contact)  

---

## Features

- **Automated ETL** (Python): download, parse, transform, load, embed  
  - NOAA GSOD (daily weather since 1929)  
  - World Bank CO₂ emissions (yearly)  
  - IPCC AR6 SPM PDF → 250-word text chunks  
- **Semantic RAG API** (TypeScript/Express):  
  - `get_emissions`, `get_top_emitters`, `get_weather`, `get_report`, etc.  
  - Google Gemini (Vertex AI) function-calling  
  - Precise MongoDB queries or vector-similarity retrieval  
- **Search & Indexes** (MongoDB Atlas):  
  - B-tree, 2dsphere (geospatial), Atlas Search (text), Vector Search  
  - Synonym collection for typo/abbreviation resilience  
- **Frontend** (React/Vite):  
  - Natural-language chat UI calls `/api/ask`  
  - Displays answer + “Sources” panel linking to each record  
- **Performance & Traceability**:  
  - Sub-2 s responses, every fact back-linked to source  
  - Optional Redis caching via `REDIS_URL`

---

## Architecture

```
[ NOAA ]─GSOD→ [ Python ETL ] ──CSV→ Mongo Atlas ─┐
[ World Bank ]─JSON→                       ┌───┴───┐
[ IPCC PDF ]──PDF→ [ Chunk & Embed ] ─emb→│ Vector │
                                           └───┬───┘
                                           [ RAG API ]
                                           ┌──┴──┐
                                           │ UI  │
                                           └─────┘
```

---

## Prerequisites

- **Python** ≥ 3.9  
- **Node.js** ≥ 18 (LTS) & **npm**  
- **MongoDB Atlas** M10+ cluster with Search & Vector enabled  
- **Google Cloud** project:  
  - Vertex AI API  
  - Service account key JSON (`GOOGLE_APPLICATION_CREDENTIALS`)  
- (Optional) **Redis** for caching  

---

## Installation

### 1. Clone & Python Setup

```bash
git clone https://github.com/wesamabed/ClimateLens.git
cd ClimateLens
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r etl/requirements.txt
```

### 2. Node.js Monorepo Setup

```bash
npm install
# copy example envs
cp server/.env.example server/.env
cp client/.env.example client/.env
```

---

## Configuration

### `server/.env`

```ini
MONGODB_URI=...
DB_NAME=climate

# Vertex/Gemini
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
GOOGLE_CLOUD_PROJECT=climatelens-dev
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_EMBED_MODEL=gemini-embedding-001
VERTEX_LLM_MODEL=gemini-2.0-flash
GEMINI_API_KEY=          # if using direct API key

# ETL
CO2_START_YEAR=2019
CO2_END_YEAR=2019
IPCC_CHUNK_WORDS=250

# (Optional) caching
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600
```

### `client/.env.production`

```ini
VITE_API_BASE=https://climatelens-server-<id>.run.app
VITE_DEV_MODE=false
```

---

## Usage

### Run ETL

```bash
# Dry-run
python -m etl.main --start-year 2020 --end-year 2020 --dry-run

# Full ingest + embeddings + indexes
python -m etl.main --start-year 1929 --end-year 2023 --reindex
```

### Run Locally

```bash
npm run dev
# → API @ http://localhost:3000
# → UI @ http://localhost:8080
```

---

## Deployment

### Build & Push Docker

```bash
gcloud builds submit . \
  --region=us-central1 \
  --tag=us-central1-docker.pkg.dev/climatelens-dev/climatelens-server/server:latest
```

### Deploy Cloud Run

```bash
gcloud run deploy climatelens-server \
  --image=us-central1-docker.pkg.dev/climatelens-dev/climatelens-server/server:latest \
  --platform=managed --region=us-central1 \
  --allow-unauthenticated --port=3000 \
  --set-env-vars=$(paste -sd, server/.env | sed 's/^/ /')
```

### Host Frontend (Firebase)

```bash
cd client
npm run build
firebase deploy --only hosting
```

**Live Demo:**  
https://climatelens-dev.web.app  

---

## CI / Tests

- **ETL CI**: Ruff lint, MyPy, PyTest, 1-year dry-run  
- **Node CI**: ESLint, Jest unit tests (mocked GenAI/Mongo/fetch)  
- Workflows: `.github/workflows/etl-ci.yml`, `node-ci.yml`

---

## Contributing

1. Fork & branch  
2. Write code & tests  
3. Submit PR → CI green → review & merge  

---

## License

MIT © 2025 Wesam Abed

---

## Contact

**Wesam Abed**  
📧 wesamwaleed22@gmail.com  
🔗 [GitHub: wesamabed/ClimateLens](https://github.com/wesamabed/ClimateLens)  
🌐 Hosted App: [climatelens-dev.web.app](https://climatelens-dev.web.app)
