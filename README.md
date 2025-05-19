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
6. [Repository Structure](#repository-structure)  
7. [Contributing](#contributing)  
8. [License](#license)  
9. [Contact](#contact)  

---

## Features

- **Automated ETL**: Fetch, parse, convert, and load 90+ years of daily GSOD data  
- **Unit Conversion**: Fahrenheit → Celsius, inches → mm, knots → m/s, etc.  
- **Concurrent Processing**: Multi-threaded download, transform, and load for speed  
- **Idempotent Runs**: Skip already-ingested years automatically  
- **Dry-Run Support**: Test pipeline without modifying the database  
- **Production-Grade**: Pydantic validation, retry logic, batch loading, structured logging  
- **AI-Driven Insights**: Integrates Google Vertex AI for natural-language queries  
- **Vector Search**: Leverages MongoDB Atlas Vector Search for fast retrieval  

---

## Prerequisites

- **Node.js** ≥ v18 & **npm**  
- **Python** ≥ 3.9  
- **MongoDB Atlas** cluster & connection URI  

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
python -m etl.main   --start-year 2000   --end-year   2001   --dry-run

# Full run (load into MongoDB)
python -m etl.main   --start-year 1980   --end-year   2023   --uri        "$MONGODB_URI"   --db-name    "$DB_NAME"   --log-level  DEBUG
```

---

## Configuration

Create a `.env` file in the `server/` directory or export environment variables:

```env
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net
DB_NAME=climatelens
PORT=3000
```

---

## Repository Structure

```bash
.
├── .github/            # GitHub Actions workflows (CI: lint, test, dry-run ETL)
│   └── etl-ci.yml      # ETL pipeline CI configuration
├── server/             # Node.js backend (TypeScript)
├── client/             # React frontend application
├── etl/                # Python ETL pipeline
│   ├── config.py       # Pydantic settings loader
│   ├── logger.py       # Structured logging setup
│   ├── downloader/     # FTP downloader & tarball extractor
│   ├── transformer/    # Parsers, converters, Pydantic models
│   ├── loader/         # Batch loader, preparer, MongoDB repository
│   ├── pipeline/       # Pipeline orchestration & step abstractions
│   ├── main.py         # CLI entry point
│   └── requirements.txt# Python dependencies
├── .gitignore          # Ignore local files, builds, data, caches
└── README.md           # Project documentation and overview
```

---

## Contributing

1. **Fork** the repository  
2. **Create** a feature branch (`git checkout -b feature/awesome`)  
3. **Write** clear, test-covered code following the existing style  
4. **Push** to your branch (`git push origin feature/awesome`)  
5. **Open** a Pull Request against `main` and ensure CI passes  

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

**Wesam Abed** – [wesamwaleed22@gmail.com](mailto:wesamwaleed22@gmail.com)  
GitHub: [your-org/ClimateLens](https://github.com/your-org/ClimateLens)  
