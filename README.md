# Anime & Manga Analytics Pipeline

> A project-based data engineering pipeline demonstrating data ingestion, profiling, validation, cleansing, quarantine workflows, normalization, and dataset integration using Python.

---

## Overview

This project simulates the early stages of a real-world data engineering workflow.

Rather than focusing solely on analysis, the project emphasizes the engineering processes required before reliable analytics can occur. Multiple anime and manga datasets are ingested, profiled, validated, cleaned, normalized, and prepared for downstream integration.

The goal is to demonstrate practical ETL concepts and data quality assessment using Python while documenting engineering decisions throughout the development process.

---

## Project Goals

This project was designed to demonstrate the following engineering concepts:

- Build a reusable CSV ingestion pipeline
- Profile incoming datasets
- Validate required fields
- Quarantine invalid records
- Normalize text for reliable joins
- Measure dataset compatibility
- Assess structural and semantic data quality
- Document engineering decisions and tradeoffs
- Prepare datasets for downstream analytics

---

## Dataset Overview

| Dataset | Purpose |
|---------|----------|
| Top 1000 Anime | Primary anime metadata |
| Most Watched Anime | Regional popularity data |
| Best Selling Manga | Manga sales information |

---

# Pipeline Architecture

```text
                Raw CSV Files
                      │
                      ▼
             Load Into Pandas
                      │
                      ▼
              Data Profiling
                      │
                      ▼
         Required Field Validation
                      │
                      ▼
      Separate Valid / Invalid Rows
              │                 │
              ▼                 ▼
        Valid Records     Quarantined Records
              │
              ▼
        Text Normalization
              │
              ▼
      Create Normalized Keys
              │
              ▼
     Match Coverage Analysis
              │
              ▼
      Dataset Integration Prep
```

---

# Repository Structure

```text
Anime-Manga-Analytics-Pipeline
│
├── CSV files/
│   ├── top_1000_animes.csv
│   ├── most_watched_anime.csv
│   └── best_selling_manga.csv
│
├── output/
│   ├── valid/
│   └── quarantined/
│
├── src/
│   └── profile_titles.py
│
├── README.md
└── requirements.txt
```

---

# Features

Current pipeline capabilities include:

- Dataset profiling
- Missing value investigation
- Required-field validation
- Invalid row quarantine
- Duplicate key investigation
- Text normalization
- Join key creation
- Dataset compatibility analysis
- Exact match coverage reporting
- Semantic data quality assessment

---

# Data Quality Assessment

One objective of this project is demonstrating that successful ETL pipelines require more than simply loading data.

## Structural Validation

The pipeline automatically validates:

- Required fields
- Missing values
- Duplicate records
- Duplicate title keys
- Join compatibility
- Dataset completeness

Rows missing required identifiers are automatically quarantined rather than discarded.

---

## Semantic Validation

While investigating duplicate title keys, the **Most Watched Anime** dataset exhibited several semantic inconsistencies.

Examples included:

- Release years inconsistent with known anime
- Highly variable episode counts for identical titles
- Conflicting metadata across duplicate records

Although these records passed structural validation, they failed semantic quality review.

---

## Engineering Decision

Rather than replacing the dataset, it was intentionally retained.

The objective of this repository is to demonstrate engineering workflows—not produce authoritative anime statistics.

Documenting the limitation illustrates an important engineering principle:

> Data can be structurally valid while still being semantically unreliable.

This mirrors real-world engineering work, where imperfect data sources are common and must be documented rather than ignored.

---

# Current Results

Current pipeline outputs include:

✔ Dataset profiling

✔ Missing value reports

✔ Validation summaries

✔ Quarantined records

✔ Cleaned datasets

✔ Normalized title keys

✔ Match coverage analysis

✔ Duplicate key investigation

✔ Semantic quality assessment

---

# Technologies Used

- Python
- Pandas
- Git
- GitHub
- CSV Processing
- ETL Concepts
- Data Validation
- Data Cleaning

---

# Skills Demonstrated

This project demonstrates experience with:

- ETL pipeline design
- Data profiling
- Data validation
- Data quality assessment
- Data cleansing
- Quarantine workflows
- Text normalization
- Dataset integration
- Pipeline documentation
- Git version control

---

# Future Improvements

Planned enhancements include:

- PostgreSQL integration
- SQLAlchemy data loading
- Dockerized environment
- Logging framework
- Automated testing
- Configuration files
- HTML data quality reports
- Pipeline scheduling
- CI/CD with GitHub Actions

---

# Lessons Learned

One of the biggest takeaways from this project is that data quality extends beyond missing values and duplicate records.

Through exploratory validation, the project demonstrates the importance of distinguishing between:

- Structural validity
- Semantic validity

Understanding this distinction is critical when designing reliable data engineering pipelines.

---

# About This Project

This repository is part of my transition from **Healthcare Data Analyst** to **Analytics Engineer / Data Engineer**.

The focus is intentionally on learning engineering principles through project-based development while documenting decisions, tradeoffs, and iterative improvements along the way.
