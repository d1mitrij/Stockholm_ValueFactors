# Algorithms and Pipeline Visualisation — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as transitionvaluation-compatible coefficient matrices**

---

## 1. End-to-End Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EPS Value Factors Pipeline                       │
└─────────────────────────────────────────────────────────────────────┘

  SOURCE                  STAGE                     OUTPUT
  ──────                  ─────                     ──────

  config.py          ─→  [1] CONFIGURATION      ─→  cfg dict
  INDICATORS dict         get_indicator_config()     years, sign, unit,
                                                     countries, nace

  EPS 2015d.1 XLSX   ─→  [2] DATA LOADING       ─→  pathway_df
  (one sheet)             load_eps_sheet()           substance_df
                          ├── generic parser          EPS_index[s]
                          └── special parsers
                              (fossil, radio,
                               waste)

  substance_df       ─→  [3] COEFFICIENT MATRIX  ─→  coeff DataFrame
  sign, years,            create_coeff_df()           shape:
  countries, nace         populate_coefficients()      (N_yr×N_sub)
                                                       × (189×21)

  EU HICP deflator   ─→  [4] INFLATION ADJUST    ─→  coeff_final
  2015 = 100.0            calculate_inflation()        C[y,s,c,n]
                          apply_deflation()

  coeff_final        ─→  [5] OUTPUT EXPORT       ─→  NNN_eps_{key}.h5
  units                   save_results()              NNN_eps_{key}.xlsx
  pathway_df              ├── HDF5 (full matrix)
                          └── Excel (50-col view)
```

---

## 2. Stage 2 — Data Loading Detail

### 2a. Generic Parser Flow

```
  load_eps_sheet(xlsx_path, sheet_name)
        │
        ├─── [dispatch] sheet_name ∈ _SPECIAL_SHEET_LOADERS?
        │         YES → call special parser → return (pathway_df, substance_df)
        │         NO  ↓
        │
        ├─── [scan] find header row
        │         _is_header_row(row) checks col 0 for keywords:
        │         "substance", "emission", "element", "flow group", …
        │
        ├─── [locate] find EPS index column
        │         Two-pass _find_col():
        │         ① HIGH: "eps", "default index", "elu/", "weighting factor"
        │         ② FALLBACK: "damage cost"  (only if no HIGH match)
        │
        ├─── [walk] data rows (header_idx + 1 onwards)
        │         • empty rows skipped
        │         • col 0 non-empty, non-summary → update current_substance
        │         • append {substance, indicator, unit, pathway,
        │                    extent_mean, contribution_mean, damage_cost_eur,
        │                    eps_index_source}
        │
        ├─── [derive] EPS index from pathway sums
        │         pathway_rows = rows where indicator ∉ {"all","total","sum"}
        │         derived[s] = Σ pathway_rows[s]["damage_cost_eur"]
        │
        ├─── [extract] source EPS from "all/all" summary rows
        │         source[s] = eps_index_source from first summary row per substance
        │
        ├─── [validate] |derived - source| / source < 0.1%
        │         violations → logger.warning
        │
        └─── [combine] eps_index = derived.combine_first(source)
                   → return (pathway_df, substance_df)
```

### 2b. Special Parser Dispatch

```
  _SPECIAL_SHEET_LOADERS = {
      "3. Fossil res":    _load_fossil_resources,   # hard-coded rows
      "14. Radionuclids": _load_radionuclides,       # fixed damage-cost column
      "16. waste":        _load_waste,               # 2 rows at known positions
  }
```

#### `_load_fossil_resources` — positions

```
  raw_rows[14][4]  → Fossil oil    (EUR/kg)
  raw_rows[43][4]  → Fossil coal   (EUR/kg, external + internal)
  raw_rows[46][4]  → Lignite       (EUR/kg)
  raw_rows[59][4]  → Natural gas   (EUR/kg CH4)
```

#### `_load_radionuclides` — column 6 scan

```
  raw_rows[0]   section title   (skipped)
  raw_rows[1]   header          (skipped)
  raw_rows[2]   unit row        (skipped)
  raw_rows[3:]  data rows:
                  col 0 → nuclide name
                  col 6 → damage cost EUR/TBq
                  stop at row where col 0 contains "emission" (water section)
```

#### `_load_waste` — two fixed rows

```
  raw_rows[6][9]  → Litter to ground         (EUR/item)
  raw_rows[7][9]  → Plastic litter to water  (EUR/kg)
```

---

## 3. Stage 3 — Coefficient Matrix Construction

### 3a. Matrix shape

```
  N_sub   = number of substances extracted from sheet
  N_yr    = 19  (years 2014–2030 annual + 2050, 2100)
  N_cty   = 189 (ISO3 country codes)
  N_nace  = 21  (NACE A21 sectors)

  Row MultiIndex:    (Year, Variable)      shape: N_yr × N_sub
  Column MultiIndex: (GeoRegion, NACE)     shape: N_cty × N_nace

  Total rows:    19 × N_sub
  Total columns: 189 × 21 = 3,969
```

### 3b. `create_coefficient_dataframe` — structure

```
                      AFG            …      ZWE
                   A  B  C10-C12  …     A  B  C10-C12  …
  (Year, Variable)
  ("2014", v₁)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]   ← initialised to sign
  ("2014", v₂)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]
  …
  ("2100", vₙ)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]
```

### 3c. `populate_coefficients` — vectorised fill

```
  d_values = sign × substance_df["eps_index"].values   # shape (N_sub,)

  arr = coeff.to_numpy(copy=False)                     # numpy view

  for i_year in 0..N_yr-1:
      row_start = i_year * N_sub
      row_end   = row_start + N_sub
      arr[row_start:row_end, :] = d_values[:, np.newaxis]
      #   ─────────────────────   ────────────────────────
      #   (N_sub, N_col) slice    broadcast (N_sub,1) → (N_sub, N_col)
```

After this step, each row holds the substance-specific EPS damage cost,
identical across all country-sector columns.

---

## 4. Stage 4 — Inflation Adjustment

### 4a. Inflation factors

```
  EU HICP deflator (GDP, EU27, base 2015 = 100.0):

  Year  Index   I[y]
  2014   98.6  0.9860
  2015  100.0  1.0000
  2016  101.0  1.0100
  2017  102.5  1.0250
  2018  104.6  1.0460
  2019  106.3  1.0630
  2020  106.9  1.0690
  2021  109.4  1.0940
  2022  117.3  1.1730
  2023  124.1  1.2410
  2024+ 124.1  1.2410  ← frozen at last known value
  …
  2100  124.1  1.2410
```

### 4b. `apply_deflation` — broadcast multiply

```
  N_sub = len(variables)

  # Build column vector of per-row inflation factors
  i_col = np.repeat(
      [I[y] for y in years],   # length N_yr, each repeated N_sub times
      N_sub,
  ).reshape(-1, 1)              # shape (N_yr × N_sub, 1)

  arr *= i_col
  # ─────────────────────────────────────────────────────────────────
  # (N_yr×N_sub, N_col) *= (N_yr×N_sub, 1)  →  broadcast over columns
  # ─────────────────────────────────────────────────────────────────
```

After this step:
```
  C[y, s, c, n] = sign × EPS_index[s] × I[y]
```

This is the final coefficient value — uniform across all (GeoRegion, NACE)
pairs for a given (Year, substance) row.

---

## 5. Stage 5 — Output Export

### 5a. HDF5 structure (full matrix)

```
  NNN_eps_{indicator}.h5
  ├── "coefficient"   DataFrame (N_yr×N_sub, N_cty×N_nace)
  │     Row MultiIndex:    [Year, Variable]
  │     Col MultiIndex:    [GeoRegion, NACE]
  │     dtype: float64
  │     compression: blosc, level 4
  │
  └── "unit"          DataFrame (N_sub, N_yr)
        index:   Variable name strings
        columns: year strings
        values:  "{y}ELU/{unit}"  or  "2023ELU/{unit}" (forecast)
```

### 5b. Excel structure (50-column view)

```
  NNN_eps_{indicator}.xlsx
  ├── "Coefficients"   (N_yr×N_sub rows) × (50 GeoRegion×NACE cols)
  │     freeze_panes: (1, 2)
  │     note: full data in .h5
  │
  ├── "Notes"          Truncation notice if cols were capped
  │
  ├── "Units"          N_sub rows × N_yr columns
  │     freeze_panes: (1, 1)
  │
  └── "Pathway data"  Full pathway_df (one row per substance×pathway)
                       index: integer
```

---

## 6. Parallel Runner Flow

```
  run_all_eps_factors.py
        │
        ├─── [discover] glob indicators/*.py  →  sorted list of scripts
        │
        ├─── [filter]   --only KEY [KEY ...]   (optional subset)
        │
        └─── [execute]  ThreadPoolExecutor(max_workers=N)
                  │
                  ├── pool.submit(run_one, script_001) ─→ Future₁
                  ├── pool.submit(run_one, script_002) ─→ Future₂
                  ├── …
                  └── pool.submit(run_one, script_012) ─→ Future₁₂

                  run_one(script):
                      result = subprocess.run(
                          ["python", script],
                          capture_output=True, timeout=600
                      )
                      record timing, stdout, stderr

        └─── [log] timestamped execution_log_{datetime}.txt
                   [OK] indicator   time   script
                   [FAIL] …         time   reason
                   Total: N/12 succeeded, wall-clock ≈ Xs
```

---

## 7. Per-Indicator Summary

| ID | Key | Substances | Parser | Notable features |
|----|-----|-----------|--------|-----------------|
| 001 | inorganic_gases | 16 | generic | Climate-critical: CO2, CH4, N2O, SO2, NOx, NH3 |
| 002 | particles | 14 | generic | Airborne PM fractions + heavy metals |
| 003 | voc | 144 | generic | Photochemical ozone formation pathways |
| 004 | halogenated_organics | 283 | generic | CFC/HCFC/HFC ozone depletion + GWP pathways |
| 005 | emissions_to_water | 14 | generic | Aquatic ecotoxicity + human health via water |
| 006 | pesticides | 302 | generic | Largest sheet; ecotox + human toxicity pathways |
| 007 | noise | 2 | generic | Functional unit: acoustic power (W) |
| 008 | radionuclides | 11 | special | YOLL + cancer via collective effective dose |
| 009 | land_use | 23 | generic | PDF·m²·yr biodiversity metric |
| 010 | fossil_resources | 4 | special | Scarcity cost; computation worksheet layout |
| 011 | other_elements | 77 | generic | Metals: ore grade depletion model |
| 012 | waste | 2 | special | Items and kg; visual + ecotox pathways |

---

## 8. Variable Name Format

```
  EPS_{CategorySlug}_{SubstanceSlug}, in {unit} (Steen2015)

  CategorySlug:  indicator_key.replace("_"," ").title().replace(" ","")
  SubstanceSlug: substance.replace(" ","_").replace(",","").replace("/","per")

  Examples:
    EPS_InorganicGases_CO2, in ELU/kg (Steen2015)
    EPS_Particles_PM2.5, in ELU/kg (Steen2015)
    EPS_Pesticides_2_4-D, in ELU/kg (Steen2015)
    EPS_Radionuclides_Kr-85, in ELU/TBq (Steen2015)
    EPS_Waste_Litter_to_ground, in ELU/unit (Steen2015)
```

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
