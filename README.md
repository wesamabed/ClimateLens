# ClimateLens

[![CI](/.github/workflows/etl-ci.yml/badge.svg)](https://github.com/your-org/ClimateLens/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **AI-powered Climate Data Explorer**  
> Combines Google Vertex AI, MongoDB Atlas Vector Search, and a robust Python ETL pipeline  
> to turn NOAA’s Global Summary of the Day (GSOD) into interactive, AI-driven insights.

---

## 📖 Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Repository Structure](#repository-structure)  
5. [Prerequisites](#prerequisites)  
6. [Setup & Installation](#setup--installation)  
   - [Node.js Backend](#nodejs-backend)  
   - [Python ETL Pipeline](#python-etl-pipeline)  
7. [Usage](#usage)  
   - [Running the Backend](#running-the-backend)  
   - [Running the ETL](#running-the-etl)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## 🧐 Overview

**ClimateLens** is an end-to-end solution for exploring global climate data:

- **Data**: Ingest NOAA GSOD (Global Summary of the Day) archives  
- **Storage**: MongoDB Atlas with Vector Search for fast retrieval  
- **AI**: Google Vertex AI for natural-language queries & insights  
- **Frontend**: React client (separate repo)  
- **Backend**: Node.js API (separate repo)  
- **ETL**: Python scripts to download, transform, and load GSOD into MongoDB  

This repo houses the **Python ETL** and project-wide CI/CD & docs.

---

## 🚀 Features

- **Automated ETL**: Fetch, parse, convert, and load 90+ years of daily weather data  
- **Unit conversion**: Fahrenheit → Celsius, inches → mm, knots → m/s, etc.  
- **Concurrent processing**: Multi-threaded download, transform, and load for speed  
- **Idempotent runs**: Skip already-ingested years automatically  
- **Dry-run support**: Test your pipeline without touching the database  
- **Production-grade**: Pydantic validation, retry logic, batch loading, robust logging  

---

## 🛠️ Tech Stack

| Layer         | Technology                                          |
| ------------- | --------------------------------------------------- |
| **ETL**       | Python 3.9, Pydantic, Tenacity, concurrent.futures |
| **Database**  | MongoDB Atlas (Vector Search + standard indexes)    |
| **AI/ML**     | Google Vertex AI                                    |
| **Backend**   | Node.js, TypeScript, Express                        |
| **Frontend**  | React                                               |
| **CI/CD**     | GitHub Actions, ESLint, Ruff                        |

---

## 📂 Repository Structure

``` text
.
├── .github/               # CI & GitHub Actions workflows
│   └── etl-ci.yml         # Lint, test, dry-run ETL
├── server/                # Node.js backend (separate TS repo)
├── client/                # React frontend (separate repo)
├── etl/                   # Python ETL pipeline
│   ├── config.py          # Pydantic settings loader
│   ├── logger.py          # Structured logging setup
│   ├── downloader/        # FTPDownloader & TarExtractor
│   ├── transformer/       # Parser, converters, Pydantic models
│   ├── loader/            # BatchLoader, preparer, MongoRepository
│   ├── pipeline/          # Step abstractions & orchestration
│   ├── main.py            # CLI entry point
│   └── requirements.txt   # Python dependencies
├── .gitignore             # Excludes local, build, data, caches
└── README.md              # This file
```
---
## 🔧 Prerequisites

Node.js ≥ v18 & npm (for backend)

Python ≥ 3.11 (for ETL)

MongoDB Atlas cluster & connection URI

Tip: you can store your ETL settings (e.g. `MONGODB_URI`, `DB_NAME`) in `server/.env`, or simply pass them via CLI flags.

🏗️ Setup & Installation

1. **Node.js Backend**  
    cd server  
    npm install  
    cp .env.example .env      # fill in MONGODB_URI, PORT, etc.  
    npm run dev  

2. **Python ETL Pipeline**  
    # From project root  
    python3 -m venv .venv  
    source .venv/bin/activate  
    pip install --upgrade pip  
    pip install -r etl/requirements.txt  

Ensure your Mongo URI & settings live in `server/.env` or pass via CLI.

🎬 Usage

- **Running the Backend**  
    cd server  
    npm run dev  
    # API available at http://localhost:<PORT>  

- **Running the ETL**  
    # Dry-run (download + transform only)  
    python -m etl.main \
      --start-year 2000 \
      --end-year   2001 \
      --dry-run  

    # Full run (load into MongoDB)  
    python -m etl.main \
      --start-year 1980 \
      --end-year   2023 \
      --uri        "$MONGODB_URI" \
      --db-name    "$DB_NAME" \
      --log-level  DEBUG  

The pipeline will:  
- Skip any year already ingested  
- Download `.tar` archives via FTP  
- Extract daily `.op.gz` files  
- Transform to JSON with unit conversions & validation  
- Load into MongoDB in concurrent batches  

🤝 Contributing

1. Open an issue to discuss your idea  
2. Fork this repo & create a feature branch  
3. Write clear, test-covered code  
4. Submit a pull request against `main`  
5. Make sure CI (lint, tests, dry-run) passes  

📜 License

This project is licensed under the MIT License.  
Feel free to use, modify, and distribute!

---
