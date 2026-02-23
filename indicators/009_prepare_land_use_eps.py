"""
009_prepare_Landuse_eps.py — EPS Value Factor script: land_use

Land use: transformation and occupation by activity type

Pipeline
────────
  Stage 1  Configuration  config.get_indicator_config("land_use")
  Stage 2  Data Loading   pipeline.load_eps_sheet() → pathway_df, substance_df
  Stage 3  Coefficients   pipeline.create_coefficient_dataframe()
                          pipeline.populate_coefficients()
  Stage 4  Inflation      pipeline.calculate_inflation_factors()
                          pipeline.apply_deflation()
  Stage 5  Output         pipeline.save_results()

Outputs
───────
  output/009_eps_land_use.h5     HDF5: keys "coefficient" and "unit"
  output/009_eps_land_use.xlsx   Excel: sheets "Coefficients", "Units", "Pathway data"

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
    pipeline.run_indicator("land_use")
