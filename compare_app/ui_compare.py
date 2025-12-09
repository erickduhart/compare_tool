import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from .config import M_TO_FT


def render_compare_tab(filtered: pd.DataFrame, length_unit: str) -> None:
    """
    Render the 'Compare' tab: select two yachts, show key specs, full specs,
    size outlines, visual bar charts and radar chart.
    """

    st.markdown("### Compare two yachts")

    # --- basic guards --------------------------------------------------------
    if len(filtered) < 2:
        st.info("Not enough yachts to compare. Adjust filters to include at least two yachts.")
        return

    comp_df = filtered.copy()

    if "name" not in comp_df.columns:
        st.warning("No 'name' column found to compare yachts.")
        return

    # --- yacht selectors ------------------------------------------------------
    yacht_names = comp_df["name"].dropna().unique().tolist()
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        yacht_a_name = st.selectbox("Yacht A", yacht_names, key="compare_yacht_a")
    with col_sel2:
        yacht_b_name = st.selectbox("Yacht B", yacht_names, key="compare_yacht_b")

    if yacht_a_name == yacht_b_name:
        st.warning("Please select two different yachts to compare.")
        return

    row_a = comp_df[comp_df["name"] == yacht_a_name].iloc[0]
    row_b = comp_df[comp_df["name"] == yacht_b_name].iloc[0]

    # --- helpers --------------------------------------------------------------
    def safe_get(row: pd.Series, col: str):
        return row.get(col) if col in row.index else None

    # Deal with units and formatting
    def format_perf(cs, ms, rg) -> str:
        cs_s = f"{cs:.1f} kn" if pd.notna(cs) else "–"
        ms_s = f"{ms:.1f} kn" if pd.notna(ms) else "–"
        rg_s = f"{rg:.0f} nm" if pd.notna(rg) else "–"
        return f"{cs_s} / {ms_s} / {rg_s}"

    def format_caps(fuel, fresh, waste, urea) -> str:
        f_s = f"{fuel:.0f} L" if pd.notna(fuel) else "–"
        fw_s = f"{fresh:.0f} L" if pd.notna(fresh) else "–"
        ww_s = f"{waste:.0f} L" if pd.notna(waste) else "–"
        u_s = f"{urea:.0f} L" if pd.notna(urea) else "–"
        return f"{f_s} / {fw_s} / {ww_s} / {u_s}"

    # --- base numeric values --------------------------------------------------
    # Some are not used directly but kept for clarity or future use
    base_a = safe_get(row_a, "base_price")
    base_b = safe_get(row_b, "base_price")

    loa_a_m = safe_get(row_a, "loa_metric")
    loa_b_m = safe_get(row_b, "loa_metric")
    beam_a_m = safe_get(row_a, "beam_metric")
    beam_b_m = safe_get(row_b, "beam_metric")
    draft_a_m = safe_get(row_a, "draft_full_load_metric")
    draft_b_m = safe_get(row_b, "draft_full_load_metric")
    area_a = safe_get(row_a, "area")
    area_b = safe_get(row_b, "area")
    gt_a = safe_get(row_a, "gross_tonnage")
    gt_b = safe_get(row_b, "gross_tonnage")

    range_a = safe_get(row_a, "range_nm")
    range_b = safe_get(row_b, "range_nm")
    cs_a = safe_get(row_a, "cruise_speed_kn")
    cs_b = safe_get(row_b, "cruise_speed_kn")
    ms_a = safe_get(row_a, "max_speed_kn")
    ms_b = safe_get(row_b, "max_speed_kn")

    fuel_a = safe_get(row_a, "fuel_oil")
    fuel_b = safe_get(row_b, "fuel_oil")
    fresh_a = safe_get(row_a, "fresh_water")
    fresh_b = safe_get(row_b, "fresh_water")
    waste_a = safe_get(row_a, "waste_water")
    waste_b = safe_get(row_b, "waste_water")
    urea_a = safe_get(row_a, "urea")
    urea_b = safe_get(row_b, "urea")

    # display units for lengths
    length_label = "m" if length_unit == "m" else "ft"
    if length_unit == "m":
        loa_a_disp, loa_b_disp = loa_a_m, loa_b_m
        beam_a_disp, beam_b_disp = beam_a_m, beam_b_m
    else:
        loa_a_disp = loa_a_m * M_TO_FT if pd.notna(loa_a_m) else None
        loa_b_disp = loa_b_m * M_TO_FT if pd.notna(loa_b_m) else None
        beam_a_disp = beam_a_m * M_TO_FT if pd.notna(beam_a_m) else None
        beam_b_disp = beam_b_m * M_TO_FT if pd.notna(beam_b_m) else None

    # --- Quick comparison (Key specs) -----------------------------------------
    st.markdown("#### Key specs comparison")

    highlight = st.checkbox("Highlight larger values", value=True)

    metrics_rows = {
        "Metric": [],
        yacht_a_name: [],
        yacht_b_name: [],
    }

    def add_metric(label: str, va, vb):
        metrics_rows["Metric"].append(label)
        metrics_rows[yacht_a_name].append(
            float(va) if va is not None and not pd.isna(va) else np.nan
        )
        metrics_rows[yacht_b_name].append(
            float(vb) if vb is not None and not pd.isna(vb) else np.nan
        )

    add_metric(f"Length (LOA) [{length_label}]", loa_a_disp, loa_b_disp)
    add_metric("Base price (M€)", base_a, base_b)
    add_metric(f"Beam [{length_label}]", beam_a_disp, beam_b_disp)
    add_metric("Area (m²)", area_a, area_b)
    add_metric("Gross Tonnage", gt_a, gt_b)
    add_metric("Range (nm)", range_a, range_b)
    add_metric("Max speed (kn)", ms_a, ms_b)

    kpi_df = pd.DataFrame(metrics_rows).set_index("Metric")

    if highlight:
        def highlight_row(s: pd.Series):
            # Convert to floats (NaNs allowed)
            vals = s.values.astype(float)

            # Collect indices of non-NaN values
            valid_indices = [i for i, v in enumerate(vals) if not np.isnan(v)]
            if not valid_indices:
                # no valid data in this row
                return [""] * len(s)

            # Find indices of min / max among valid entries
            max_idx = max(valid_indices, key=lambda i: vals[i])
            min_idx = min(valid_indices, key=lambda i: vals[i])

            styles = [""] * len(s)
            styles[max_idx] = "color: green; font-weight: bold;"
            styles[min_idx] = "color: red;"
            return styles

        styled = (
            kpi_df.style
            .apply(highlight_row, axis=1)
            .format("{:.2f}")
        )
        st.dataframe(styled, use_container_width=True)
    else:
        st.dataframe(kpi_df, use_container_width=True)

    # --- Full specs (side by side) -------------------------------------------
    st.markdown("---")
    st.markdown("#### Full specs")

    def detail_block(yacht_label: str, row: pd.Series):
        st.markdown(f"##### {yacht_label}")

        loa_m = safe_get(row, "loa_metric")
        beam_m = safe_get(row, "beam_metric")
        draft_m = safe_get(row, "draft_full_load_metric")
        area_m2 = safe_get(row, "area")

        loa_ft = loa_m * M_TO_FT if pd.notna(loa_m) else None
        beam_ft = beam_m * M_TO_FT if pd.notna(beam_m) else None
        draft_ft = draft_m * M_TO_FT if pd.notna(draft_m) else None

        loa_in = int((loa_ft - int(loa_ft)) * 12) if pd.notna(loa_ft) else None
        beam_in = int((beam_ft - int(beam_ft)) * 12) if pd.notna(beam_ft) else None
        draft_in = int((draft_ft - int(draft_ft)) * 12) if pd.notna(draft_ft) else None

        if length_unit == "m":
            loa_display = f"{loa_m:.2f} m" if pd.notna(loa_m) else "–"
            beam_display = f"{beam_m:.2f} m" if pd.notna(beam_m) else "–"
            draft_display = f"{draft_m:.2f} m" if pd.notna(draft_m) else "–"
        else:
            loa_display = f"{int(loa_ft):d} ft  {loa_in:d} in" if loa_ft is not None else "–"
            beam_display = f"{int(beam_ft):d} ft  {beam_in:d} in" if beam_ft is not None else "–"
            draft_display = f"{int(draft_ft):d} ft  {draft_in:d} in" if draft_ft is not None else "–"

        # basic info
        st.markdown("**Basic info**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.caption("Displacement type")
            st.write(row.get("displacement_type", "–"))
        with col_b2:
            st.caption("Material")
            st.write(row.get("material", "–"))
        with col_b3:
            st.caption("Gross tonnage")
            gt_val = row.get("gross_tonnage")
            st.write(f"{gt_val:.0f} GT" if pd.notna(gt_val) else "–")

        st.markdown("---")

        # dimensions
        st.markdown("**Dimensions**")
        area_display = f"{area_m2:.0f} m²" if pd.notna(area_m2) else "–"
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.caption("Length (LOA)")
            st.write(loa_display)
        with col_d2:
            st.caption("Beam (max)")
            st.write(beam_display)
        with col_d3:
            st.caption("Draft (full load)")
            st.write(draft_display)
        with col_d4:
            st.caption("Area")
            st.write(area_display)

        st.markdown("---")

        # performance & capacities
        st.markdown("**Performance & capacities**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.caption("Performance (cruise / max / range)")
            cs = safe_get(row, "cruise_speed_kn")
            ms = safe_get(row, "max_speed_kn")
            rg = safe_get(row, "range_nm")
            st.write(format_perf(cs, ms, rg))

        with col_p2:
            st.caption("Capacities (fuel / fresh / waste / urea)")
            f = safe_get(row, "fuel_oil")
            fw = safe_get(row, "fresh_water")
            ww = safe_get(row, "waste_water")
            u = safe_get(row, "urea")
            st.write(format_caps(f, fw, ww, u))

        st.markdown("---")

        # accommodation
        st.markdown("**Accommodation**")
        gc = safe_get(row, "guest_cabins_std")
        gb = safe_get(row, "guest_beds_std")
        gbath = safe_get(row, "guest_bathrooms_std")
        cr = safe_get(row, "crew")
        gc_s = gc if gc is not None else "–"
        gb_s = gb if gb is not None else "–"
        gbath_s = gbath if gbath is not None else "–"
        cr_s = cr if cr is not None else "–"
        st.caption("Guest cabins / beds / baths / crew")
        st.write(f"{gc_s} / {gb_s} / {gbath_s} / {cr_s}")

        st.markdown("---")

        # machinery
        st.markdown("**Machinery**")
        st.write(f"Engine: {safe_get(row, 'engine') or '–'}")
        st.write(f"Propulsion: {safe_get(row, 'propulsion') or '–'}")
        st.write(f"Generators: {safe_get(row, 'generators') or '–'}")
        st.write(f"Bow thruster: {safe_get(row, 'bow_thr') or '–'}")
        st.write(f"Stabilizers: {safe_get(row, 'stabilizers') or '–'}")
        st.write(f"Consumption (est.): {safe_get(row, 'consumption') or '–'}")

        st.markdown("---")

        # toys & notes
        st.markdown("**Toys & Notes**")
        js = safe_get(row, "jet_ski")
        tl = safe_get(row, "tender_length")
        js_txt = f"Jet ski: {js}" if js is not None else "Jet ski: –"
        tl_txt = (
            f"Tender length: {tl:.1f} m"
            if tl is not None and not pd.isna(tl)
            else "Tender length: –"
        )
        st.write(js_txt)
        st.write(tl_txt)
        notes = safe_get(row, "notes")
        notex_txt = f"Notes: {notes}" if pd.notna(notes) else "Notes:  –––"
        st.write(notex_txt)

    col_left, col_right = st.columns(2)
    with col_left:
        detail_block(yacht_a_name, row_a)
    with col_right:
        detail_block(yacht_b_name, row_b)

    
    # --- Visual comparison bar chart -----------------------------------------
    # Not sure if this is needed with the full specs above, but leaving it for now
    # mayber useful for quick visual, or could improve later
    st.markdown("---")
    st.markdown("#### Visual comparison")

    metric_options = {
        "Base price (M€)": "base_price",
        f"Length (LOA) [{length_label}]": "loa_metric",
        f"Beam [{length_label}]": "beam_metric",
        "Area (m²)": "area",
        "Gross Tonnage": "gross_tonnage",
        "Range (nm)": "range_nm",
        "Cruise speed (kn)": "cruise_speed_kn",
        "Max speed (kn)": "max_speed_kn",
    }
    selected_metric_label = st.selectbox(
        "Select metric for bar chart",
        list(metric_options.keys()),
    )
    selected_metric_col = metric_options[selected_metric_label]

    if selected_metric_col not in comp_df.columns:
        st.info("Selected metric not available in dataset.")
    else:
        va = safe_get(row_a, selected_metric_col)
        vb = safe_get(row_b, selected_metric_col)
        bar_df = pd.DataFrame(
            [
                {"yacht": yacht_a_name, "value": va},
                {"yacht": yacht_b_name, "value": vb},
            ]
        ).dropna(subset=["value"])

        if not bar_df.empty:
            chart = (
                alt.Chart(bar_df)
                .mark_bar()
                .encode(
                    y=alt.Y("yacht:N", title="Yacht"),
                    x=alt.X("value:Q", title=selected_metric_label),
                    color=alt.Color("yacht:N", title="Yacht"),
                    tooltip=[
                        "yacht",
                        alt.Tooltip("value:Q", title=selected_metric_label, format=".2f"),
                    ],
                )
                .properties(height=400,
                            width=600,)
            )
            st.altair_chart(chart, use_container_width=False)

