"""UI components: Header, warnings, sidebar filters, and KPI cards."""

from typing import Tuple, List
import pandas as pd
import streamlit as st
from src.config import MONTH_ORDER, APP_TITLE
from src.metrics import compute_kpis


def render_header():
    """Render the dashboard header and methodological disclaimers."""
    st.title(APP_TITLE)
    st.markdown(
        """
        Interactive analytical dashboard for studying provisional U.S. natality patterns across 
        geographies, calendar months, and infant sexes.
        """
    )

    # Attribution and methodological notices
    c1, c2, c3 = st.columns([1.2, 1.4, 1.4])
    with c1:
        st.info("🏛️ **Source:** CDC NCHS WONDER Database")
    with c2:
        st.warning("⚠️ **Provisional Data:** Subject to revision and late registration updates.")
    with c3:
        st.error("📊 **Counts ≠ Rates:** Gross figures reflect population scale, not fertility rates.")
    st.markdown("---")


def render_sidebar(df: pd.DataFrame) -> Tuple[List[str], List[str], str]:
    """Render sidebar filters with bulk actions and active filter summaries."""
    st.sidebar.header("Filter Controls")

    all_states = sorted(df["state_of_residence"].unique().tolist())
    all_months = [m for m in MONTH_ORDER if m in df["month"].cat.categories]
    all_sexes = ["All", "Female", "Male"]

    # Session State Initialization for filters
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    # Action Buttons: Select All & Reset
    btn_col1, btn_col2 = st.sidebar.columns(2)
    with btn_col1:
        if st.button("Select All", use_container_width=True):
            st.session_state.selected_states = all_states
            st.session_state.selected_months = all_months
            st.session_state.selected_sex = "All"
            st.rerun()

    with btn_col2:
        if st.button("Reset Filters", use_container_width=True):
            st.session_state.selected_states = all_states
            st.session_state.selected_months = all_months
            st.session_state.selected_sex = "All"
            st.rerun()

    # Multiselect Widgets
    selected_states = st.sidebar.multiselect(
        "Geographies (States & DC):",
        options=all_states,
        default=st.session_state.selected_states,
        key="selected_states",
    )

    selected_months = st.sidebar.multiselect(
        "Months:",
        options=all_months,
        default=st.session_state.selected_months,
        key="selected_months",
    )

    selected_sex = st.sidebar.radio(
        "Infant Sex:",
        options=all_sexes,
        index=all_sexes.index(st.session_state.selected_sex),
        key="selected_sex",
        horizontal=True,
    )

    # Active Filters Summary expander
    with st.sidebar.expander("Active Filter Summary", expanded=False):
        st.caption(f"**Geographies Selected:** {len(selected_states)} of {len(all_states)}")
        st.caption(f"**Months Selected:** {len(selected_months)} of {len(all_months)}")
        st.caption(f"**Sex Subset:** {selected_sex}")

    return selected_states, selected_months, selected_sex


def render_kpi_strip(filtered_df: pd.DataFrame):
    """Render the 5 executive KPI summary cards."""
    kpis = compute_kpis(filtered_df)
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            label="Total Births",
            value=f"{kpis['total_births']:,}",
        )
    with c2:
        st.metric(
            label="Active Geographies",
            value=f"{kpis['unique_geos']} / 51",
        )
    with c3:
        st.metric(
            label="Avg. Births / Month",
            value=f"{kpis['avg_births_per_month']:,.0f}",
        )
    with c4:
        st.metric(
            label="Top Geography",
            value=kpis["top_geo"],
            help=f"Volume: {kpis['top_geo_births']:,} births" if kpis["top_geo"] != "N/A" else None,
        )
    with c5:
        st.metric(
            label="Peak Month",
            value=kpis["top_month"],
            help=f"Volume: {kpis['top_month_births']:,} births" if kpis["top_month"] != "N/A" else None,
        )
    st.markdown("---")
