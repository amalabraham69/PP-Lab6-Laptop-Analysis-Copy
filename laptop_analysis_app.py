from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Laptop Specification Explorer",
    page_icon="💻",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("laptop_dataset.csv")


@st.cache_data

def load_data():
    """Load the laptop dataset and create a numeric RAM column for analysis."""
    data = pd.read_csv(DATA_FILE)
    data.columns = data.columns.str.strip()
    data["Inches"] = pd.to_numeric(data["Inches"], errors="coerce")
    data["Ram_GB"] = pd.to_numeric(
        data["Ram"].str.replace("GB", "", regex=False), errors="coerce"
    )
    return data.dropna(subset=["Inches", "Ram_GB"])


try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found. Keep laptop_dataset.csv beside this Python file.")
    st.stop()

st.title("Laptop Specification Explorer")
st.write(
    "Explore laptop brands, categories, screen sizes, memory and specifications "
    "using interactive filters and charts."
)

# Sidebar filters apply to every section of the dashboard.
st.sidebar.header("Dataset Filters")
companies = sorted(df["Company"].dropna().unique().tolist())
laptop_types = sorted(df["TypeName"].dropna().unique().tolist())

selected_companies = st.sidebar.multiselect(
    "Company", companies, default=companies
)
selected_types = st.sidebar.multiselect(
    "Laptop type", laptop_types, default=laptop_types
)

ram_min = int(df["Ram_GB"].min())
ram_max = int(df["Ram_GB"].max())
selected_ram = st.sidebar.slider(
    "RAM (GB)", min_value=ram_min, max_value=ram_max,
    value=(ram_min, ram_max), step=1
)

screen_min = float(df["Inches"].min())
screen_max = float(df["Inches"].max())
selected_screen = st.sidebar.slider(
    "Screen size (inches)", min_value=screen_min, max_value=screen_max,
    value=(screen_min, screen_max), step=0.1
)

filtered = df[
    df["Company"].isin(selected_companies)
    & df["TypeName"].isin(selected_types)
    & df["Ram_GB"].between(selected_ram[0], selected_ram[1])
    & df["Inches"].between(selected_screen[0], selected_screen[1])
].copy()

st.sidebar.caption("All KPIs, tables and charts update when these filters change.")

if filtered.empty:
    st.warning("No laptops match the selected filters. Change the filters in the sidebar.")
    st.stop()

# Calculate the KPIs from the filtered records.
record_count = len(filtered)
total_ram = filtered["Ram_GB"].sum()
average_ram = filtered["Ram_GB"].mean()
total_screen = filtered["Inches"].sum()
average_screen = filtered["Inches"].mean()

# Reusable grouped summaries.
company_counts = (
    filtered.groupby("Company").size().reset_index(name="Laptop Count")
    .sort_values("Laptop Count", ascending=False)
)
type_counts = (
    filtered.groupby("TypeName").size().reset_index(name="Laptop Count")
    .sort_values("Laptop Count", ascending=False)
)
ram_by_screen = (
    filtered.groupby("Inches", as_index=False)
    .agg(Average_RAM_GB=("Ram_GB", "mean"), Laptop_Count=("laptop_ID", "count"))
    .sort_values("Inches")
)

# Main dashboard sections.
overview_tab, analysis_tab, visuals_tab, insights_tab = st.tabs(
    ["Dataset Overview", "Data Analysis", "Visualizations", "Insights"]
)

with overview_tab:
    st.subheader("Laptop Dataset Overview")
    st.caption(f"Showing {record_count:,} of {len(df):,} records after filtering.")

    with st.container(border=True):
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total laptops", f"{record_count:,}")
        kpi2.metric("Total RAM", f"{total_ram:,.0f} GB")
        kpi3.metric("Average RAM", f"{average_ram:.2f} GB")
        kpi4.metric("Average screen size", f"{average_screen:.2f} in")

    st.subheader("Category-wise Record Counts")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Laptops by company**")
        st.dataframe(company_counts, use_container_width=True, hide_index=True)
    with col2:
        st.write("**Laptops by type**")
        st.dataframe(type_counts, use_container_width=True, hide_index=True)

    with st.expander("View filtered dataset"):
        st.dataframe(filtered.drop(columns=["Ram_GB"]), use_container_width=True)

with analysis_tab:
    st.subheader("Specification Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Average specifications**")
        summary = pd.DataFrame(
            {
                "Attribute": ["Screen size", "RAM"],
                "Sum": [total_screen, total_ram],
                "Average": [average_screen, average_ram],
                "Unit": ["inches", "GB"],
            }
        )
        st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
    with col2:
        st.write("**Most common values**")
        common_ram = filtered["Ram"].mode().iloc[0]
        common_size = filtered["Inches"].mode().iloc[0]
        st.write(f"- Most common RAM: **{common_ram}**")
        st.write(f"- Most common screen size: **{common_size:g} inches**")
        st.write(f"- Number of companies: **{filtered['Company'].nunique()}**")
        st.write(f"- Number of laptop types: **{filtered['TypeName'].nunique()}**")

    with st.expander("How the analysis is calculated"):
        st.write(
            "RAM values such as 8GB are converted to numeric gigabytes. "
            "The sums, averages and category counts are calculated from the "
            "records currently selected by the sidebar filters."
        )

with visuals_tab:
    st.subheader("Laptop Specification Visualizations")
    left, right = st.columns(2)

    with left:
        top_companies = company_counts.head(10).sort_values("Laptop Count")
        bar_fig = px.bar(
            top_companies,
            x="Laptop Count",
            y="Company",
            orientation="h",
            text="Laptop Count",
            title="Top 10 Companies by Laptop Records",
            labels={"Laptop Count": "Number of laptops", "Company": "Company"},
        )
        bar_fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(bar_fig, use_container_width=True)
        st.caption(
            "Interpretation: This chart compares how many laptop records belong "
            "to each of the ten most represented companies."
        )

    with right:
        line_fig = px.line(
            ram_by_screen,
            x="Inches",
            y="Average_RAM_GB",
            markers=True,
            title="Average RAM by Screen Size",
            labels={
                "Inches": "Screen size (inches)",
                "Average_RAM_GB": "Average RAM (GB)",
            },
            hover_data=["Laptop_Count"],
        )
        st.plotly_chart(line_fig, use_container_width=True)
        st.caption(
            "Interpretation: The line shows how average RAM differs across "
            "screen sizes in the filtered dataset."
        )

    scatter_fig = px.scatter(
        filtered,
        x="Inches",
        y="Ram_GB",
        color="TypeName",
        hover_data=["Company", "Product", "Cpu"],
        title="Relationship Between Screen Size and RAM",
        labels={
            "Inches": "Screen size (inches)",
            "Ram_GB": "RAM (GB)",
            "TypeName": "Laptop type",
        },
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
    st.caption(
        "Interpretation: Each point represents a laptop. The colours distinguish "
        "laptop types and help compare their screen sizes and RAM."
    )

with insights_tab:
    st.subheader("Key Insights from the Filtered Data")
    top_company = company_counts.iloc[0]
    top_type = type_counts.iloc[0]
    common_ram = filtered["Ram"].mode().iloc[0]
    common_size = filtered["Inches"].mode().iloc[0]

    st.markdown(
        f"- **Most represented company:** {top_company['Company']} "
        f"({int(top_company['Laptop Count'])} records)."
    )
    st.markdown(
        f"- **Most common laptop type:** {top_type['TypeName']} "
        f"({int(top_type['Laptop Count'])} records)."
    )
    st.markdown(f"- **Most common RAM configuration:** {common_ram}.")
    st.markdown(f"- **Most common screen size:** {common_size:g} inches.")
    st.markdown(
        f"- **Average specifications:** {average_ram:.2f} GB RAM and "
        f"{average_screen:.2f}-inch screen size."
    )

    st.info(
        "These findings describe the laptop records in this dataset. "
        "The selected CSV does not contain a price column, so this application "
        "does not make price or value-for-money comparisons."
    )

st.divider()
st.caption("Laptop Specification Explorer | Python Programming Lab 6")
