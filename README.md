
[![ETL CI](https://github.com/wesamabed/ClimateLens/actions/workflows/etl-ci.yml/badge.svg)](https://github.com/wesamabed/ClimateLens/actions/workflows/etl-ci.yml)
[![Node.js CI](https://github.com/wesamabed/ClimateLens/actions/workflows/node-ci.yml/badge.svg)](https://github.com/wesamabed/ClimateLens/actions/workflows/node-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# ClimateLens

**AI-powered Climate Data Explorer** combining a robust Python ETL pipeline, MongoDB Atlas Vector Search, and Google Vertex AI to turn NOAA’s Global Summary of the Day (GSOD) into interactive, AI-driven insights.

---

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [Configuration](#configuration)  
   1. [ETL (.env)](#etl-env)  
   2. [GSOD & CO₂ Settings](#gsod--co₂-settings)  
   3. [IPCC Report Settings](#ipcc-report-settings)  
   4. [Google Vertex AI](#google-vertex-ai)  
   5. [MongoDB Atlas & Vector Search](#mongodb-atlas--vector-search)  
6. [Repository Structure](#repository-structure)  
7. [CI / Tests](#ci--tests)  
8. [Contributing](#contributing)  
9. [License](#license)  
10. [Contact](#contact)  

---

## Features

- **Automated ETL**: Fetch, parse, convert, and load 90+ years of daily GSOD data  
- **CO₂ Emissions**: Pull total CO₂ emissions from World Bank API  
- **IPCC Report**: Download & chunk AR6 SPM PDF into ≤250‑word paragraphs  
- **Concurrent Processing**: Multi-threaded download, transform, load, embed  
- **Idempotent Runs**: Skip already-ingested years & paragraphs automatically  
- **Dry-Run Support**: Test pipeline without modifying the database  
- **AI-Driven Insights**: Integrates Google Vertex AI embeddings  
- **Vector Search**: Leverages MongoDB Atlas Vector Search for semantic retrieval  

---

## Prerequisites

- **Node.js** ≥ v18 & **npm**  
- **Python** ≥ 3.9  
- **MongoDB Atlas** cluster (M10+ with Search enabled)  
- **Google Cloud** project with Vertex AI and service account  

---

## Installation

### 1. Node.js Backend

```bash
cd server
npm install
cp .env.example .env    # fill in MONGODB_URI, PORT, etc.
npm run dev
```

### 2. Python ETL Pipeline

```bash
# From project root
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r etl/requirements.txt
```

---

## Usage

### Running the Backend

```bash
cd server
npm run dev
# API available at http://localhost:<PORT>
```

### Running the ETL

```bash
# Dry-run (download + transform only)
python -m etl.main \
  --start-year 2000 --end-year 2001 \
  --dry-run

# Full run (load + embed + index)
python -m etl.main \
  --start-year 1980 --end-year 2023 \
  --co2-start-year 2000 --co2-end-year 2023 \
  --uri "$MONGODB_URI" \
  --db-name "$DB_NAME" \
  --vertex-project "$VERTEX_PROJECT" \
  --vertex-region "$VERTEX_REGION" \
  --vertex-model "$VERTEX_MODEL" \
  --embed-batch-size 64 \
  --reindex \
  --log-level DEBUG
```

---

## Configuration

### ETL (.env)

Create a file `server/.env` (or export these env vars):

```ini
# Core
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net
DB_NAME=climate
DATA_DIR=data/gsod

# GSOD → NOAA archive
DOWNLOAD_BASE_URL=https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive
DOWNLOAD_RETRY_ATTEMPTS=3
DOWNLOAD_RETRY_WAIT=5
DOWNLOAD_MAX_WORKERS=4

# CO₂ emissions → World Bank
CO2_INDICATOR=EN.GHG.CO2.MT.CE.AR5
CO2_START_YEAR=1929
CO2_END_YEAR=2023

# IPCC Report
IPCC_PDF_URL=https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf
IPCC_PDF_NAME=IPCC_AR6_WGI_SPM.pdf
IPCC_CHUNK_WORDS=250
DATA_DIR_IPCC=data/ipcc

# Vertex AI embeddings
VERTEX_PROJECT=your-gcp-project-id
VERTEX_REGION=us-central1
VERTEX_MODEL=textembedding-gecko@latest
EMBED_BATCH_SIZE=64
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json

# MongoDB Atlas Vector Search
ATLAS_PROJECT_ID=<atlas-project-id>
ATLAS_CLUSTER=<atlas-cluster-name>
ATLAS_PUBLIC_KEY=<atlas-api-public-key>
ATLAS_PRIVATE_KEY=<atlas-api-private-key>
```

#### GSOD & CO₂ Settings

- `START_YEAR` / `END_YEAR`: range of GSOD years  
- `CO2_START_YEAR` / `CO2_END_YEAR`: range of CO₂ years  

#### IPCC Report Settings

- `IPCC_PDF_URL`: download URL  
- `IPCC_PDF_NAME`: stored filename  
- `IPCC_CHUNK_WORDS`: max words per text chunk  

#### Google Vertex AI

1. Enable Vertex AI API in your GCP project.  
2. Create a service account with roles:  
   - Vertex AI User  
   - AI Platform Admin  
3. Download the JSON key and set  
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```  
4. Set `VERTEX_PROJECT`, `VERTEX_REGION`, `VERTEX_MODEL`, `EMBED_BATCH_SIZE`.  

#### MongoDB Atlas & Vector Search

1. Provision an **M10+** cluster with **Search Nodes** enabled.  
2. Obtain API keys: Project Owner role.  
3. In Atlas UI → Access Manager → API Keys → Create.  
4. Add `ATLAS_PROJECT_ID`, `ATLAS_CLUSTER`, `ATLAS_PUBLIC_KEY`, `ATLAS_PRIVATE_KEY`.  
5. Run ETL with `--reindex` to auto-create the vector index.  

---

## Repository Structure

```bash
.
├── .github/
│   ├── etl-ci.yml
│   └── node-ci.yml
├── server/             # Node.js backend
├── client/             # React frontend
├── etl/                # Python ETL
│   ├── config.py
│   ├── main.py
│   ├── downloader/
│   ├── transformer/
│   ├── loader/
│   ├── pipeline/
│   ├── embed/
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## CI / Tests

- **Lint & Type-Check**: `ruff check etl`  
- **Unit Tests**: `pytest etl/tests`  
- **ETL Smoke**: dry-run via GitHub Actions on push/pr  

---

## Contributing

1. Fork & branch  
2. Write tests & code  
3. PR → CI green → Review → Merge  

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

**Wesam Abed** – [wesamwaleed22@gmail.com](mailto:wesamwaleed22@gmail.com)  
GitHub: [wesamabed/ClimateLens](https://github.com/wesamabed/ClimateLens)
