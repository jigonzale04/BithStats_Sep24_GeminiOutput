"""Cached data loading and schema validation."""

from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import MONTH_ORDER, US_STATE_ABBR

REQUIRED_COLUMNS = {
    "state_of_residence": object,
    "month": object,
    "month_code": "int64",
    "year_code": "int64",
    "sex_of_infant": object,
    "births": "int64",
}


def find_data_file() -> Path:
    """Resolve data file location across local development and cloud deployments."""
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "Provisional_Natality_2025_CDC.csv",
        Path(__file__).resolve().parent.parent / "Provisional_Natality_2025_CDC.csv",
        Path("data/Provisional_Natality_2025_CDC.csv"),
        Path("Provisional_Natality_2025_CDC.csv"),
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "Provisional_Natality_2025_CDC.csv was not found in ./data/ or root directory."
    )


@st.cache_data(show_spinner="Loading natality dataset...")
def load_and_validate_data() -> pd.DataFrame:
    """Load, validate, and enrich the provisional CDC natality dataset."""
    file_path = find_data_file()
    df = pd.read_csv(file_path)

    # 1. Column presence check
    missing_cols = set(REQUIRED_COLUMNS.keys()) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    # 2. Null check
    null_counts = df[list(REQUIRED_COLUMNS.keys())].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Null values detected in mandatory fields:\n{null_counts}")

    # 3. Numeric validity check
    if (df["births"] < 0).any():
        raise ValueError("Negative birth counts found in dataset.")

    # 4. Enforce strict categorical ordering for months
    df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)

    # 5. Enrich with state postal code for choropleth mapping
    df["state_abbr"] = df["state_of_residence"].map(US_STATE_ABBR)
    unmapped = df[df["state_abbr"].isna()]["state_of_residence"].unique()
    if len(unmapped) > 0:
        st.warning(f"Unmapped geographies for map view: {', '.join(unmapped)}")

    return df
