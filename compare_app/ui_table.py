import streamlit as st
import pandas as pd


def render_table_tab(df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """
    Render the 'Table' tab:
    - Show filtered dataframe
    - Show counts
    - Allow CSV download of the filtered data
    """

    st.markdown("### Filtered dataset")

    st.write(f"Showing {len(filtered)} of {len(df)} total yachts.")

    # Display the filtered dataframe
    st.dataframe(filtered, use_container_width=True)

    # Download button for filtered data
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered CSV",
        data=csv_bytes,
        file_name="yachts_filtered.csv",
        mime="text/csv",
    )

