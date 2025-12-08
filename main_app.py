import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from yacht_etl.io.master_loader import load_csv_file

from compare_app.config import APP_TITLE, OUTPUT_PATH, __version__
from compare_app.etl_ui import render_sidebar_etl
from compare_app.filters import render_filters
from compare_app.ui_overview import render_overview_tab
from compare_app.ui_table import render_table_tab
from compare_app.ui_charts import render_charts_tab
from compare_app.ui_compare import render_compare_tab


def main():
    # --- Page config & title ------------------------------------------------
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)

    # Display version & unit settings
    st.sidebar.caption(f"**App version:** {__version__}")
    st.sidebar.subheader("Display settings")

    # session state stays when switching tabs
    if "length_unit" not in st.session_state:
        st.session_state["length_unit"] = "m"

    length_unit = st.sidebar.radio(
        "Length unit",
        ["m", "ft"],
        index=0 if st.session_state["length_unit"] == "m" else 1,
    )
    st.session_state["length_unit"] = length_unit

    # --- Sidebar: ETL + settings -------------------------------------------
    # ETL / cheatsheet upload / build master CSV
    render_sidebar_etl()
    # --- Load master dataset -----------------------------------------------
    if not OUTPUT_PATH.exists():
        st.info(
            "No dataset found yet. "
            "Upload an Excel sheet and click **Build / refresh CSV** "
            "in the sidebar to create it."
        )
        return

    try:
        df = load_csv_file(OUTPUT_PATH)
    except Exception as e:
        st.error(f"Failed to load CSV from {OUTPUT_PATH}: {e}")
        return

    if df.empty:
        st.warning("The dataset is empty.")
        return

    # --- Global filters -----------------------------------------------------
    filtered = render_filters(df, length_unit)

    # --- Tabs ---------------------------------------------------------------
    tab_overview, tab_table, tab_compare, tab_charts = st.tabs(
        ["Overview", "Table", "Compare", "Charts & Analytics"]
    )

    with tab_overview:
        render_overview_tab(filtered, length_unit)

    with tab_table:
        render_table_tab(df, filtered)

    with tab_compare:
        render_compare_tab(filtered, length_unit)
        
    with tab_charts:
        render_charts_tab(filtered, length_unit)



if __name__ == "__main__":
    main()
