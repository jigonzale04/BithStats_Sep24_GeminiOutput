import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
DATA_PATH = "Provisional_Natality_2025_CDC.csv"
REQUIRED_FIELDS = ["state_of_residence", "month", "sex_of_infant", "births"]

try:
    df = pd.read_csv(DATA_PATH)
    # Normalize column names: strip whitespace, lowercase, replace spaces with underscores
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # Validate required logical fields
    missing_fields = [col for col in REQUIRED_FIELDS if col not in df.columns]
    if missing_fields:
        st.error(f"Missing required logical fields: {', '.join(missing_fields)}")
        st.write(df.columns)
        st.stop()

    # Convert births to numeric and drop nulls
    df["births"] = pd.to_numeric(df["births"], errors="coerce")
    df = df.dropna(subset=["births"])

except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading the dataset: {e}")
    st.stop()

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

# Months
available_months = sorted(df["month"].dropna().unique().tolist())
month_options = ["All"] + available_months
selected_months = st.sidebar.multiselect(
    "Select Month", options=month_options, default=["All"]
)

# Gender
available_genders = sorted(df["sex_of_infant"].dropna().unique().tolist())
gender_options = ["All"] + available_genders
selected_genders = st.sidebar.multiselect(
    "Select Gender", options=gender_options, default=["All"]
)

# State
available_states = sorted(df["state_of_residence"].dropna().unique().tolist())
state_options = ["All"] + available_states
selected_states = st.sidebar.multiselect(
    "Select State", options=state_options, default=["All"]
)

# STEP 5 — Filtering Logic
filtered_df = df.copy()

if "All" not in selected_months and selected_months:
    filtered_df = filtered_df[filtered_df["month"].isin(selected_months)]

if "All" not in selected_genders and selected_genders:
    filtered_df = filtered_df[filtered_df["sex_of_infant"].isin(selected_genders)]

if "All" not in selected_states and selected_states:
    filtered_df = filtered_df[filtered_df["state_of_residence"].isin(selected_states)]

# STEP 9 — Edge Case Handling: Empty filter result
if (
    filtered_df.empty
    or not selected_months
    or not selected_genders
    or not selected_states
):
    st.warning("No data found matching the selected filter criteria.")
else:
    # STEP 6 — Aggregation
    agg_df = (
        filtered_df.groupby(["state_of_residence", "sex_of_infant"], as_index=False)[
            "births"
        ]
        .sum()
        .sort_values(by="state_of_residence", ascending=True)
    )

    # STEP 7 — Plot
    fig = px.bar(
        agg_df,
        x="state_of_residence",
        y="births",
        color="sex_of_infant",
        barmode="group",
        title="Total Births by State and Gender",
        labels={
            "state_of_residence": "State of Residence",
            "births": "Total Births",
            "sex_of_infant": "Gender",
        },
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, linecolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="whitesmoke", linecolor="lightgray"),
        legend_title_text="Gender",
        autosize=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    # STEP 8 — Show Filtered Table
    st.subheader("Filtered Data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
