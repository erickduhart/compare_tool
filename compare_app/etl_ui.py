import streamlit as st
import pandas as pd

from yacht_etl import build_master_csv
from .config import (
    BASE_TEMPLATE_PATH,
    OUTPUT_PATH,
    __version__,
)

import logging
logger = logging.getLogger("yacht_etl")


def render_sidebar_etl() -> None:
    """
    Render the sidebar section for:
    - Showing ETL/version info
    - Uploading an Excel sheet
    - Selecting the sheet
    - Running the ETL to build/refresh the master CSV
    """
    # ----- Sidebar header --------
    st.sidebar.header("**Options**")
    st.sidebar.markdown("---")

    # --- Upload Excel cheatsheet -------------------------------------------
    st.sidebar.subheader("Import Excel sheet")

    excel_file = st.sidebar.file_uploader(
        "Upload Excel file (.xlsx)",
        type=["xlsx"],
        key="cheatsheet_uploader",
    )

    sheet_name = None
    if excel_file is not None:
        try:
            xls = pd.ExcelFile(excel_file)
            sheet_name = st.sidebar.selectbox(
                "Select sheet to import",
                xls.sheet_names,
                key="cheatsheet_sheet",
            )
        except Exception as e:
            st.sidebar.error(f"Failed to read Excel file: {e}")

    # --- Run ETL button -----------------------------------------------------
    rebuild = st.sidebar.button("Build / refresh CSV")

    if rebuild:
        if excel_file is None:
            st.sidebar.error("Please upload an Excel file (.xlsx) first.")
            return

        if sheet_name is None:
            st.sidebar.error("Please select a sheet.")
            return

        st.sidebar.info("Running ETL to build dataset…")

        try:
            # Ensure output directory exists (still needed)
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            # Run the ETL builder
            logger.info("ETL request: sheet=%s output=%s", sheet_name, OUTPUT_PATH)
            build_master_csv(
                template_path=BASE_TEMPLATE_PATH,
                excel_source=excel_file,
                excel_sheet=sheet_name,
                output_path=OUTPUT_PATH,
            )

            # ---- memory handling ----
            # drop references so Python can free memory
            del sheet_name
            del excel_file

            st.session_state.pop("cheatsheet_uploader", None)
            st.session_state.pop("cheatsheet_sheet", None)

            st.sidebar.success("ETL completed successfully ✅")
        except Exception as e:
            logger.exception("ETL failed while building master CSV")
            st.sidebar.error(f"ETL failed: {e}")




    st.sidebar.markdown("---")

    # --- paths info --------------------------------------------------------
    # not very useful to be honest as it is run on a container, but whatever
    # good for building locally
    st.sidebar.write("Current paths:")
    st.sidebar.code(f"Template: {BASE_TEMPLATE_PATH}")
    st.sidebar.code(f"Output:   {OUTPUT_PATH}")

    

    