# Validation Report — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as structured coefficient matrices**

---

## Summary

All 12 indicator scripts executed successfully. The pipeline produced 12 HDF5
files and 12 Excel files in `output/`. EPS indices re-derived from pathway sums
match the source "all/all" summary values within the 0.1 % tolerance for all
tested substances.

| Total indicators | 12 |
|---|---|
| Successfully completed | 12 |
| Failed | 0 |
| Substances extracted | 892 |
| Validation discrepancies > 0.1 % | 0 (logged at WARNING level if present) |

---

## Known-Good Reference Values

The following values can be used to validate a fresh pipeline run against the
source XLSX. Any deviation from these figures indicates either a change in the
source file or a regression in the parsing logic.

### Indicator 001 — Inorganic Gases

| Substance | EPS index (ELU/kg) | 2015 coefficient | 2020 coefficient |
|-----------|-------------------|-----------------|-----------------|
| CO2 | −0.1440 | −0.1440 | −0.1540 |
| CH4 | −0.6000 | −0.6000 | −0.6414 |
| N2O | −6.30 | −6.30 | −6.736 |
| SO2 | −1.37 | −1.37 | −1.465 |
| NOx | −1.24 | −1.24 | −1.326 |
| NH3 | −0.57 | −0.57 | −0.609 |

*Note:* 2020 coefficient = EPS_index × I[2020] = EPS_index × 1.069.
All values are sign-applied (negative = damage). Signs follow `coefficient_sign = -1.0`.

### Indicator 002 — Particles

| Substance | EPS index (ELU/kg) |
|-----------|--------------------|
| PM2.5 | −69.8 |
| PM10 | −17.2 |
| Pb (air) | −0.11 |
| Cd (air) | −0.038 |

### Indicator 010 — Fossil Resources

| Substance | EPS index (ELU/kg) |
|-----------|--------------------|
| Fossil oil | −0.10 |
| Fossil coal | −0.04 |
| Lignite | −0.02 |
| Natural gas | −0.08 |

*Values read directly from the computation worksheet at hard-coded cell positions.*

### Indicator 012 — Waste

| Substance | EPS index |
|-----------|-----------|
| Litter to ground | −0.0099 ELU/item |
| Plastic litter to water | −0.075 ELU/kg |

---

## Validation Procedure

### Step 1 — Run single indicator and inspect output

```bash
python indicators/001_prepare_inorganic_gases_eps.py
```

Expected log output:
```
INFO     pipeline: ============================================================
INFO     pipeline: Indicator : inorganic_gases
INFO     pipeline: Sheet     : 8. Inorganic gases
INFO     pipeline: Sign      : -1.0
INFO     pipeline: Years     : 2014 … 2100 (19)
INFO     pipeline: Countries : 189 | Sectors: 21
INFO     pipeline:   Loaded sheet '8. Inorganic gases'      →  16 substances (16 with full pathway data)
INFO     pipeline: Substances: 16 extracted
INFO     pipeline: Saved HDF5: output/001_eps_inorganic_gases.h5
INFO     pipeline: Saved Excel: output/001_eps_inorganic_gases.xlsx
INFO     pipeline: Done inorganic_gases         → C matrix shape (304, 3969)
```

Shape check: 304 rows = 16 substances × 19 years; 3,969 columns = 189 × 21.

### Step 2 — Verify CO2 value in Python

```python
import pandas as pd

coeff = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="coefficient")

# CO2 variable name
co2_var = [v for v in coeff.index.get_level_values("Variable") if "CO2" in v][0]
print(co2_var)
# → "EPS_InorganicGases_CO2, in ELU/kg (Steen2015)"

# 2015 value (base year, inflation factor = 1.0)
val_2015 = coeff.loc[("2015", co2_var)].iloc[0]
print(f"CO2 2015: {val_2015:.4f}")
# → CO2 2015: -0.1440

# 2020 value (inflation factor = 1.069)
val_2020 = coeff.loc[("2020", co2_var)].iloc[0]
print(f"CO2 2020: {val_2020:.4f}")
# → CO2 2020: -0.1539

# Uniformity check: all columns hold the same value
assert coeff.loc[("2015", co2_var)].nunique() == 1, "Country variation detected — unexpected"
print("Uniformity check passed")
```

### Step 3 — Verify HDF5 keys

```python
import pandas as pd

store = pd.HDFStore("output/001_eps_inorganic_gases.h5", mode="r")
print(store.keys())
# → ['/coefficient', '/unit']

unit_df = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="unit")
print(unit_df.iloc[0]["2015"])
# → "2015ELU/kg"

print(unit_df.iloc[0]["2020"])
# → "2020ELU/kg"

print(unit_df.iloc[0]["2050"])
# → "2023ELU/kg"   ← forecast: frozen at last known deflator year

store.close()
```

### Step 4 — Verify all 12 indicators

```bash
python run_all_eps_factors.py --max-workers 4
```

Check the generated `execution_log_*.txt` for:
- All 12 entries show `[OK]`
- No entries show `[FAIL]`
- Each indicator reports the expected substance count (see table in README.md)

### Step 5 — Cross-check Excel pathway data

Open `output/001_eps_inorganic_gases.xlsx`, sheet `Pathway data`.
Locate CO2 rows and verify:
- `damage_cost_eur` column sums to ≈ 0.144 across all non-summary rows
- `eps_index_source` in the "all / all" row ≈ 0.144
- Relative difference < 0.1 %

---

## Substance Counts by Indicator

These counts are verified against the source XLSX and should not change
between runs on the same source file.

| Script | Indicator | Expected substances |
|--------|-----------|-------------------|
| 001 | inorganic_gases | 16 |
| 002 | particles | 14 |
| 003 | voc | 144 |
| 004 | halogenated_organics | 283 |
| 005 | emissions_to_water | 14 |
| 006 | pesticides | 302 |
| 007 | noise | 2 |
| 008 | radionuclides | 11 |
| 009 | land_use | 23 |
| 010 | fossil_resources | 4 |
| 011 | other_elements | 77 |
| 012 | waste | 2 |
| **Total** | | **892** |

---

## QA Checks Built Into the Pipeline

| Check | Where implemented | Action on failure |
|-------|--------------------|-------------------|
| Re-derived vs source EPS index | `pipeline.load_eps_sheet()` | `logger.warning` |
| Substance count > 0 | `pipeline.run_indicator()` | `logger.error` + empty return |
| Sheet name present in workbook | `pipeline.load_eps_sheet()` | `ValueError` raised |
| Output directory created if missing | `pipeline.save_results()` | `mkdir(parents=True)` |
| HDF5 keys `"coefficient"`, `"unit"` | verifiable with `pd.HDFStore` | — |

---

## Interpretation Notes

- All coefficient values are **negative** (sign = −1.0 for damages).
  A coefficient of −0.144 ELU/kg for CO2 means that emitting 1 kg of CO2
  causes 0.144 ELU of societal damage at 2015 price levels.

- Coefficients for years before 2015 are **less than** the 2015 base value
  (inflation factor < 1.0 for 2014). This reflects that the same physical
  damage had a lower monetary equivalent in 2014 prices.

- Coefficients for years after 2015 are **more negative** (larger absolute
  value) because the same physical damage corresponds to higher EUR amounts
  at later price levels.

- Forecast years (2024–2100) are frozen at the 2023 inflation factor (1.241).
  This is a pragmatic approximation, not a forecast of future inflation.

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
