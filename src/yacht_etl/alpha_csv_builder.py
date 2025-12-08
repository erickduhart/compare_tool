import pandas as pd
from pathlib import Path
from typing import Union, BinaryIO, IO

from .utils.conversions import ft_in_to_ft
from .config.excel_columns import EXCEL_COLUMN_MAP, REQUIRED_EXCEL_COLUMNS

# build_master_csv: converts excel file to a  manageable csv
ExcelSource = Union[Path, str, BinaryIO, IO[bytes]]

def build_master_csv(
        template_path: Path,
        excel_source: ExcelSource,
        excel_sheet: Union[str, int],
        output_path: Path,
):


    # --- 1) Load template to get the target column order ---
    base_template = pd.read_csv(template_path)
    target_columns = base_template.columns

    # --- 2) Load Excel sheet with all the raw data ---
    # read from in-memory file-like object
    if isinstance(excel_source, (str, Path)):
        raw = pd.read_excel(
            excel_source,
            sheet_name=excel_sheet
        )
    else:
        try:
            excel_source.seek(0)
        except Exception:
            pass
        raw = pd.read_excel(
            excel_source,
            sheet_name=excel_sheet
        )


    # Validate required columns
    missing = [c for c in REQUIRED_EXCEL_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(
            f"Missing expected columns in Excel: {missing}. "
            f"Available columns: {list(raw.columns)}"
        )

    # Normalize column names to internal names
    raw = raw.rename(columns=EXCEL_COLUMN_MAP)
    # --- from here on, ONLY use internal names! ---
    # e.g., raw["name"], raw["base_price_million_eur"], raw["fuel_oil_cap"], etc.

    # --- 3) add displacement_type ---

    # Convert Name to string for safe string ops
    name_str = raw["name"].astype(str)

    # Any row whose Name contains "DISPLACEMENT" is treated as a section header
    mask_sections = name_str.str.contains("DISPLACEMENT", case=False, na=False)

    # Initialize column
    raw["displacement_type"] = pd.NA

    # Put the raw section text on those rows
    raw.loc[mask_sections, "displacement_type"] = name_str[mask_sections].str.strip()

    # Forward-fill so every yacht row gets its section type
    raw["displacement_type"] = raw["displacement_type"].ffill()

    # Normalize to two clean categories where possible
    def normalize_displacement_type(x):
        if pd.isna(x):
            return pd.NA
        s = str(x).upper()
        if "SEMI" in s:
            return "SEMI-DISPLACEMENT"
        elif "FULL" in s:
            return "FULL DISPLACEMENT"
        else:
            # In case some different type appears in the future
            return x

    raw["displacement_type"] = raw["displacement_type"].apply(normalize_displacement_type)



    # --- 4) Remove section rows and clean dataset ---

    # Drop the section-label rows themselves
    data = raw[~mask_sections].copy()

    # Remove the "Units" row
    data = data[data["name"] != "Units"]

    # Drop rows with missing Name
    data = data[~data["name"].isna()].copy()

    # --- 5) Build the final DataFrame in the template structure ---

    out = pd.DataFrame({
        # Identification / pricing
        "name": data["name"],
        # Base Price (2023) is in million €, convert to €
        # "base_price": pd.to_numeric(data["Base Price (2023)"], errors="coerce") * 1_000_000,
        "base_price": pd.to_numeric(data["base_price_million_eur"], errors="coerce"),
        "price_m2": round(pd.to_numeric(data["price_m2"], errors="coerce")),
        "price_gt": round(pd.to_numeric(data["price_gt"], errors="coerce")),
        "price_ton": round(pd.to_numeric(data["price_ton"], errors="coerce")),

        # Dimensions: LOA, LWL, beam, draft
        "loa_metric": pd.to_numeric(data["loa_m"], errors="coerce"),
        "loa_imperial": ft_in_to_ft(data["loa_ft"], data["loa_in"]),
        "lwl_metric": pd.to_numeric(data["lwl_m"], errors="coerce"),
        "lwl_imperial": ft_in_to_ft(data["lwl_ft"], data["lwl_in"]),
        "beam_metric": pd.to_numeric(data["beam_m"], errors="coerce"),
        "beam_imperial": ft_in_to_ft(data["beam_ft"], data["beam_in"]),
        "draft_full_load_metric": pd.to_numeric(data["draft_full_m"], errors="coerce"),
        "draft_full_load_imperial": ft_in_to_ft(data["draft_full_ft"], data["draft_full_in"]),

        # Area / material
        "area": pd.to_numeric(data["area_m2"], errors="coerce"),
        "material": data["material"],

        # Weights / capacities
        "full_load_displacement_t": pd.to_numeric(data["displacement_t"], errors="coerce"),
        "gross_tonnage": pd.to_numeric(data["gross_tonnage"], errors="coerce"),
        "fuel_oil": pd.to_numeric(data["fuel_oil_cap"], errors="coerce"),
        "urea": pd.to_numeric(data["urea_cap"], errors="coerce"),
        "fresh_water": pd.to_numeric(data["fresh_water_cap"], errors="coerce"),
        "waste_water": pd.to_numeric(data["waste_water_cap"], errors="coerce"),

        # Performance
        "range_nm": pd.to_numeric(data["range_nm_raw"], errors="coerce"),
        "cruise_speed_kn": pd.to_numeric(data["cruise_speed_kn_raw"], errors="coerce"),
        "max_speed_kn": pd.to_numeric(data["max_speed_kn_raw"], errors="coerce"),

        # Machinery
        "engine": data["engine_raw"],
        "consumption": round(pd.to_numeric(data["consumption_raw"], errors='coerce')),
        "propulsion": data["propulsion_raw"],
        "generators": data["generators_raw"],
        "bow_thr": data["bow_thr_raw"],
        "stabilizers": data["stabilizers_raw"],

        # Accommodation
        "guest_cabins_std": pd.to_numeric(data["guest_cabins_std_raw"], errors="coerce"),
        "guest_beds_std": pd.to_numeric(data["guest_beds_std_raw"], errors="coerce"),
        "guest_bathrooms_std": pd.to_numeric(data["guest_bathrooms_std_raw"], errors="coerce"),

        # Crew
        "crew_cabins": pd.to_numeric(data["crew_cabins_raw"], errors="coerce"),
        "crew_bathrooms": pd.to_numeric(data["crew_bathrooms_raw"], errors="coerce"),
        "crew": pd.to_numeric(data["crew_std_raw"], errors="coerce"),

        # Toys / tenders / displacement type/ notes
        "jet_ski": pd.to_numeric(data["jet_ski_raw"], errors="coerce"),
        "tender_length": pd.to_numeric(data["tender_length_m"], errors="coerce"),
        "displacement_type": data["displacement_type"],
        "notes": data["notes_raw"],
    })

    # Ensure exact column order as in base_yacht_master.csv
    out = out[target_columns]

    # dataframe cleaning and corrections
    out['engine'] = out['engine'].apply(
        lambda x: None if isinstance(x, str) and len(x) < 4 else x
    )
    out['generators'] = out['generators'].apply(
        lambda x: None if isinstance(x, str) and len(x) < 4 else x
    )
    out['bow_thr'] = out['bow_thr'].apply(
        lambda x: None if isinstance(x, str) and len(x) < 4 else x
    )
    out['stabilizers'] = out['stabilizers'].apply(
        lambda x: None if isinstance(x, str) and len(x) < 4 else x
    )

            

    # --- 5) Save the result to a new CSV ---
    out.to_csv(output_path, index=False)

    print(f"Saved transformed dataset to: {output_path}")
    print(f"Rows: {len(out)}, Columns: {len(out.columns)}")
    return out