import streamlit as st
import pandas as pd

from .config import M_TO_FT


def render_overview_tab(filtered: pd.DataFrame, length_unit: str) -> None:
    """
    Render the 'Overview' tab:
    - KPIs (count, avg price, avg LOA, avg GT)
    - Yacht detail view for a single selected yacht
    """
    # Create side cols + a main center column for data display
    col_left, col_main, col_right = st.columns([1, 3, 1])
    with col_main:
        st.markdown("### Overview (filtered)")

        # --- metrics -------------------------------------------
        n_yachts = len(filtered)

        avg_price = (
            float(filtered["base_price"].mean())
            if "base_price" in filtered.columns
            and not filtered["base_price"].isna().all()
            else None
        )
        avg_loa_m = (
            float(filtered["loa_metric"].mean())
            if "loa_metric" in filtered.columns
            and not filtered["loa_metric"].isna().all()
            else None
        )
        avg_gt = (
            float(filtered["gross_tonnage"].mean())
            if "gross_tonnage" in filtered.columns
            and not filtered["gross_tonnage"].isna().all()
            else None
        )

        # convert the length (LOA) metric to selected unit
        if avg_loa_m is not None:
            if length_unit == "m":
                avg_loa_display = avg_loa_m
                loa_label = "Avg LOA (m)"
            else:
                avg_loa_display = avg_loa_m * M_TO_FT
                loa_label = "Avg LOA (ft)"
        else:
            avg_loa_display = None
            loa_label = "Avg LOA"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Yachts", n_yachts)
        c2.metric(
            "Avg base price (M€)",
            f"{avg_price:.2f}" if avg_price is not None else "–",
        )
        c3.metric(
            loa_label,
            f"{avg_loa_display:.1f}" if avg_loa_display is not None else "–",
        )
        c4.metric(
            "Avg GT",
            f"{avg_gt:.0f}" if avg_gt is not None else "–",
        )

        st.markdown("---")
        st.markdown("### Yacht detail view")

        # --- check if: no yachts ---------------------------------------------------
        if len(filtered) == 0:
            st.info("No yachts available with current filters.")
            return

        # --- yacht selector -----------------------------------------------------
        yacht_names = (
            filtered["name"].dropna().unique().tolist()
            if "name" in filtered.columns
            else []
        )

        if not yacht_names:
            st.warning("No 'name' column found to select yachts.")
            return

        selected_yacht = st.selectbox("Select a yacht", yacht_names)

        yacht_row = filtered[filtered["name"] == selected_yacht].iloc[0]

        # --- Derived values for units -------------------------------------------
        loa_m = yacht_row.get("loa_metric")
        beam_m = yacht_row.get("beam_metric")
        draft_m = yacht_row.get("draft_full_load_metric")

        loa_ft = loa_m * M_TO_FT if pd.notna(loa_m) else None
        beam_ft = beam_m * M_TO_FT if pd.notna(beam_m) else None
        draft_ft = draft_m * M_TO_FT if pd.notna(draft_m) else None

        loa_in = int((loa_ft - int(loa_ft)) * 12) if pd.notna(loa_ft) else None
        beam_in = int((beam_ft - int(beam_ft)) * 12) if pd.notna(beam_ft) else None
        draft_in = int((draft_ft - int(draft_ft)) * 12) if pd.notna(draft_ft) else None

        if length_unit == "m":
            loa_display = f"{loa_m:.1f} m" if pd.notna(loa_m) else "–"
            beam_display = f"{beam_m:.1f} m" if pd.notna(beam_m) else "–"
            draft_display = f"{draft_m:.2f} m" if pd.notna(draft_m) else "–"
        else:
            loa_display = f"{int(loa_ft):d} ft  {loa_in:d} in" if loa_ft is not None else "–"
            beam_display = f"{int(beam_ft):d} ft  {beam_in:d} in" if beam_ft is not None else "–"
            draft_display = f"{int(draft_ft):d} ft  {draft_in:d} in" if draft_ft is not None else "–"

        # --- Layout: Basic info -------------------------------------------------
        st.markdown(f"#### {selected_yacht}")

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.caption("Displacement type")
            st.write(yacht_row.get("displacement_type", "–"))
        with col_b2:
            st.caption("Material")
            st.write(yacht_row.get("material") if pd.notna(yacht_row.get("material")) else "–")
        with col_b3:
            st.caption("Gross tonnage")
            gt_val = yacht_row.get("gross_tonnage")
            st.write(f"{gt_val:.0f} GT" if pd.notna(gt_val) else "–")

        st.caption("---")

        # --- Dimensions ---------------------------------------------------------
        st.markdown("**Dimensions**")
        area_m2 = yacht_row.get("area")
        area_display = f"{area_m2:.0f} m²" if pd.notna(area_m2) else "–"

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.caption("LOA")
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

        st.caption("---")

        # --- Performance ------------------------------------------------
        st.markdown("**Performance**")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.caption("Cruise speed")
            cs = yacht_row.get("cruise_speed_kn")
            st.write(f"{cs:.1f} kn" if pd.notna(cs) else "–")
        with col_p2:
            st.caption("Max speed")
            ms = yacht_row.get("max_speed_kn")
            st.write(f"{ms:.1f} kn" if pd.notna(ms) else "–")
        with col_p3:
            st.caption("Range")
            r = yacht_row.get("range_nm")
            st.write(f"{r:.0f} nm" if pd.notna(r) else "–")

        st.caption("---")

        # --- Capacities -------------------------------------------------------
        st.markdown("**Capacities**")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.caption("Fuel oil")
            f = yacht_row.get("fuel_oil")
            st.write(f"{f:.0f} L" if pd.notna(f) else "–")
        with col_c2:
            st.caption("Fresh water")
            fw = yacht_row.get("fresh_water")
            st.write(f"{fw:.0f} L" if pd.notna(fw) else "–")
        with col_c3:
            st.caption("Urea")
            u = yacht_row.get("urea")
            st.write(f"{u:.0f} L" if pd.notna(u) else "–")
        with col_c4:
            st.caption("Waste water")
            ww = yacht_row.get("waste_water")
            st.write(f"{ww:.0f} L" if pd.notna(ww) else "–")

        st.caption("---")

        # --- Accommodation ------------------------------------------------------
        st.markdown("**Accommodation**")
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            st.caption("Guest cabins (std.)")
            ac = yacht_row.get("guest_cabins_std")
            st.write(f"{ac:.0f}" if pd.notna(ac) else "–")
        with col_a2:
            st.caption("Guest beds (std.)")
            gbd = yacht_row.get("guest_beds_std")
            st.write(f"{gbd:.0f}" if pd.notna(gbd) else "–")
        with col_a3:
            st.caption("Guest bathrooms (std.)")
            gb = yacht_row.get("guest_bathrooms_std")
            st.write(f"{gb:.0f}" if pd.notna(gb) else "–")
        with col_a4:
            st.caption("Crew")
            cr = yacht_row.get("crew")
            st.write(f"{cr:.0f}" if pd.notna(cr) else "–")

        st.caption("---")

        # --- Machinery ----------------------------------------------------------

        st.markdown("**Machinery**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.caption("Engine")
            st.write(yacht_row.get("engine") if pd.notna(yacht_row.get("engine")) else "–")
            st.caption("Propulsion")
            st.write(yacht_row.get("propulsion") if pd.notna(yacht_row.get("propulsion")) else "–")
            st.caption("Generators")
            st.write(yacht_row.get("generators") if pd.notna(yacht_row.get("generators")) else "–")
        with col_m2:
            st.caption("Bow thruster")
            st.write(yacht_row.get("bow_thr") if pd.notna(yacht_row.get("bow_thr")) else "–")
            st.caption("Stabilizers")
            st.write(yacht_row.get("stabilizers") if pd.notna(yacht_row.get("stabilizers")) else "–")
            st.caption("Consumption (est.)")
            csp = yacht_row.get("consumption", "–")
            st.write(f"{csp:.0f} L/H" if pd.notna(csp) else "–")

        st.caption("---")

        # --- Toys & Notes -------------------------------------------------------
        st.markdown("**Toys & Notes**")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.caption("Jet ski (opt.)")
            st.write(f"{yacht_row.get("jet_ski"):.0f}" if pd.notna(yacht_row.get("jet_ski")) else "–")
            st.caption("Main tender length")
            tl = yacht_row.get("tender_length")
            st.write(f"{tl:.1f} m" if pd.notna(tl) else "–")
        with col_t2:
            st.caption("Notes")
            st.write(yacht_row.get("notes") if pd.notna(yacht_row.get("notes")) else "")
