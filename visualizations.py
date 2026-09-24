"""Plotly chart generators with accessible color palettes and non-truncated axes."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.config import COLOR_PALETTE, MONTH_ORDER


def plot_monthly_trend(df: pd.DataFrame) -> go.Figure:
    """Create a 12-month trend line chart with baseline starting at zero."""
    monthly_data = (
        df.groupby("month", observed=True)["births"]
        .sum()
        .reindex(MONTH_ORDER)
        .dropna()
        .reset_index()
    )

    fig = px.line(
        monthly_data,
        x="month",
        y="births",
        markers=True,
        title="Monthly Total Birth Trend",
        labels={"month": "Month", "births": "Recorded Birth Count"},
    )
    fig.update_traces(
        line=dict(color=COLOR_PALETTE["primary"], width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Births: %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        yaxis=dict(rangemode="tozero", tickformat=","),
        xaxis=dict(tickangle=-30),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


def plot_state_choropleth(df: pd.DataFrame) -> go.Figure:
    """Render a clean US state choropleth map."""
    state_agg = (
        df.groupby(["state_of_residence", "state_abbr"], observed=True)["births"]
        .sum()
        .reset_index()
    )

    total_in_view = state_agg["births"].sum()
    state_agg["pct_of_selection"] = (
        (state_agg["births"] / total_in_view * 100).round(2) if total_in_view > 0 else 0
    )

    fig = px.choropleth(
        state_agg,
        locations="state_abbr",
        locationmode="USA-states",
        color="births",
        scope="usa",
        color_continuous_scale=COLOR_PALETTE["choropleth_scale"],
        hover_name="state_of_residence",
        hover_data={"state_abbr": False, "births": ":,", "pct_of_selection": ":.2f%"},
        labels={"births": "Birth Count", "pct_of_selection": "% of Selected Births"},
        title="Geographic Distribution of Births",
    )
    fig.update_layout(
        geo=dict(lakecolor="white"),
        coloraxis_colorbar=dict(title="Births", tickformat=","),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def plot_state_rankings(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing state rankings in descending volume."""
    state_totals = (
        df.groupby("state_of_residence", observed=True)["births"]
        .sum()
        .reset_index()
        .sort_values("births", ascending=True)
    )

    fig = px.bar(
        state_totals,
        x="births",
        y="state_of_residence",
        orientation="h",
        title="State Birth Volume Ranking",
        labels={"births": "Total Births", "state_of_residence": "State / Geography"},
    )
    fig.update_traces(
        marker_color=COLOR_PALETTE["primary"],
        hovertemplate="<b>%{y}</b><br>Total Births: %{x:,.0f}<extra></extra>",
    )
    fig.update_layout(
        xaxis=dict(rangemode="tozero", tickformat=","),
        height=max(500, len(state_totals) * 18),
        margin=dict(l=10, r=20, t=40, b=30),
    )
    return fig


def plot_top_bottom_geos(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """Side-by-side comparative bar chart contrasting the top N and bottom N states."""
    state_totals = (
        df.groupby("state_of_residence", observed=True)["births"]
        .sum()
        .reset_index()
        .sort_values("births", ascending=False)
    )

    if len(state_totals) < n * 2:
        top_df = state_totals.head(n).copy()
        top_df["Tier"] = "Highest Volume"
        combined = top_df
    else:
        top_df = state_totals.head(n).copy()
        top_df["Tier"] = f"Top {n}"
        bottom_df = state_totals.tail(n).copy()
        bottom_df["Tier"] = f"Bottom {n}"
        combined = pd.concat([top_df, bottom_df])

    fig = px.bar(
        combined,
        x="state_of_residence",
        y="births",
        color="Tier",
        barmode="group",
        title=f"Disparity Spotlight: Top {n} vs. Bottom {n} Geographies",
        labels={"state_of_residence": "State", "births": "Births"},
        color_discrete_map={f"Top {n}": COLOR_PALETTE["primary"], f"Bottom {n}": COLOR_PALETTE["female"]},
    )
    fig.update_layout(
        yaxis=dict(rangemode="tozero", tickformat=","),
        xaxis=dict(tickangle=-25),
        margin=dict(l=30, r=20, t=50, b=40),
    )
    fig.update_traces(hovertemplate="<b>%{x}</b> (%{data.name})<br>Births: %{y:,.0f}<extra></extra>")
    return fig


def plot_sex_comparison(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing Male and Female births month-by-month."""
    sex_monthly = (
        df.groupby(["month", "sex_of_infant"], observed=True)["births"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        sex_monthly,
        x="month",
        y="births",
        color="sex_of_infant",
        barmode="group",
        title="Infant Sex Distribution by Month",
        labels={"month": "Month", "births": "Recorded Births", "sex_of_infant": "Infant Sex"},
        color_discrete_map={"Female": COLOR_PALETTE["female"], "Male": COLOR_PALETTE["male"]},
        category_orders={"month": MONTH_ORDER},
    )
    fig.update_layout(
        yaxis=dict(rangemode="tozero", tickformat=","),
        margin=dict(l=30, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_traces(hovertemplate="<b>%{x}</b> (%{data.name})<br>Births: %{y:,.0f}<extra></extra>")
    return fig


def plot_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """State-by-Month heatmap highlighting seasonal variations and geographical concentrations."""
    pivot = (
        df.pivot_table(
            index="state_of_residence",
            columns="month",
            values="births",
            aggfunc="sum",
            fill_value=0,
            observed=True,
        )
    )
    cols_in_order = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[cols_in_order]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=COLOR_PALETTE["heatmap_scale"],
            colorbar=dict(title="Births", tickformat=","),
            hovertemplate="State: %{y}<br>Month: %{x}<br>Births: %{z:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Birth Counts Matrix (State × Month)",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Geography", dtick=1),
        height=max(550, len(pivot) * 16),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig
