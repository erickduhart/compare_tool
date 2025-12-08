import streamlit as st
import pandas as pd
from pathlib import Path

from yacht_etl import build_master_csv
from .config import (
    BASE_TEMPLATE_PATH,
    OUTPUT_PATH,
    NEW_DATA_DIR,
    __version__,
)


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

    # Show version
    #st.sidebar.caption(f"App version: **{__version__}**")
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
    #st.sidebar.markdown("---")
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
            # make sure output dir exists
            NEW_DATA_DIR.mkdir(parents=True, exist_ok=True)

            # Save uploaded file to disk so build_master_csv can read it by its path
            uploaded_excel_path: Path = NEW_DATA_DIR / "uploaded_cheatsheet.xlsx"
            uploaded_excel_path.write_bytes(excel_file.getbuffer())

            # Run the ETL builder
            build_master_csv(
                template_path=BASE_TEMPLATE_PATH,
                excel_path=uploaded_excel_path,
                excel_sheet=sheet_name,
                output_path=OUTPUT_PATH,
            )

            st.sidebar.success("ETL completed successfully ✅")
        except Exception as e:
            st.sidebar.error(f"ETL failed: {e}")




    st.sidebar.markdown("---")

    st.sidebar.write("Current paths:")
    st.sidebar.code(f"Template: {BASE_TEMPLATE_PATH}")
    st.sidebar.code(f"Output:   {OUTPUT_PATH}")

    

    