# Anime & Manga Analytics Pipeline

A project-based data engineering pipeline built with Python to ingest, profile,
validate, clean, quarantine, normalize, and prepare multiple anime and manga
datasets for downstream analysis.

## Project Goals

- Build a reusable CSV ingestion and validation workflow
- Identify missing, duplicate, and semantically inconsistent records
- Quarantine invalid rows without losing source data
- Normalize title fields for cross-dataset matching
- Prepare cleaned datasets for integration and analysis

## Pipeline

Raw CSVs  
↓  
Load  
↓  
Profile  
↓  
Validate  
↓  
Separate valid and quarantined rows  
↓  
Clean text fields  
↓  
Create normalized title keys  
↓  
Measure match coverage  
↓  
Prepare for aggregation and merging  

## Data Quality Assessment

During exploratory profiling and validation, the **Most Watched Anime**
dataset passed structural validation but exhibited several semantic
inconsistencies.

### Structural Validation Results

- Required fields were identified and validated.
- Records with missing required titles were quarantined.
- Duplicate title keys were detected and investigated.
- Title normalization was performed to support dataset joins.

### Semantic Observations

Several records contained values that conflicted with the known properties of
the referenced anime, including:

- Release years that did not align with the title
- Episode counts that varied dramatically for the same anime
- Repeated titles with conflicting metadata

These observations suggest that the dataset is likely synthetic or generated
for demonstration purposes rather than representing authoritative production
data.

### Project Decision

Because the primary objective of this project is to demonstrate the design of a
data engineering pipeline—including ingestion, profiling, validation,
cleansing, quarantine workflows, normalization, and dataset integration—the
dataset was retained.

The limitation is documented so readers can evaluate the engineering workflow
without interpreting the final analytical results as authoritative.
