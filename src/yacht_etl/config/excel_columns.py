# Map raw Excel column names -> internal names
EXCEL_COLUMN_MAP = {
    # Identification / pricing
    "Name": "name",
    "Base Price (2023)": "base_price_million_eur",
    "Price / m2": "price_m2",
    "Price/GT  (Euros/Gross Ton)": "price_gt",
    "Price/Ton  (Euros/Metric Ton)": "price_ton",

    # Dimensions (metric)
    "LOA": "loa_m",
    "LWL": "lwl_m",
    "Max beam": "beam_m",
    "Draft at full load": "draft_full_m",

    # Dimensions (imperial) – these were the “Unnamed: xx” columns
    "Unnamed: 14": "loa_ft",
    "Unnamed: 15": "loa_in",
    "Unnamed: 11": "lwl_ft",
    "Unnamed: 12": "lwl_in",
    "Unnamed: 17": "beam_ft",
    "Unnamed: 18": "beam_in",
    "Unnamed: 20": "draft_full_ft",
    "Unnamed: 21": "draft_full_in",

    # Area / material
    "Area": "area_m2",
    "Material": "material",

    # Weights / capacities
    "Full load Displacement": "displacement_t",
    "Gross tonnage": "gross_tonnage",
    "Fuel oil capacity": "fuel_oil_cap",
    "Urea": "urea_cap",
    "Fresh water capacity": "fresh_water_cap",
    "Waste water capacity": "waste_water_cap",

    # Performance
    "Range @ Speed": "range_nm_raw",
    "Cruise speed (80%)": "cruise_speed_kn_raw",
    "Max speed": "max_speed_kn_raw",

    # Machinery
    "Largest Engine": "engine_raw",
    "Consumption (Estimation)": "consumption_raw",
    "Propulsion": "propulsion_raw",
    "Generators (Recommended)": "generators_raw",
    "Bow thr.": "bow_thr_raw",
    "Stabilizers": "stabilizers_raw",

    # Accommodation
    "Guest cabins std": "guest_cabins_std_raw",
    "N. beds std": "guest_beds_std_raw",
    "N. guest bathr. std": "guest_bathrooms_std_raw",

    # Crew
    "Crew cabins": "crew_cabins_raw",
    "Crew Bathrooms": "crew_bathrooms_raw",
    "No. of Crew std": "crew_std_raw",

    # Toys / tenders / notes
    "N. Jet ski (OPT)": "jet_ski_raw",
    "Length\nMain Tender": "tender_length_m",
    "Notes": "notes_raw",
}

# For validation: which Excel columns MUST exist
REQUIRED_EXCEL_COLUMNS = list(EXCEL_COLUMN_MAP.keys())
