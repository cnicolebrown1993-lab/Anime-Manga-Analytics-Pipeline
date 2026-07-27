from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

# Path to the root of the repository.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_FOLDER = PROJECT_ROOT / "CSV files"

OUTPUT_FOLDER = PROJECT_ROOT / "output"
QUARANTINED_FOLDER = OUTPUT_FOLDER / "quarantined"
VALID_FOLDER = OUTPUT_FOLDER / "valid"

TOP_ANIME_FILE = CSV_FOLDER / "top_1000_animes.csv"
WATCHED_ANIME_FILE = (
    CSV_FOLDER / "most_watched_anime_dataset_100_entries.csv"
)
MANGA_FILE = CSV_FOLDER / "best-selling-manga.csv"


# --------------------------------------------------
# File and directory setup
# --------------------------------------------------

def create_output_directories() -> None:
    """Create pipeline output directories if they do not exist."""

    VALID_FOLDER.mkdir(parents=True, exist_ok=True)
    QUARANTINED_FOLDER.mkdir(parents=True, exist_ok=True)


def load_datasets() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load the three raw CSV datasets."""

    top_anime = pd.read_csv(TOP_ANIME_FILE)
    watched_anime = pd.read_csv(WATCHED_ANIME_FILE)
    manga = pd.read_csv(MANGA_FILE)

    return top_anime, watched_anime, manga


# --------------------------------------------------
# Data profiling and validation
# --------------------------------------------------

def print_profile(
    name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Print basic profiling information for one dataset."""

    print(f"\n{name}")
    print("-" * len(name))
    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns):,}")
    print(
        f"Duplicate rows: "
        f"{dataframe.duplicated().sum():,}"
    )

    print("\nMissing values:")
    print(dataframe.isna().sum())


def investigate_missing_values(
    name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Investigate missing-value patterns in one dataset."""

    rows_with_missing = dataframe[
        dataframe.isna().any(axis=1)
    ]

    completely_blank_rows = dataframe[
        dataframe.isna().all(axis=1)
    ]

    heading = f"Missing-value investigation: {name}"

    print(f"\n{heading}")
    print("-" * len(heading))
    print(
        "Rows containing at least one missing value: "
        f"{len(rows_with_missing):,}"
    )
    print(
        f"Completely blank rows: "
        f"{len(completely_blank_rows):,}"
    )

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
    """Check that required columns exist and contain valid values."""

    heading = f"Required-field check: {name}"

    print(f"\n{heading}")
    print("-" * len(heading))

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        print(
            f"Missing required columns: "
            f"{missing_columns}"
        )
        return

    invalid_rows = dataframe[
        dataframe[required_columns]
        .isna()
        .any(axis=1)
    ]

    print(
        f"Rows missing required values: "
        f"{len(invalid_rows):,}"
    )

    if invalid_rows.empty:
        print("All required fields are populated.")
    else:
        print("\nRows that should be quarantined:")
        print(invalid_rows)


def validate_everything(
    name: str,
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Run all current data-quality checks for one dataset."""

    heading = f"Validation report: {name}"

    print(f"\n{heading}")
    print("=" * len(heading))

    print_profile(
        name,
        dataframe,
    )

    investigate_missing_values(
        name,
        dataframe,
    )

    check_required_fields(
        name,
        dataframe,
        required_columns,
    )


# --------------------------------------------------
# Row separation and cleaning
# --------------------------------------------------

def separate_valid_and_quarantined_rows(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate valid rows from rows missing required values."""

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise KeyError(
            "Cannot separate rows because required columns "
            f"are missing: {missing_columns}"
        )

    quarantine_mask = (
        dataframe[required_columns]
        .isna()
        .any(axis=1)
    )

    valid_rows = dataframe.loc[~quarantine_mask].copy()
    quarantined_rows = dataframe.loc[quarantine_mask].copy()

    return valid_rows, quarantined_rows


def clean_text_column(
    dataframe: pd.DataFrame,
    column_name: str,
) -> pd.DataFrame:
    """Remove leading, trailing, and repeated whitespace."""

    if column_name not in dataframe.columns:
        raise KeyError(
            f"Text column not found: {column_name}"
        )

    cleaned_dataframe = dataframe.copy()

    cleaned_dataframe[column_name] = (
        cleaned_dataframe[column_name]
        .astype("string")
        .str.strip()
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
    )

    return cleaned_dataframe


def create_title_key(
    dataframe: pd.DataFrame,
    source_column: str,
    key_column: str = "title_key",
) -> pd.DataFrame:
    """Create a normalized technical key for exact title matching."""

    if source_column not in dataframe.columns:
        raise KeyError(
            f"Title column not found: {source_column}"
        )

    keyed_dataframe = dataframe.copy()

    keyed_dataframe[key_column] = (
        keyed_dataframe[source_column]
        .astype("string")
        .str.lower()
        .str.strip()
        .str.replace(
            r"[^a-z0-9\s]",
            " ",
            regex=True,
        )
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.strip()
    )

    return keyed_dataframe


# --------------------------------------------------
# Saving pipeline outputs
# --------------------------------------------------

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


def save_quarantined_rows(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    """Save quarantined rows to the quarantined output folder."""

    output_path = QUARANTINED_FOLDER / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print("\nSaved quarantined rows to:")
    print(output_path)


def print_separation_results(
    name: str,
    valid_rows: pd.DataFrame,
    quarantined_rows: pd.DataFrame,
) -> None:
    """Print valid and quarantined row counts."""

    heading = f"Separation results: {name}"

    print(f"\n{heading}")
    print("-" * len(heading))
    print(f"Valid rows: {len(valid_rows):,}")
    print(
        f"Quarantined rows: "
        f"{len(quarantined_rows):,}"
    )


def process_dataset(
    name: str,
    dataframe: pd.DataFrame,
    required_columns: list[str],
    title_column: str,
    valid_filename: str,
    quarantined_filename: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate, separate, clean, key, and save one dataset.

    Returns:
        A tuple containing the valid keyed rows and the
        quarantined rows.
    """

    validate_everything(
        name,
        dataframe,
        required_columns,
    )

    valid_rows, quarantined_rows = (
        separate_valid_and_quarantined_rows(
            dataframe,
            required_columns,
        )
    )

    cleaned_rows = clean_text_column(
        valid_rows,
        title_column,
    )

    keyed_rows = create_title_key(
        cleaned_rows,
        title_column,
    )

    print_separation_results(
        name,
        keyed_rows,
        quarantined_rows,
    )

    save_valid_rows(
        keyed_rows,
        valid_filename,
    )

    save_quarantined_rows(
        quarantined_rows,
        quarantined_filename,
    )

    return keyed_rows, quarantined_rows


# --------------------------------------------------
# Join and title-key investigation
# --------------------------------------------------

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
    print(
        top_anime["anime_name"]
        .head(10)
        .to_string(index=False)
    )

    print("\nSample Most Watched Anime titles:")
    print(
        watched_anime["Anime Name"]
        .head(10)
        .to_string(index=False)
    )

    print("\nSample Best-Selling Manga titles:")
    print(
        manga["Manga series"]
        .head(10)
        .to_string(index=False)
    )


def print_title_key_samples(
    top_anime: pd.DataFrame,
    watched_anime: pd.DataFrame,
    manga: pd.DataFrame,
) -> None:
    """Print sample original titles and normalized title keys."""

    print("\nSample Top Anime title keys:")
    print(
        top_anime[
            [
                "anime_name",
                "title_key",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nSample Watched Anime title keys:")
    print(
        watched_anime[
            [
                "Anime Name",
                "title_key",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nSample Manga title keys:")
    print(
        manga[
            [
                "Manga series",
                "title_key",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


def inspect_match_coverage(
    top_anime: pd.DataFrame,
    watched_anime: pd.DataFrame,
    manga: pd.DataFrame,
) -> None:
    """Measure exact title overlap and duplicate join keys."""

    top_keys = set(
        top_anime["title_key"].dropna()
    )

    watched_keys = set(
        watched_anime["title_key"].dropna()
    )

    manga_keys = set(
        manga["title_key"].dropna()
    )

    top_watched_matches = (
        top_keys.intersection(watched_keys)
    )

    top_manga_matches = (
        top_keys.intersection(manga_keys)
    )

    print("\nExact-match coverage")
    print("====================")

    print(
        "\nUnique Top Anime titles: "
        f"{top_anime['title_key'].nunique():,}"
    )

    print(
        "Unique Watched Anime titles: "
        f"{watched_anime['title_key'].nunique():,}"
    )

    print(
        "Unique Manga titles: "
        f"{manga['title_key'].nunique():,}"
    )

    print(
        "\nExact matches between Top Anime "
        "and Watched Anime: "
        f"{len(top_watched_matches):,}"
    )

    print(
        "Exact matches between Top Anime "
        "and Manga: "
        f"{len(top_manga_matches):,}"
    )

    print("\nDuplicate title keys:")

    print(
        "Top Anime: "
        f"{top_anime['title_key'].duplicated().sum():,}"
    )

    print(
        "Watched Anime: "
        f"{watched_anime['title_key'].duplicated().sum():,}"
    )

    print(
        "Manga: "
        f"{manga['title_key'].duplicated().sum():,}"
    )

    print(
        "\nSample Top Anime ↔ Watched Anime matches:"
    )
    print(
        sorted(top_watched_matches)[:20]
    )

    print(
        "\nSample Top Anime ↔ Manga matches:"
    )
    print(
        sorted(top_manga_matches)[:20]
    )


def inspect_duplicate_title_keys(
    dataframe: pd.DataFrame,
    name: str,
    title_column: str,
) -> None:
    """Display rows whose title key appears more than once."""

    duplicate_mask = (
        dataframe["title_key"]
        .duplicated(keep=False)
    )

    duplicate_rows = (
        dataframe.loc[duplicate_mask]
        .sort_values("title_key")
    )

    heading = f"Duplicate-key investigation: {name}"

    print(f"\n{heading}")
    print("=" * len(heading))

    print(
        "Rows involved in duplicate keys: "
        f"{len(duplicate_rows):,}"
    )

    print(
        "Distinct duplicated keys: "
        f"{duplicate_rows['title_key'].nunique():,}"
    )

    if duplicate_rows.empty:
        print("No duplicate title keys found.")
        return

    columns_to_display = [
        title_column,
        "title_key",
        "Most Watched in Country",
        "Ratings",
        "Number of Episodes",
        "Release Year",
    ]

    available_columns = [
        column
        for column in columns_to_display
        if column in duplicate_rows.columns
    ]

    print()
    print(
        duplicate_rows[available_columns]
        .to_string(index=False)
    )


# --------------------------------------------------
# Semantic validation
# --------------------------------------------------

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
        dataframe[
            "Duration per Episode (minutes)"
        ] > 90
    ]

    print("\nSemantic validation: Most Watched Anime")
    print("========================================")

    print(
        "Rows with suspicious release years: "
        f"{len(suspicious_release_years):,}"
    )

    print(
        "Rows with unusually high episode counts: "
        f"{len(suspicious_episode_counts):,}"
    )

    print(
        "Rows with unusually long episode durations: "
        f"{len(suspicious_durations):,}"
    )


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main() -> None:
    """Run the anime and manga data preparation pipeline."""

    create_output_directories()

    top_anime, watched_anime, manga = load_datasets()

    keyed_top_anime, _ = process_dataset(
        name="Top 1000 Anime",
        dataframe=top_anime,
        required_columns=[
            "anime_id",
            "anime_name",
        ],
        title_column="anime_name",
        valid_filename="top_1000_anime_cleaned.csv",
        quarantined_filename=(
            "top_1000_anime_missing_required.csv"
        ),
    )

    keyed_watched_anime, _ = process_dataset(
        name="Most Watched Anime",
        dataframe=watched_anime,
        required_columns=[
            "Anime Name",
        ],
        title_column="Anime Name",
        valid_filename=(
            "most_watched_anime_cleaned.csv"
        ),
        quarantined_filename=(
            "most_watched_missing_titles.csv"
        ),
    )

    keyed_manga, _ = process_dataset(
        name="Best-Selling Manga",
        dataframe=manga,
        required_columns=[
            "Manga series",
        ],
        title_column="Manga series",
        valid_filename=(
            "best_selling_manga_cleaned.csv"
        ),
        quarantined_filename=(
            "best_selling_manga_missing_titles.csv"
        ),
    )

    inspect_join_columns(
        keyed_top_anime,
        keyed_watched_anime,
        keyed_manga,
    )

    print_title_key_samples(
        keyed_top_anime,
        keyed_watched_anime,
        keyed_manga,
    )

    inspect_match_coverage(
        keyed_top_anime,
        keyed_watched_anime,
        keyed_manga,
    )

    inspect_duplicate_title_keys(
        dataframe=keyed_watched_anime,
        name="Most Watched Anime",
        title_column="Anime Name",
    )

    check_watched_anime_semantics(
        keyed_watched_anime,
    )


if __name__ == "__main__":
    main()