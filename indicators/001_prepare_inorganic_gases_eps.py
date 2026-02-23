"""
001_prepare_Inorganicgases_eps.py — EPS Value Factor script: inorganic_gases

Inorganic gas emissions to air (CO2, CO, NOx, SO2, H2S, NH3, HCl, HF, O3, …)

Pipeline
────────
  Stage 1  Configuration  config.get_indicator_config("inorganic_gases")
  Stage 2  Data Loading   pipeline.load_eps_sheet() → pathway_df, substance_df
  Stage 3  Coefficients   pipeline.create_coefficient_dataframe()
                          pipeline.populate_coefficients()
  Stage 4  Inflation      pipeline.calculate_inflation_factors()
                          pipeline.apply_deflation()
  Stage 5  Output         pipeline.save_results()

Outputs
───────
  output/001_eps_inorganic_gases.h5     HDF5: keys "coefficient" and "unit"
  output/001_eps_inorganic_gases.xlsx   Excel: sheets "Coefficients", "Units", "Pathway data"

Source
──────
  Steen, B. (2015). EPS 2015d.1. Swedish Life Cycle Center Report 2015:4a.
"""

import logging
import sys
from pathlib import Path

# ── Make sibling modules importable ──
sys.path.insert(0, str(Path(__file__).parent.parent))

import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s: %(message)s",
)

if __name__ == "__main__":
    pipeline.run_indicator("inorganic_gases")
