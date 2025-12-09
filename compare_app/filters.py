import streamlit as st
import pandas as pd

from .config import M_TO_FT


def render_filters(df: pd.DataFrame, length_unit: str) -> pd.DataFrame:
    """
    Render the global filters and return a filtered copy of df.

    Filters:
    - Displacement type (exact match) Not sure if this is useful enough  
    - Material (exact match) Might be useful, don't know yet
    - Base price range (M€) Very useful
    - LOA range (slider in m or ft, depending on length_unit) Very useful
    """
    # TODO: add option to reset all filters?
    # TODO: consider adding/change more filters (e.g., year, etc.)

    st.markdown("### Filters")

    # we make sure numeric value for sliders (in case something came as object, etc.)
    # This should already be handled in the ETL, but we repeat here as redundancy.
    # Copy to avoid modifying original df
    df = df.copy()
    if "base_price" in df.columns:
        df["base_price"] = pd.to_numeric(df["base_price"], errors="coerce")
    if "loa_metric" in df.columns:
        df["loa_metric"] = pd.to_numeric(df["loa_metric"], errors="coerce")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    # --- Displacement type filter ------------------------------------------
    with col_f1:
        if "displacement_type" in df.columns:
            disp_opts = (
                ["All"]
                + sorted(df["displacement_type"].dropna().unique().tolist())
            )
        else:
            disp_opts = ["All"]
        selected_disp = st.selectbox("Displacement type", disp_opts, index=0)

    # --- Material filter ----------------------------------------------------
    with col_f2:
        if "material" in df.columns:
            mat_opts = ["All"] + sorted(df["material"].dropna().unique().tolist())
        else:
            mat_opts = ["All"]
        selected_mat = st.selectbox("Material", mat_opts, index=0)

    # --- Base price range (M€) ---------------------------------------------
    with col_f3:
        if "base_price" in df.columns and df["base_price"].notna().any():
            min_price = float(df["base_price"].min())
            max_price = float(df["base_price"].max())
            price_range = st.slider(
                "Base price (M€)",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
            )
        else:
            price_range = (None, None)

    # --- LOA range (with unit toggle) --------------------------------------
    with col_f4:
        if "loa_metric" in df.columns and df["loa_metric"].notna().any():
            # Base values in meters
            min_loa_m = float(df["loa_metric"].min())
            max_loa_m = float(df["loa_metric"].max())

            if length_unit == "m":
                # Slider in meters
                loa_min_display = min_loa_m
                loa_max_display = max_loa_m
                loa_value_display = (min_loa_m, max_loa_m)
                loa_range_display = st.slider(
                    "Length Overall (LOA)",
                    min_value=loa_min_display,
                    max_value=loa_max_display,
                    value=loa_value_display,
                )
                # Selected range in meters
                loa_range_m = loa_range_display
                # Show equivalent in feet
                st.caption(
                    f"{loa_range_m[0] * M_TO_FT:.1f} ft – {loa_range_m[1] * M_TO_FT:.1f} ft"
                )

            else:  # length_unit as "ft"
                # convert base range to ft for the slider
                min_loa_ft = min_loa_m * M_TO_FT
                max_loa_ft = max_loa_m * M_TO_FT
                loa_min_display = min_loa_ft
                loa_max_display = max_loa_ft
                loa_value_display = (min_loa_ft, max_loa_ft)
                loa_range_display = st.slider(
                    "Length Overall (LOA)",
                    min_value=loa_min_display,
                    max_value=loa_max_display,
                    value=loa_value_display,
                )
                # convert selected range (ft) back to meters for the filters
                loa_range_m = (
                    loa_range_display[0] / M_TO_FT,
                    loa_range_display[1] / M_TO_FT,
                )
                # Show equivalent in meters
                st.caption(
                    f"{loa_range_m[0]:.1f} m – {loa_range_m[1]:.1f} m"
                )
        else:
            loa_range_m = (None, None)

    # --- Apply filters ------------------------------------------------------
    filtered = df.copy()

    if selected_disp != "All" and "displacement_type" in filtered.columns:
        filtered = filtered[filtered["displacement_type"] == selected_disp]

    if selected_mat != "All" and "material" in filtered.columns:
        filtered = filtered[filtered["material"] == selected_mat]

    if price_range[0] is not None and "base_price" in filtered.columns:
        price_col = filtered["base_price"]
        filtered = filtered[
            price_col.isna() | (
            (price_col >= price_range[0]) &
            (price_col <= price_range[1])
            )
        ]

    if loa_range_m[0] is not None and "loa_metric" in filtered.columns:
        loa_col = filtered["loa_metric"]
        filtered = filtered[
            loa_col.isna() | (
            (loa_col >= loa_range_m[0]) &
            (loa_col <= loa_range_m[1])
            )
        ]

    return filtered
