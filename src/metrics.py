"""Aggregation functions for KPI cards and summaries."""

from typing import Dict, Any
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate core summary metrics for the active filtered selection."""
    if df.empty:
        return {
            "total_births": 0,
            "unique_geos": 0,
            "avg_births_per_month": 0,
            "top_geo": "N/A",
            "top_geo_births": 0,
            "top_month": "N/A",
            "top_month_births": 0,
        }

    total_births = int(df["births"].sum())
    unique_geos = int(df["state_of_residence"].nunique())
    unique_months = int(df["month"].nunique())
    avg_per_month = total_births / unique_months if unique_months > 0 else 0

    # Top Geography
    geo_totals = df.groupby("state_of_residence", observed=True)["births"].sum()
    top_geo = geo_totals.idxmax() if not geo_totals.empty else "N/A"
    top_geo_births = geo_totals.max() if not geo_totals.empty else 0

    # Top Month
    month_totals = df.groupby("month", observed=True)["births"].sum()
    top_month = str(month_totals.idxmax()) if not month_totals.empty else "N/A"
    top_month_births = month_totals.max() if not month_totals.empty else 0

    return {
        "total_births": total_births,
        "unique_geos": unique_geos,
        "avg_births_per_month": avg_per_month,
        "top_geo": top_geo,
        "top_geo_births": int(top_geo_births),
        "top_month": top_month,
        "top_month_births": int(top_month_births),
    }
