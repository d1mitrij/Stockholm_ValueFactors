# Data Updates — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as transitionvaluation-compatible coefficient matrices**

---

## Overview

This document describes when and how to update the EPS Value Factors dataset.
Updates may arise from three sources:

1. **New EPS version** — a revised LCIA dataset published by the Swedish Life
   Cycle Center (e.g., EPS 2015d.2 or EPS 2020).
2. **Deflator update** — annual update to the EU HICP GDP deflator from Eurostat.
3. **Geography or sector update** — changes to the country list or NACE
   classification used by the transitionvaluation framework.

---

## 1. Updating the EU HICP Deflator

The EU GDP deflator (Eurostat `nama_10_gdp`, EU27) is updated annually,
typically in April for the preceding year.

### Source

```
Eurostat Data Browser
Dataset: nama_10_gdp
Unit:    Price index (implicit deflator), 2015 = 100
Filter:  NA_ITEM = B1GQ, GEO = EU27_2020, PRICES = PD15_EUR
```

### Procedure

1. Download the updated deflator series from Eurostat.

2. Edit `config.py`, section `EU_DEFLATOR_2015BASE`:

   ```python
   EU_DEFLATOR_2015BASE = {
       "2014": 98.6, "2015": 100.0, "2016": 101.0, "2017": 102.5,
       "2018": 104.6, "2019": 106.3, "2020": 106.9, "2021": 109.4,
       "2022": 117.3, "2023": 124.1,
       "2024": <new_value>,    # ← add new year
   }
   EU_DEFLATOR_LAST_KNOWN_YEAR = "2024"    # ← update this
   ```

3. Re-run all indicators:

   ```bash
   python run_all_eps_factors.py --max-workers 4
   ```

4. Verify the updated coefficient for CO2 in 2024:

   ```python
   import pandas as pd
   coeff = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="coefficient")
   co2_var = [v for v in coeff.index.get_level_values("Variable") if "CO2" in v][0]
   print(coeff.loc[("2024", co2_var)].iloc[0])
   # Expected: -0.1440 × (new_deflator / 100)
   ```

5. Check unit strings: the new year should show `"2024ELU/kg"` instead of
   `"2023ELU/kg"` for that year.

---

## 2. Adopting a New EPS Version

### Preparation

When the Swedish Life Cycle Center publishes a new EPS version:

1. Download the new XLSX and inspect its structure using Excel.
2. Check sheet names: do they match the names in `config.INDICATORS`?
3. Check column layout in each sheet: does the generic parser detect the
   EPS index column correctly?
4. Check for new substances or removed substances.

### File naming convention

Place the new XLSX in the project root and update `config.COMMON_PATHS`:

```python
COMMON_PATHS = {
    "eps_xlsx_with_secondary": ROOT_DIR / "EPS-2020-Including-secondary-particles.xlsx",
    "eps_xlsx_without_secondary": ROOT_DIR / "EPS-2020-Excluding-secondary-particles.xlsx",
    ...
}
```

Keep the old XLSX in place (rename to `old/`) for comparison.

### Sheet name changes

If worksheet names have changed, update the `sheet_name` entry in
`config.INDICATORS` for the affected indicators:

```python
INDICATORS = {
    "inorganic_gases": {
        "sheet_name": "8. Inorganic gases",    # ← update if renamed
        ...
    },
    ...
}
```

### New substances

New substances will be picked up automatically by the generic parser if they
appear in the standard tabular layout. Special parsers (`_load_fossil_resources`,
`_load_radionuclides`, `_load_waste`) must be updated manually if new rows
are added to those sheets.

### New indicators / categories

If a new EPS category is added (new worksheet):

1. Add an entry to `config.INDICATORS`:

   ```python
   "new_category": {
       "sheet_name":       "17. New category",
       "coefficient_sign": -1.0,
       "data_year":        "2020",
       "unit_base":        "ELU/kg",
       "description":      "Description of new category",
       "script_id":        "013",
   },
   ```

2. Create the indicator script `indicators/013_prepare_new_category_eps.py`:

   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   import pipeline

   if __name__ == "__main__":
       pipeline.run_indicator("new_category")
   ```

3. The parallel runner (`run_all_eps_factors.py`) discovers scripts by glob
   automatically — no changes needed.

### Validation after update

Run the full validation procedure from `VALIDATION_REPORT.md`:
- Compare new vs old substance counts.
- Compare CO2 and PM2.5 reference values.
- Check for new `WARNING` messages in the execution log.

---

## 3. Updating the Country List

The 189-country list in `config.COUNTRIES` follows the WifOR transitionvaluation
convention (ISO 3166-1 alpha-3 codes). Updates are required when:

- A country is added or removed from the WifOR framework.
- A country changes ISO3 code (e.g., country dissolution or unification).

### Procedure

1. Edit `config.COUNTRIES` — add or remove ISO3 codes.
2. Re-run all indicators. The new country list is applied automatically.
3. Notify the transitionvaluation maintainers if the change affects cross-project
   comparability.

**Note:** Because EPS characterisation factors are globally uniform
(D[s] does not vary by country), adding or removing a country from the list
does not change any coefficient *values* — it only changes the number of
columns in the output matrix.

---

## 4. Updating the NACE Sector Classification

The 21-sector A21 classification in `config.NACE_SECTORS` is the standard
for EORA26-style MRIO analysis. Updates are required if the transitionvaluation
framework adopts a different sector aggregation.

### Procedure

1. Edit `config.NACE_SECTORS` — add, remove, or rename sector codes.
2. Re-run all indicators.

**Note:** As with countries, EPS coefficients are uniform across sectors,
so this only affects the column structure, not the coefficient values.

---

## 5. Output File Versioning

Output files are not version-controlled (listed in `.gitignore`). If you need
to preserve a specific run for archival or comparison purposes:

```bash
# Archive current output
mkdir -p archive/2026-02-23
cp output/*.h5 archive/2026-02-23/
cp output/*.xlsx archive/2026-02-23/
cp execution_log_*.txt archive/2026-02-23/
echo "EPS 2015d.1 | EU deflator 2014–2023" > archive/2026-02-23/README.txt
```

---

## 6. Update Checklist

Use this checklist before pushing updated outputs:

- [ ] Source XLSX version confirmed (file name, date in Introduction sheet)
- [ ] `config.EU_DEFLATOR_2015BASE` updated with latest Eurostat values
- [ ] `EU_DEFLATOR_LAST_KNOWN_YEAR` updated
- [ ] All 12 indicators ran to completion (no `[FAIL]` in execution log)
- [ ] Total substance count: 892 (or documented if changed)
- [ ] CO2 2015 coefficient ≈ −0.144 ELU/kg (or documented if changed)
- [ ] Unit strings verified: `"{year}ELU/kg"` for known years, `"2023ELU/kg"` for frozen forecasts
- [ ] VALIDATION_REPORT.md reference values table updated if values changed
- [ ] METHODOLOGY.md updated if EPS version or monetary values changed

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
