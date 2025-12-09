import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

from .config import M_TO_FT, COLOR_REG, COLOR_CHARTS, COLOR_LINES


def render_charts_tab(filtered: pd.DataFrame, length_unit: str) -> None:
    """
    Render the 'Charts' tab:
    - LOA vs base price scatter (with unit toggle)
    - LOA distribution histogram
    - Base price distribution histogram
    - Boxplot for selected key metric
    - Price vs gross tonnage scatter
    - Price per GT/Area ranking bar chart
    """
    st.markdown("### Charts")

    if filtered.empty:
        st.warning("No data to plot with current filters.")
        return

    # Make a copy so we can safely add derived columns
    chart_df = filtered.copy()
    
    # Ensure numeric types where expected
    for col in ["loa_metric", "base_price", "gross_tonnage",
                "beam_metric", "range_nm"]:
        if col in chart_df.columns:
            chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    # Add LOA in feet for convenience
    if "loa_metric" in chart_df.columns:
        chart_df["loa_ft"] = chart_df["loa_metric"] * M_TO_FT

    # ----------------------------------------------------------------------
    # 1) LOA vs base price scatter
    # ----------------------------------------------------------------------
    if "loa_metric" in chart_df.columns and "base_price" in chart_df.columns:
        if length_unit == "m":
            x_field = "loa_metric"
            x_title = "LOA (m)"
        else:
            x_field = "loa_ft"
            x_title = "LOA (ft)"

        scatter = (
            alt.Chart(chart_df.dropna(subset=[x_field, "base_price"]))
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X(x_field, title=x_title),
                y=alt.Y("base_price", title="Base price (M€)"),
                color=alt.Color("displacement_type", title="Displacement type"),
                tooltip=[
                    "name",
                    alt.Tooltip("loa_metric", title="LOA (m)", format=".1f"),
                    alt.Tooltip("loa_ft", title="LOA (ft)", format=".1f"),
                    alt.Tooltip("base_price", title="Base price (M€)", format=".2f"),
                    alt.Tooltip("gross_tonnage", title="GT", format=".0f"),
                ],
            )
            .interactive()
        )
        st.markdown("#### LOA vs base price")
        st.altair_chart(scatter, use_container_width=True)

    # ----------------------------------------------------------------------
    # 2) LOA distribution histogram
    # ----------------------------------------------------------------------
    if "loa_metric" in chart_df.columns:
        st.markdown("#### LOA distribution")

        if length_unit == "m":
            hist_loa_df = chart_df.dropna(subset=["loa_metric"])
            x_field = "loa_metric"
            x_title = "LOA (m)"
        else:
            hist_loa_df = chart_df.dropna(subset=["loa_ft"])
            x_field = "loa_ft"
            x_title = "LOA (ft)"

        if not hist_loa_df.empty:
            loa_hist = (
                alt.Chart(hist_loa_df)
                .mark_bar()
                .encode(
                    x=alt.X(
                        x_field,
                        bin=alt.Bin(maxbins=20),
                        title=x_title,
                    ),
                    y=alt.Y("count()", title="Count"),
                    color=alt.Color(
                        "displacement_type",
                        title="Displacement type",
                        legend=alt.Legend(title="Displacement"),
                    ),
                )
            )
            st.altair_chart(loa_hist, use_container_width=True)

    # ----------------------------------------------------------------------
    # 3) Base price distribution histogram
    # ----------------------------------------------------------------------
    if "base_price" in chart_df.columns:
        st.markdown("#### Base price distribution")

        price_hist = (
            alt.Chart(chart_df.dropna(subset=["base_price"]))
            .mark_bar()
            .encode(
                x=alt.X(
                    "base_price",
                    bin=alt.Bin(maxbins=20),
                    title="Base price (M€)",
                ),
                y=alt.Y("count()", title="Count"),
                color=alt.Color(
                    "displacement_type",
                    title="Displacement type",
                    legend=alt.Legend(title="Displacement"),
                ),
            )
        )
        st.altair_chart(price_hist, use_container_width=True)

    # ----------------------------------------------------------------------
    # 4) Boxplot for key metrics
    # ----------------------------------------------------------------------
    st.markdown("#### Boxplot for key metrics")

    metric_options = {
        "Base price (M€)": "base_price",
        "Gross tonnage": "gross_tonnage",
        "Beam (m)": "beam_metric",
        "Range (nm)": "range_nm",
        "Area (m²)" : "area",
    }

    if length_unit == "ft":
        metric_options = {
            "Base price (M€)": "base_price",
            "Gross tonnage": "gross_tonnage",
            "Beam (ft)": "beam_metric",
            "Range (nm)": "range_nm",
            "Area (m²)" : "area",
        }

    selected_metric_label = st.selectbox(
        "Select metric for boxplot",
        list(metric_options.keys()),
    )
    selected_metric_col = metric_options[selected_metric_label]

    if selected_metric_col in chart_df.columns:
        metric_series = pd.to_numeric(
            chart_df[selected_metric_col], errors="coerce"
        ).dropna()

        if not metric_series.empty:
            metric_values = metric_series.copy()
            metric_title = selected_metric_label

            if selected_metric_col == "beam_metric" and length_unit == "ft":
                metric_values = metric_values * M_TO_FT

            box_df = pd.DataFrame({"metric": metric_title, "value": metric_values})

            box_chart = (
                alt.Chart(box_df)
                .mark_boxplot()
                .encode(
                    y=alt.Y("metric:N", title="Metric"),
                    x=alt.X("value:Q", title="Value"),
                )
                .properties(
                    height=400,
                    width=600,
                )
            )

            st.altair_chart(box_chart, use_container_width=False)
        else:
            st.info("No data available for the selected metric.")
    else:
        st.info("Selected metric not available in dataset.")



    st.markdown("---")
    st.markdown("### Advanced Analytics")

    # ------------------------------------------------------------------
    # Choose volume metric for price & residual analysis (GT vs Area)
    # ------------------------------------------------------------------
    # Try to detect an "area" column (adjust candidate names if needed)
    area_col = None
    for cand in ["area_m2", "area", "area_total"]:
        if cand in chart_df.columns:
            area_col = cand
            break

    volume_metric_options: dict[str, tuple[str, str]] = {}

    if "gross_tonnage" in chart_df.columns:
        volume_metric_options["Gross tonnage (GT)"] = ("gross_tonnage", "GT")

    if area_col is not None:
        volume_metric_options["Area (m²)"] = (area_col, "m²")

    if volume_metric_options:
        selected_volume_label = st.selectbox(
            "Metric for price & residual analysis",
            list(volume_metric_options.keys()),
        )
        volume_col, volume_unit = volume_metric_options[selected_volume_label]
    else:
        selected_volume_label = None
        volume_col = None
        volume_unit = ""


    # ----------------------------------------------------------------------
    # 5) Price vs chosen volume metric (GT or Area) with polynomial regression
    # ----------------------------------------------------------------------
    if "base_price" in chart_df.columns and volume_col is not None:
        st.markdown(f"#### Price vs {selected_volume_label} (regression trendline)")

        vol_df = chart_df.dropna(subset=["base_price", volume_col]).copy()

        if not vol_df.empty:
            # Scatter
            scatter = (
                alt.Chart(vol_df)
                .mark_circle(size=70, opacity=0.75)
                .encode(
                    x=alt.X(
                        f"{volume_col}:Q",
                        title=selected_volume_label,
                    ),
                    y=alt.Y(
                        "base_price:Q",
                        title="Base price (M€)",
                    ),
                    color=alt.Color(
                        "displacement_type:N",
                        title="Displacement type",
                    ),
                    tooltip=[
                        "name",
                        alt.Tooltip(volume_col, title=selected_volume_label, format=".0f"),
                        alt.Tooltip("base_price", title="Price (M€)", format=".2f"),
                        alt.Tooltip("loa_metric", title="LOA (m)", format=".1f"),
                    ],
                )
            )

            # Polynomial regression line (order 2)
            # Requires at least 3 data points, else altair raises an error
            # here higher order polynomials seems to overfit too much
            # Not sure if the regression is really meaningful in this context, but it's illustrative
            poly_reg = (
                alt.Chart(vol_df)
                .transform_regression(
                    on=volume_col,
                    regression="base_price",
                    method="poly",
                    order=2,
                )
                .mark_line(color=COLOR_REG, size=3)
                .encode(
                    x=alt.X(f"{volume_col}:Q", title=selected_volume_label),
                    y=alt.Y("base_price:Q", title="Base price (M€)"),
                )
            )

            chart = (scatter + poly_reg).interactive()
            st.altair_chart(chart, use_container_width=True)

    # ----------------------------------------------------------------------
    # Price per volume metric (M€ / GT or M€ / m²) depending on dropdown
    # ----------------------------------------------------------------------
    if volume_col is not None:
        if volume_col == "gross_tonnage" and "price_gt" in chart_df.columns:
            st.markdown("#### Price per GT (M€ / GT)")

            value_col = "price_gt"
            title = "Price per GT (M€ / GT)"
        elif volume_col == area_col and "price_m2" in chart_df.columns:
            st.markdown("#### Price per Area (M€ / m²)")

            value_col = "price_m2"
            title = "Price per m² (M€ / m²)"
        else:
            st.info(
                "No price-per-volume metric available for the selected volume metric."
            )
            value_col = None

        if value_col is not None:
            ppm_df = chart_df.copy()
            ppm_df = ppm_df[
                ppm_df[value_col].notna() & (ppm_df[value_col] > 0)
            ].copy()

            if not ppm_df.empty:
                # Sort so best value (lowest price per unit) at top
                ppm_df = ppm_df.sort_values(value_col, ascending=True)

                # Slider to limit number of yachts displayed
                max_n_default = min(30, len(ppm_df))
                max_n_limit = min(100, len(ppm_df))

                # Check max bars to avoid app crash or errors
                if max_n_limit == 1:
                    max_bars = 1
                    st.warning("Only one Yacht displayed with current filters")
                else:
                    max_bars = st.slider(
                        "Max yachts to show (sorted by best value)",
                        min_value=1,
                        max_value=max_n_limit,
                        value=max_n_default,
                        step=1,
                        key="price_per_volume_max_bars",
                    )

                ppm_df = ppm_df.head(max_bars)

                bar_chart_ppv = (
                    alt.Chart(ppm_df)
                    .mark_bar()
                    .encode(
                        y=alt.Y(
                            "name:N",
                            sort="-x",
                            title="Yacht",
                        ),
                        x=alt.X(
                            f"{value_col}:Q",
                            title=title,
                            axis=alt.Axis(format=".3f"),
                        ),
                        color=alt.Color(
                            "displacement_type:N",
                            title="Displacement type",
                        ),
                        tooltip=[
                            "name",
                            alt.Tooltip(value_col, title=title, format=".3f"),
                            alt.Tooltip(
                                "base_price", title="Base price (M€)", format=".2f"
                            ),
                            alt.Tooltip(
                                volume_col,
                                title=selected_volume_label,
                                format=".0f",
                            ),
                        ],
                    )
                    .properties(
                        height=600,
                        width=700,
                    )
                )

                st.altair_chart(bar_chart_ppv, use_container_width=False)
            else:
                st.info("Not enough valid data to display price-per-volume metric.")



    # ----------------------------------------------------------------------
    # Residuals chart: actual price - residuals (value indicator)
    # with toggle between bar chart and scatter (using chosen metric)
    # ----------------------------------------------------------------------
    if "base_price" in chart_df.columns and volume_col is not None:
        st.markdown(f"#### Price residuals vs {selected_volume_label}")

        vol_df = chart_df.dropna(subset=["base_price", volume_col]).copy()

        # Need at least 3 points to fit a quadratic polynomial, same as before
        if len(vol_df) >= 3:
            x = np.asarray(vol_df[volume_col].astype(float).values, dtype=float)
            y = np.asarray(vol_df["base_price"].astype(float).values, dtype=float)

            # Fit polynomial: price ≈ a·X² + b·X + c
            coeffs = np.polyfit(x, y, deg=2)
            y_pred = np.polyval(coeffs, x)

            # Residuals: actual - predicted
            residuals = y - y_pred
            vol_df["residual"] = residuals

            # Choose view: bar chart or scatter
            view_mode = st.radio(
                "Residuals view",
                ["Bar chart (by yacht)", "Scatter (price vs residual)"],
                horizontal=True,
                key="residuals_view_mode",
            )

            if view_mode.startswith("Bar"):
                # Bar chart: sort by residual so "best value" (most negative) at top
                bar_df = vol_df.sort_values("residual", ascending=True).copy()

                max_rows = 40
                if len(bar_df) > max_rows:
                    bar_df = bar_df.head(max_rows)

                residual_chart = (
                    alt.Chart(bar_df)
                    .mark_bar()
                    .encode(
                        y=alt.Y(
                            "name:N",
                            sort="-x",  # sorted by residual
                            title="Yacht",
                        ),
                        x=alt.X(
                            "residual:Q",
                            title="Residual (M€)",
                            axis=alt.Axis(format=".2f"),
                        ),
                        color=alt.condition(
                            "datum.residual > 0",
                            alt.value(COLOR_CHARTS),   # red for overpriced
                            alt.value(COLOR_CHARTS),   # green for good value
                        ),
                        tooltip=[
                            "name",
                            alt.Tooltip("residual:Q", title="Residual (M€)", format=".2f"),
                            alt.Tooltip("base_price:Q", title="Price (M€)", format=".2f"),
                            alt.Tooltip(volume_col, title=selected_volume_label, format=".0f"),
                        ],
                    )
                    .properties(
                        height=600,
                        width=700,
                    )
                )

                st.altair_chart(residual_chart, use_container_width=False)

            else:
                # Scatter: x = price, y = residual
                scatter_df = vol_df.copy()

                zero_line = (
                    alt.Chart(pd.DataFrame({"residual": [0.0]}))
                    .mark_rule(strokeDash=[4, 4], color=COLOR_LINES)
                    .encode(y="residual:Q")
                )

                residual_scatter = (
                    alt.Chart(scatter_df)
                    .mark_circle(size=70, opacity=0.75)
                    .encode(
                        x=alt.X(
                            f"{volume_col}:Q",
                            title=selected_volume_label,
                        ),
                        y=alt.Y(
                            "residual:Q",
                            title="Residual (M€)",
                            axis=alt.Axis(format=".2f"),
                        ),
                        color=alt.Color(
                            "displacement_type:N",
                            title="Displacement type",
                        ),
                        tooltip=[
                            "name",
                            alt.Tooltip(
                                volume_col, title=selected_volume_label, format=".0f"
                            ),
                            alt.Tooltip(
                                "base_price:Q", title="Price (M€)", format=".2f"
                            ),
                            alt.Tooltip(
                                "residual:Q", title="Residual (M€)", format=".2f"
                            ),
                        ],
                    )
                    .properties(
                        height=400,
                        width=800,
                    )
                )


                st.altair_chart(
                    (zero_line + residual_scatter).interactive(),
                    use_container_width=False,
                )

        else:
            st.info("Not enough data points to fit a polynomial regression for residuals.")


