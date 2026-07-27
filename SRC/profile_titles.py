from pathlib import Path

import pandas as pd

# path to the root of the repository
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_FOLDER = PROJECT_ROOT / "CSV files"

OUTPUT_FOLDER = PROJECT_ROOT / "output"
QUARANTINED_FOLDER = OUTPUT_FOLDER / "quarantined"
VALID_FOLDER = OUTPUT_FOLDER / "valid"

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

def clean_text_column(
        dataframe: pd.DataFrame,
        column_name: str,
) -> pd.DataFrame:
    """Safely clean whitespace in one text column."""

    cleaned_dataframe = dataframe.copy()
        
    cleaned_dataframe[column_name] = (
         cleaned_dataframe[column_name]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        )
    return cleaned_dataframe

def save_valid_rows(
        dataframe: pd.DataFrame,
        filename: str,
) -> None:
    """Save valid cleaned rows to the valid output folder."""

    output_path = VALID_FOLDER / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print("\nSaved valid rows to:")
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

def inspect_join_columns(
        top_anime: pd.DataFrame,
        watched_anime: pd.DataFrame,
        manga: pd.DataFrame,
) -> None:
    """Inspect possible title columns before attempting merges."""

    print("\nPotential join columns")
    print("======================")

    print("\nTop 1000 Anime columns:")
    print(top_anime.columns.tolist())

    print("\nMost Watched Anime columns:")
    print(watched_anime.columns.tolist())

    print("\nBest-Selling Manga columns:")
    print(manga.columns.tolist())

    print("\nSample Top 1000 Anime titles:")
    print(top_anime["anime_name"].head(10).to_string(index=False))

    print("\nSample Most Watched Anime titles:")
    print(watched_anime["Anime Name"].head(10).to_string(index=False))

    print("\nSample Best-Selling Manga titles:")
    print(manga["Manga series"].head(10).to_string(index=False))

def create_title_key(
        dataframe: pd.DataFrame,
        source_column: str,
        key_column: str = "title_key",
) -> pd.DataFrame:
    """Create a normalized technical key for exact title matching."""

    keyed_dataframe = dataframe.copy()

    keyed_dataframe[key_column] = (
        keyed_dataframe[source_column]
        .str.lower()
        .str.strip()
        .str.replace(r"[^a-z0-9\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return keyed_dataframe

def inspect_match_coverage(
        top_anime: pd.DataFrame,
        watched_anime: pd.DataFrame,
        manga: pd.DataFrame,
) -> None:
    """Measure exact title overlap and duplicate join keys."""

    top_keys = set(top_anime["title_key"])
    watched_keys = set(watched_anime["title_key"])
    manga_keys = set(manga["title_key"])

    top_watched_matches = top_keys.intersection(watched_keys)
    top_manga_matches = top_keys.intersection(manga_keys)

    print("\nExact-match coverage")
    print("====================")

    print(
        "\nUnique Top Anime titles:",
        top_anime["title_key"].nunique(),
    )
    print(
        "Unique Watched Anime titles:",
        watched_anime["title_key"].nunique(),
    )
    print(
        "Unique Manga titles:",
        manga["title_key"].nunique(),
    )

    print(
        "\nExact matches between Top Anime and Watched Anime:",
        len(top_watched_matches),
    )
    print(
        "Exact matches between Top Anime and Manga:",
        len(top_manga_matches),
    )

    print("\nDuplicate title keys:")
    print(
        "Top Anime:",
        top_anime["title_key"].duplicated().sum(),
    )
    print(
        "Watched Anime:",
        watched_anime["title_key"].duplicated().sum(),
    )
    print(
        "Manga:",
        manga["title_key"].duplicated().sum(),
    )

    print("\nSample Top Anime ↔ Watched Anime matches:")
    print(sorted(top_watched_matches)[:20])

    print("\nSample Top Anime ↔ Manga matches:")
    print(sorted(top_manga_matches)[:20])

def inspect_duplicate_title_keys(
        dataframe: pd.DataFrame,
        name: str,
        title_column: str,
) -> None:
    """Display rows whose normalized title key appears more than once."""

    duplicate_mask = dataframe["title_key"].duplicated(keep=False)

    duplicate_rows = (
        dataframe[duplicate_mask]
        .sort_values(["title_key"])
    )

    print(f"\nDuplicate-key investigation: {name}")
    print("=" * (29 + len(name)))

    print(
        f"Rows involved in duplicate keys: "
        f"{len(duplicate_rows)}"
    )

    print(
        f"Distinct duplicated keys: "
        f"{duplicate_rows['title_key'].nunique()}"
    )

    print(
        duplicate_rows[
            [
                title_column,
                "title_key",
                "Most Watched in Country",
                "Ratings",
                "Number of Episodes",
                "Release Year",
            ]
        ].to_string(index=False)
    )

def check_watched_anime_semantics(
        dataframe: pd.DataFrame,
) -> None:
    """Flag suspicious values in the watched-anime dataset."""

    suspicious_release_years = dataframe[
        (dataframe["Release Year"] < 1960)
        | (dataframe["Release Year"] > 2026)
    ]

    suspicious_episode_counts = dataframe[
        dataframe["Number of Episodes"] > 150
    ]

    suspicious_durations = dataframe[
        dataframe["Duration per Episode (minutes)"] > 90
    ]

    print("\nSemantic validation: Most Watched Anime")
    print("========================================")

    print(
        f"Rows with suspicious release years: "
        f"{len(suspicious_release_years)}"
    )

    print(
        f"Rows with unusually high episode counts: "
        f"{len(suspicious_episode_counts)}"
    )

    print(
        f"Rows with unusually long episode durations: "
        f"{len(suspicious_durations)}"
    )

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

#--------------------------------------------------
#TOP 1000 Anime
#---------------------------------------------------
    
    valid_top_anime, quarantined_top_anime = (
        separate_valid_and_quarantined_rows(
            top_anime,
            ["anime_id", "anime_name"],
        )
    )

    cleaned_top_anime = clean_text_column(
        valid_top_anime,
        "anime_name",
    )

    print("\nSeparation results: Top 1000 Anime")
    print("----------------------------------")
    print(f"Valid rows: {len(valid_top_anime)}")
    print(f"Quarantined rows: {len(quarantined_top_anime)}")

    save_valid_rows(
        cleaned_top_anime,
        "top_1000_anime_cleaned.csv",
    )

    save_quarantined_row(
        quarantined_top_anime,
        "top_1000_anime_missing_required.csv",
    )


    # --------------------------------------------------
    # Most Watched Anime
    # --------------------------------------------------

    valid_watched_anime, quarantined_watched_anime = (
        separate_valid_and_quarantined_rows(
            watched_anime,
            ["Anime Name"],
        )
    )

    cleaned_watched_anime = clean_text_column(
        valid_watched_anime,
        "Anime Name",
    )

    print("\nSeparation results: Most Watched Anime")
    print("--------------------------------------")
    print(f"Valid rows: {len(valid_watched_anime)}")
    print(f"Quarantined rows: {len(quarantined_watched_anime)}")

    save_valid_rows(
        cleaned_watched_anime,
        "most_watched_anime_cleaned.csv",
    )

    save_quarantined_row(
        quarantined_watched_anime,
        "most_watched_missing_titles.csv",
    )


    # --------------------------------------------------
    # Best-Selling Manga
    # --------------------------------------------------

    valid_manga, quarantined_manga = (
        separate_valid_and_quarantined_rows(
            manga,
            ["Manga series"],
        )
    )

    cleaned_manga = clean_text_column(
        valid_manga,
        "Manga series",
    )

    print("\nSeparation results: Best-Selling Manga")
    print("--------------------------------------")
    print(f"Valid rows: {len(valid_manga)}")
    print(f"Quarantined rows: {len(quarantined_manga)}")

    save_valid_rows(
        cleaned_manga,
        "best_selling_manga_cleaned.csv",
    )

    save_quarantined_row(
        quarantined_manga,
        "best_selling_manga_missing_titles.csv",
    )
    keyed_top_anime = create_title_key(
        cleaned_top_anime,
        "anime_name",
    )

    keyed_watched_anime = create_title_key(
        cleaned_watched_anime,
        "Anime Name",
    )

    keyed_manga = create_title_key(
        cleaned_manga,
        "Manga series",
    )

    inspect_join_columns(
        keyed_top_anime,
        keyed_watched_anime,
        keyed_manga,
    )

    print("\nSample Top Anime title keys:")
    print(
        keyed_top_anime[
            ["anime_name", "title_key"]
        ].head(10).to_string(index=False)
    )

    print("\nSample Watched Anime title keys:")
    print(
        keyed_watched_anime[
            ["Anime Name", "title_key"]
        ].head(10).to_string(index=False)
    )

    print("\nSample Manga title keys:")
    print(
        keyed_manga[
            ["Manga series", "title_key"]
        ].head(10).to_string(index=False)
    )

    inspect_match_coverage(
        keyed_top_anime,
        keyed_watched_anime,
        keyed_manga,
    )

    inspect_duplicate_title_keys(
        keyed_watched_anime,
        "Most Watched Anime",
        "Anime Name",
    )

    check_watched_anime_semantics(
        keyed_watched_anime,
    )

if __name__ == "__main__":
    main()   