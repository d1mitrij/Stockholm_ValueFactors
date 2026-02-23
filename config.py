"""
config.py — EPS Value Factors configuration.

Mirrors the structure of the WifOR Value Factors config.py so that
indicator scripts, pipeline functions, and the parallel runner share
one consistent source of truth.

Key parallels with transitionvaluation/WifOR-Value-Factors
──────────────────────────────────────────────────────────
  WifOR COMMON_PATHS     → COMMON_PATHS  (source XLSX path)
  WifOR COMMON_PARAMS    → COMMON_PARAMS (year range, inflation params)
  WifOR INDICATORS dict  → INDICATORS    (one entry per EPS sheet/category)
  WifOR get_years()      → get_years()   (same 19-element year array)
  WifOR get_indicator_config(key) → get_indicator_config(key)
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent

COMMON_PATHS = {
    # EPS 2015 source XLSX (both variants available)
    "eps_xlsx_with_secondary": ROOT_DIR / (
        "2015_4a-EPS-2015d.1-Including-climate-impacts-from-secondary-particles (1).xlsx"
    ),
    "eps_xlsx_without_secondary": ROOT_DIR / "old" / (
        "2015_4b-EPS-2015dx.1-excluding-climate-impacts-from-secondary-particles-1.xlsx"
    ),
    "output_dir": Path(__file__).parent / "output",
}

# ── Countries ──────────────────────────────────────────────────────────────────
# ISO 3166-1 alpha-3 country codes.
# EPS 2015 characterisation factors are globally uniform (no country variation
# in the base dataset), so D[i] is broadcast identically across all countries.
# This list is kept consistent with the 188-country WifOR owntable convention.
COUNTRIES = [
    "AFG","AGO","ALB","ARE","ARG","ARM","ATG","AUS","AUT","AZE",
    "BDI","BEL","BEN","BFA","BGD","BGR","BHR","BHS","BIH","BLR",
    "BLZ","BOL","BRA","BRB","BRN","BTN","BWA","CAF","CAN","CHE",
    "CHL","CHN","CIV","CMR","COD","COG","COL","COM","CPV","CRI",
    "CUB","CYP","CZE","DEU","DJI","DNK","DOM","DZA","ECU","EGY",
    "ERI","ESP","EST","ETH","FIN","FJI","FRA","FSM","GAB","GBR",
    "GEO","GHA","GIN","GMB","GNB","GNQ","GRC","GRD","GTM","GUY",
    "HND","HRV","HTI","HUN","IDN","IND","IRL","IRN","IRQ","ISL",
    "ISR","ITA","JAM","JOR","JPN","KAZ","KEN","KGZ","KHM","KIR",
    "KNA","KOR","KWT","LAO","LBN","LBR","LBY","LCA","LKA","LSO",
    "LTU","LUX","LVA","MAR","MDA","MDG","MDV","MEX","MHL","MKD",
    "MLI","MLT","MMR","MNE","MNG","MOZ","MRT","MUS","MWI","MYS",
    "NAM","NER","NGA","NIC","NLD","NOR","NPL","NRU","NZL","OMN",
    "PAK","PAN","PER","PHL","PLW","PNG","POL","PRT","PRY","PSE",
    "QAT","ROU","RUS","RWA","SAU","SDN","SEN","SGP","SLB","SLE",
    "SLV","SMR","SOM","SRB","SSD","STP","SUR","SVK","SVN","SWE",
    "SWZ","SYC","SYR","TCD","TGO","THA","TJK","TKM","TLS","TON",
    "TTO","TUN","TUR","TUV","TZA","UGA","UKR","URY","USA","UZB",
    "VCT","VEN","VNM","VUT","WSM","YEM","ZAF","ZMB","ZWE",
]

# ── NACE sectors (A21 macro-classification) ────────────────────────────────────
# EPS has no sector differentiation; all sectors receive the same coefficient.
# Using A21 keeps the output compatible with MRIO/EORA26-style analysis.
NACE_SECTORS = [
    "A",            # Agriculture, forestry and fishing
    "B",            # Mining and quarrying
    "C10-C12",      # Food, beverages, tobacco
    "C13-C15",      # Textiles, wearing apparel, leather
    "C16-C18",      # Wood, paper, printing
    "C19",          # Coke and refined petroleum products
    "C20-C21",      # Chemicals and pharmaceuticals
    "C22-C23",      # Rubber, plastics, non-metallic minerals
    "C24-C25",      # Basic metals and fabricated metal products
    "C26-C28",      # Electronics, machinery
    "C29-C30",      # Motor vehicles, other transport
    "C31-C33",      # Furniture and other manufacturing
    "D",            # Electricity, gas, steam and air conditioning
    "E",            # Water supply, sewerage, waste
    "F",            # Construction
    "G-I",          # Trade, transport, accommodation, food services
    "J",            # Information and communication
    "K",            # Financial and insurance activities
    "L",            # Real estate activities
    "M-N",          # Professional, scientific, administrative services
    "O-U",          # Public administration, education, health, other
]

# ── Year series ────────────────────────────────────────────────────────────────
def get_years() -> list[str]:
    """
    Return the standard 19-element year series used across all indicator scripts.

    Matches the WifOR transitionvaluation convention:
      annual: 2014 – 2030  (17 years)
      + 2050, 2100         (2 long-horizon years)
    """
    annual = list(np.arange(2014, 2031, dtype=int).astype(str))
    return annual + ["2050", "2100"]


# ── EU HICP deflator (European Commission, base = 2015 = 100.0) ───────────────
# Source: Eurostat nama_10_gdp (GDP deflator, EU27)
# EPS 2015 values are denominated in EUR at 2015 price levels.
# Forecast years (2024–2100) are frozen at the last known value (2023).
# Format: {year_str: deflator_index}
EU_DEFLATOR_2015BASE = {
    "2014": 98.6, "2015": 100.0, "2016": 101.0, "2017": 102.5,
    "2018": 104.6, "2019": 106.3, "2020": 106.9, "2021": 109.4,
    "2022": 117.3, "2023": 124.1,
}
EU_DEFLATOR_BASE_YEAR = "2015"          # EPS reference year
EU_DEFLATOR_LAST_KNOWN_YEAR = "2023"    # freeze forecast years at this value

# ── Indicators ─────────────────────────────────────────────────────────────────
# One entry per EPS 2015 worksheet that contains substance-level EPS indices.
#
# Parallel to WifOR INDICATORS dict:
#   coefficient_sign  →  -1.0 damages, +1.0 benefits  (same convention as WifOR)
#   data_year         →  "2015"  (EPS base year, all coefficients in 2015 EUR)
#   unit_base         →  native ELU/[unit] for this category
#   sheet_name        →  exact XLSX worksheet name
#   eps_col_hint      →  column keyword to locate EPS-index column (passed to parser)
INDICATORS = {
    "inorganic_gases": {
        "sheet_name":       "8. Inorganic gases",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Inorganic gas emissions to air (CO2, CO, NOx, SO2, H2S, NH3, …)",
        "script_id":        "001",
    },
    "particles": {
        "sheet_name":       "9. Particles",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Particulate matter and heavy metals to air (PM2.5, PM10, As, Cd, Pb, …)",
        "script_id":        "002",
    },
    "voc": {
        "sheet_name":       "10. VOC",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Volatile organic compound emissions to air",
        "script_id":        "003",
    },
    "halogenated_organics": {
        "sheet_name":       "11. Halo. org.",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Halogenated organic compounds (CFCs, HCFCs, HFCs, …)",
        "script_id":        "004",
    },
    "emissions_to_water": {
        "sheet_name":       "7. Em to water",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Substance emissions to freshwater and seawater",
        "script_id":        "005",
    },
    "pesticides": {
        "sheet_name":       "12. Pesticides",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Pesticide active substance emissions (~200 substances)",
        "script_id":        "006",
    },
    "noise": {
        "sheet_name":       "13. Noise",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/W",
        "description":      "Road traffic noise (relative power of noise)",
        "script_id":        "007",
    },
    "radionuclides": {
        "sheet_name":       "14. Radionuclids",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/TBq",
        "description":      "Radioactive emissions to air from nuclear fuel cycle",
        "script_id":        "008",
    },
    "land_use": {
        "sheet_name":       "15. Land use",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/m2yr",
        "description":      "Land use (transformation and occupation)",
        "script_id":        "009",
    },
    "fossil_resources": {
        "sheet_name":       "3. Fossil res",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Fossil resource extraction (oil, coal, lignite, natural gas)",
        "script_id":        "010",
    },
    "other_elements": {
        "sheet_name":       "6. Other elements",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/kg",
        "description":      "Mineral and metal element extraction (Ag, Au, Cu, Fe, …)",
        "script_id":        "011",
    },
    "waste": {
        "sheet_name":       "16. waste",
        "coefficient_sign": -1.0,
        "data_year":        "2015",
        "unit_base":        "ELU/unit",
        "description":      "Waste littering to ground and water",
        "script_id":        "012",
    },
}

# ── Common parameters ──────────────────────────────────────────────────────────
COMMON_PARAMS = {
    # DataFrame MultiIndex level names (same as WifOR)
    "row_index_names":  ["Year", "Variable"],
    "col_index_names":  ["GeoRegion", "NACE"],

    # Coefficient naming template:  EPS_{category}_{substance}, in {unit} (Steen2015)
    "variable_template": "EPS_{category}_{substance}, in {unit} (Steen2015)",

    # HDF5 key names (mirrors WifOR)
    "hdf5_coeff_key": "coefficient",
    "hdf5_unit_key":  "unit",

    # Excel sheet names (mirrors WifOR)
    "excel_sheet_coefficients": "Coefficients",
    "excel_sheet_units":        "Units",
    "excel_freeze_coefficients": (1, 2),
    "excel_freeze_units":        (1, 1),

    # Inflation reference country (mirrors WifOR; here we use EU-wide deflator)
    "inflation_reference": "EU",

    # EPS source reference
    "source_reference": "Steen (2015) EPS 2015d.1, Swedish Life Cycle Center",
}


# ── Public helpers ─────────────────────────────────────────────────────────────

def get_indicator_config(key: str) -> dict:
    """
    Return a merged flat config dict for one indicator.

    Mirrors WifOR's ``get_indicator_config()`` signature.
    The returned dict contains all keys from INDICATORS[key],
    COMMON_PARAMS, COMMON_PATHS, plus computed output paths and
    the full year list.
    """
    if key not in INDICATORS:
        raise KeyError(f"Unknown indicator '{key}'. Valid keys: {list(INDICATORS)}")

    years = get_years()
    out_dir = COMMON_PATHS["output_dir"]
    script_id = INDICATORS[key]["script_id"]

    return {
        **INDICATORS[key],
        **COMMON_PARAMS,
        **{k: str(v) for k, v in COMMON_PATHS.items()},
        "years":    years,
        "countries": COUNTRIES,
        "nace":     NACE_SECTORS,
        "hdf5_path":  str(out_dir / f"{script_id}_eps_{key}.h5"),
        "excel_path": str(out_dir / f"{script_id}_eps_{key}.xlsx"),
    }


def list_indicators() -> list[tuple[str, str, str]]:
    """Return (key, script_id, description) tuples for all indicators."""
    return [
        (k, v["script_id"], v["description"])
        for k, v in INDICATORS.items()
    ]
