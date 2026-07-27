# Media Metadata ETL Pipeline
#Data Quality Assessment

During exploratory data profiling and validation, the Most Watched Anime dataset passed structural validation but exhibited several semantic inconsistencies during quality assessment.

Structural validation results
Required fields were identified and validated.
Records with missing required titles were quarantined.
Duplicate title keys were detected and investigated.
Title normalization was performed to support dataset joins.
Semantic observations

While investigating duplicate titles, several records contained values that were inconsistent with the known properties of the referenced anime. Examples included:

Release years that did not align with the anime's actual release date.
Episode counts that varied dramatically for the same title.
Repeated titles with conflicting metadata.

These observations suggest that the dataset is likely synthetic or generated for demonstration purposes rather than representing authoritative production data.

Project decision

Because the primary objective of this project is to demonstrate the design of a data engineering pipeline—including ingestion, profiling, validation, cleansing, quarantine workflows, normalization, and dataset integration—the dataset was retained for the remainder of the project.

This decision is documented so that future readers understand the limitations of the source data while still being able to evaluate the engineering techniques demonstrated throughout the project.
