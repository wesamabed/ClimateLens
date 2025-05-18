ClimateLens

AI-powered climate data explorer using MongoDB Atlas Vector Search + Google Vertex AI

Table of Contents

Project Overview

Features

Tech Stack

Repository Structure

Setup & Installation

Prerequisites

Node.js Application

Python ETL Pipeline

Usage

Running the Node App

Running the ETL Pipeline

Contributing

License

Project Overview

ClimateLens is an AI-powered climate data explorer that combines:

Google Vertex AI for advanced machine learning and large language model integrations.

MongoDB Atlas Vector Search to efficiently store, index, and query climate data.

A Python ETL pipeline to ingest NOAA's Global Summary of the Day (GSOD) data into MongoDB.

This repository contains both the backend Node.js application and the ETL scripts required to fetch, transform, and load climate data.

Features

Full-text & vector search over climate datasets.

AI-driven insights using pre-trained models on Google Cloud.

Automated ETL pipeline for daily weather summaries (1980-present).

Scalable architecture suitable for production and experimentation.

Tech Stack

Backend: Node.js, TypeScript, Express

Database: MongoDB Atlas Vector Search

Cloud AI: Google Vertex AI

ETL Pipeline: Python, Pandas, Pydantic, Typer

CI/CD: GitHub Actions, ESLint, Ruff

Repository Structure

.
├── server/                  # Node.js application
│   ├── .env                 # Environment variables for backend
│   ├── src/                 # TypeScript source code
│   ├── tsconfig.json
│   └── package.json
├── etl/                     # Python ETL scripts
│   ├── config.py            # Configuration loader (Pydantic)
│   ├── logger.py            # Logging adapter
│   ├── pipeline/            # ETL pipeline steps (download, transform, load)
│   ├── main.py              # CLI entry-point for ETL
│   └── requirements.txt
├── .github/workflows/       # CI configurations
├── .gitignore
└── README.md

Setup & Installation

Prerequisites

Node.js v18+ & npm

Python 3.11+

MongoDB Atlas cluster (connection URI)

Node.js Application

Install dependencies

cd server
npm install

Configure environment

Copy .env.example to .env in server/

Set MONGODB_URI, DB_NAME, PORT, etc.

Run the server

npm run dev

Python ETL Pipeline

Create virtual environment (at repo root):

python3 -m venv .venv
source .venv/bin/activate

Install ETL dependencies

pip install -r etl/requirements.txt

Configure ETL

Ensure server/.env contains your MONGODB_URI and settings.

Usage

Running the Node App

cd server
npm run dev
# Access at http://localhost:<PORT>

Running the ETL Pipeline

From the repo root:

# Dry-run (no DB writes)
python -m etl.main --dry-run

# Dry-run with explicit URI
python -m etl.main --dry-run --uri mongodb://dry-run

# Full run (uses server/.env URI)
python -m etl.main

Contributing

Contributions are welcome! Please:

Open an issue to discuss your idea.

Fork the repo and create a branch (feature/...).

Commit with clear messages and PR against main.

Ensure CI passes (lint, type-checks, ETL smoke test).

## Python ETL Pipeline

Under `etl/` you’ll find a configurable, production-grade ETL that:

1. **Downloads** NOAA GSOD `.tar` archives via FTP  
2. **Extracts** the daily `.op.gz` files  
3. **Transforms** them into clean JSON documents using Pydantic + unit-conversion  
4. **Loads** them in batches into MongoDB

### Prerequisites

- Python 3.9+  
- A MongoDB URI in `server/.env` (or pass `--uri` on the CLI)

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r etl/requirements.txt


# Dry-run (download & transform only):
python -m etl.main \
  --start-year 2000 \
  --end-year   2001 \
  --dry-run

# Full run (load into MongoDB):
python -m etl.main \
  --start-year 2010 \
  --end-year   2015 \
  --uri        "$MONGODB_URI" \
  --log-level  DEBUG


etl/
├── config.py        # Pydantic settings loader
├── logger.py        # Standardized logger factory
├── downloader/      # FTPDownloader + TarExtractor
├── transformer/     # Fixed‐width parser → Pydantic models
├── loader/          # BatchLoader → MongoRepository
├── pipeline/        # Orchestrates Download → Transform → Load
├── main.py          # CLI entry point
└── requirements.txt




License

MIT

