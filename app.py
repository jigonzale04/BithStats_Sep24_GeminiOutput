"""Main Streamlit application entry point."""

import streamlit as st
import pandas as pd
from src.data_loader import load_and_validate_data
from src.components import render_header, render_sidebar, render_kpi_strip
from src.visualizations import (
    plot_monthly_trend,
    plot_state_choropleth,
    plot_state_rankings,
    plot_top_bottom_geos,
    plot_sex_comparison,
    plot_state_month_heatmap,
)

# Page configuration
st.set_page_config(
    page_title="Provisional Natality Analytics",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_filters(
    df: pd.DataFrame, states: list, months: list, sex: str
) -> pd.DataFrame:
    """Filter DataFrame according to sidebar parameters."""
    mask = df["state_of_residence"].isin(states) & df["month"].isin(months)
    if sex != "All":
        mask = mask & (df["sex_of_infant"] == sex)
    return df[mask].copy()


def main():
    # 1. Load Data
    try:
        raw_df = load_and_validate_data()
    except Exception as e:
        st.error(f"Data loading failed: {e}")
        st.stop()

    # 2. Header
    render_header()

    # 3. Sidebar
    selected_states, selected_months, selected_sex = render_sidebar(raw_df)

    # 4. Filter Data
    filtered_df = apply_filters(raw_df, selected_states, selected_months, selected_sex)

    # Empty State Guard
    if filtered_df.empty:
        st.warning(
            "⚠️ No observations match the current filter selection. "
            "Please select at least one State and one Month from the sidebar."
        )
        return

    # 5. KPI Strip
    render_kpi_strip(filtered_df)

    # 6. Tab Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🗺️ Geographic Analysis",
        "📅 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📖 About the Data",
    ])

    # Tab 1: Overview
    with tab1:
        col_map, col_trend = st.columns([1.2, 1.0])
        with col_map:
            st.plotly_chart(plot_state_choropleth(filtered_df), use_container_width=True)
        with col_trend:
            st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

    # Tab 2: Geographic Analysis
    with tab2:
        col_rank, col_disparity = st.columns([1.1, 1.0])
        with col_rank:
            st.plotly_chart(plot_state_rankings(filtered_df), use_container_width=True)
        with col_disparity:
            st.plotly_chart(plot_top_bottom_geos(filtered_df, n=5), use_container_width=True)
            st.caption(
                "💡 **Pedagogical Note:** Notice how top states (e.g., California, Texas) dominate absolute volumes. "
                "Remind students to differentiate volume differences driven by total state population from fertility trends."
            )

    # Tab 3: Monthly & Sex Analysis
    with tab3:
        st.plotly_chart(plot_sex_comparison(filtered_df), use_container_width=True)

        if selected_sex == "All":
            sex_summary = filtered_df.groupby("sex_of_infant")["births"].sum()
            f_count = sex_summary.get("Female", 0)
            m_count = sex_summary.get("Male", 0)
            ratio = (m_count / f_count * 100) if f_count > 0 else 0
            st.info(f"**Secondary Ratio Indicator:** Current selection exhibits a Sex Ratio at Birth of **{ratio:.2f} males per 100 females**.")

        st.plotly_chart(plot_state_month_heatmap(filtered_df), use_container_width=True)

    # Tab 4: Data Table & Download
    with tab4:
        st.subheader("Filtered Dataset View")
        st.markdown(f"Displaying **{len(filtered_df):,}** records matching current criteria.")

        display_df = filtered_df[[
            "state_of_residence", "month", "month_code", "year_code", "sex_of_infant", "births"
        ]].sort_values(["state_of_residence", "month_code", "sex_of_infant"])

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "state_of_residence": "State / Geography",
                "month": "Month",
                "month_code": "Month Code",
                "year_code": "Year",
                "sex_of_infant": "Infant Sex",
                "births": st.column_config.NumberColumn("Birth Count", format="%d"),
            },
            hide_index=True,
        )

        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered CSV",
            data=csv_data,
            file_name="filtered_provisional_natality_2025.csv",
            mime="text/csv",
        )

    # Tab 5: About the Data
    with tab5:
        st.subheader("Methodology and Analytical Guidelines")
        st.markdown(
            """
            ### Purpose & Audience
            This dashboard is configured for **undergraduate business analytics** students to build competency in:
            - **Exploratory Data Analysis (EDA):** Detecting seasonal peaks, sex ratios, and geographic concentrations.
            - **Confounder Awareness:** Understanding why California and Texas appear highest in birth counts (population scale) and why gross counts should not be treated as birth rates.
            
            ### Data Source
            - **Origin:** CDC National Center for Health Statistics (NCHS) National Vital Statistics System (NVSS).
            - **Data Type:** Provisional Natality Records for 2025.
            
            ### Critical Limitations
            1. **Provisional Status:** Provisional counts are based on flow of birth certificates received by NCHS and are subject to late submissions and retrospective revisions.
            2. **Denominator Absence:** This dataset supplies absolute frequencies ($N$). True comparative fertility rates require age-adjusted female population denominators from the U.S. Census Bureau.
            
            ### Suggested Guided Inquiry Questions
            - *Do late summer months (July–September) consistently exhibit higher birth volumes across states, or is the pattern localized?*
            - *Is the male-to-female ratio consistent across states, or are anomalies present due to small sample variations in lower-population states?*
            """
        )


if __name__ == "__main__":
    main()
