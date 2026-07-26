from pathlib import Path

import pandas as pd

# path to the root of the repository
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_FOLDER = PROJECT_ROOT / "CSV files"

OUTPUT_FOLDER = PROJECT_ROOT / "output"
QUARANTINED_FOLDER = OUTPUT_FOLDER / "quarantined"


TOP_ANIME_FILE = CSV_FOLDER / "top_1000_animes.csv"
WATCHED_ANIME_FILE = CSV_FOLDER / "most_watched_anime_dataset_100_entries.csv"
MANGA_FILE = CSV_FOLDER / "best-selling-manga.csv"


def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """load the three raw csv datasets."""

    top_anime = pd.read_csv(TOP_ANIME_FILE)
    watched_anime = pd.read_csv(WATCHED_ANIME_FILE)
    manga = pd.read_csv(MANGA_FILE)


    return top_anime, watched_anime, manga

def print_profile(name:str, dataframe:pd.DataFrame) -> None:
    """Print basic profiling information for one dataset."""
        
    print(f"\n{name}")
    print("-" * len(name))
    print(f"Rows: {len(dataframe):,}")
    print(f"columns: {len(dataframe.columns)}")
    print(f"duplicate rows: {dataframe.duplicated().sum()}")

    print("\nMissing values:")
    print(dataframe.isna().sum())

def investigate_missing_values(
        name: str,
        dataframe: pd.DataFrame
)-> None:
    """Investigate missing-value patterns in dataset"""

    rows_with_missing = dataframe[dataframe.isna().any(axis=1)]
    completely_blank_rows = dataframe[dataframe.isna().all(axis=1)]

    print(f"\nMissing-value investigation: {name}")
    print("-" * (29 + len(name)))
    print(f"Rows containing at least one missing value: {len(rows_with_missing)}")
    print(f"completely blank rows: {len(completely_blank_rows)}")

    if rows_with_missing.empty:
        print("No missing values found.")
    else: 
        print("\nRows with missing values:")
        print(rows_with_missing)      

def check_required_fields(
        name: str,
        dataframe: pd.DataFrame,
        required_columns: list[str],
) -> None:
    """Check whether required columns exist and contain missing values."""

    print(f"\nRequired-field check: {name}")
    print("-" * (22 + len(name)))

    missing_columns = [
        column 
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return

    invalid_rows = dataframe[dataframe[required_columns].isna().any(axis=1)]

    print(f"Rows missing required values: {len(invalid_rows)}")

    if invalid_rows.empty:
        print("All required fields are populated")
    else:
        print("\nRows that should be quarantined:")
        print(invalid_rows)

def separate_valid_and_quarantined_rows(
        dataframe: pd.DataFrame,
        required_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Seperate valid rows from rows missing required values"""

    quarantine_mask = dataframe[required_columns].isna().any(axis=1)

    quarantined_rows = dataframe[quarantine_mask]
    valid_rows = dataframe[~quarantine_mask]
    return valid_rows, quarantined_rows

def save_quarantined_row(
        dataframe:pd.DataFrame,
        filename:str,
) -> None:
    """Save quarantined rows to the quarantined output folder."""

    output_path = QUARANTINED_FOLDER / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print("\nSaved quarantined rows to:")
    print(output_path)

def validate_everything(
        name: str,
        dataframe: pd.DataFrame,
        required_columns: list[str],
)-> None:
    """Run all current data-quality checks for one dataset"""

    print(f"\nValidation report: {name}")
    print("=" * (19 + len(name)))

    print_profile(name, dataframe)
    investigate_missing_values(name, dataframe)
    check_required_fields(name, dataframe, required_columns)

def main() -> None:
    top_anime, watched_anime, manga = load_datasets()

    validate_everything(
        "Top 1000 Anime",
        top_anime,
        ["anime_id", "anime_name"],
    )

    validate_everything(
        "Most Watched Anime",
        watched_anime,
        ["Anime Name"],
    )

    validate_everything(
        "Best-Selling Manga",
        manga,
        ["Manga series"],
    )

    valid_watched_anime, quarantined_watched_anime = (
        separate_valid_and_quarantined_rows(
            watched_anime,
            ["Anime Name"],
        )
    )

    print("\nSeparation results: Most Watched Anime")
    print("--------------------------------------")
    print(f"Valid rows: {len(valid_watched_anime)}")
    print(f"Quarantined rows: {len(quarantined_watched_anime)}")

    save_quarantined_row(
        quarantined_watched_anime,
        "most_watched_missing_titles.csv",
    )
if __name__ == "__main__":
    main()   