# Stockholm Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as structured coefficient matrices**

Author: Dr Dimitrij Euler, [Greenings](https://greenings.org) — dimitrij.euler@greenings.org

---

## Overview

This repository transfers the **EPS 2015d.1** Life Cycle Impact Assessment (LCIA)
dataset (Steen 2015, Swedish Life Cycle Center) into a structured value-factor
pipeline using a `config.py` → `pipeline.py` → indicators/ architecture.

Each of the 12 EPS impact categories (inorganic gases, particles, VOCs, pesticides, …)
is implemented as a standalone indicator script that:

1. **Re-derives** the EPS characterisation factor from the Excel pathway rows
   (re-implementing the Excel formula in Python, not just reading pre-computed totals)
2. **Produces** a `C[y, substance, country, sector]` coefficient matrix in the
   standard `(Year, Variable) × (GeoRegion, NACE)` coefficient matrix format
3. **Exports** to HDF5 (full matrix) and Excel (representative view)

### Formula

```
C[y, s, c, n] = Sign(s) × EPS_index[s] × I[y]
```

| Symbol | Description |
|---|---|
| `y` | Year — 2014–2030 (annual) + 2050, 2100 |
| `s` | Substance (e.g. CO2, PM2.5, 2,4-D) |
| `c` | ISO3 country code (189 countries) |
| `n` | NACE sector code (A21, 21 sectors) |
| `Sign(s)` | −1.0 for damages; +1.0 for benefits |
| `EPS_index[s]` | Environmental Load Units per kg (ELU/kg), derived from pathway sums |
| `I[y]` | EU HICP deflator[y] / deflator[2015] |

Because EPS 2015 is a **global** characterisation factor, `C` is uniform across
all `(GeoRegion, NACE)` column pairs for a given `(Year, substance)` row.
The full 189 × 21 column structure covers all countries and NACE sectors.

---

## Indicators

| Script | Category | Substances | Unit |
|---|---|---|---|
| 001 | Inorganic gases | 16 | ELU/kg |
| 002 | Particles | 14 | ELU/kg |
| 003 | Volatile organic compounds | 144 | ELU/kg |
| 004 | Halogenated organics (CFCs, HCFCs …) | 283 | ELU/kg |
| 005 | Emissions to water | 14 | ELU/kg |
| 006 | Pesticides | 302 | ELU/kg |
| 007 | Noise | 2 | ELU/W |
| 008 | Radionuclides | 11 | ELU/TBq |
| 009 | Land use | 23 | ELU/m²yr |
| 010 | Fossil resources | 4 | ELU/kg |
| 011 | Other elements (Ag, Au, Cu …) | 77 | ELU/kg |
| 012 | Waste (littering) | 2 | ELU/unit |
| **Total** | | **892** | |

---

## Output format

Each indicator produces two files in `output/`:

| File | Contents |
|---|---|
| `NNN_eps_{indicator}.h5` | Full coefficient matrix (HDF5, keys: `coefficient`, `unit`) |
| `NNN_eps_{indicator}.xlsx` | Excel: `Coefficients` sheet (50 representative columns), `Units`, `Pathway data` |

### HDF5 structure

```
key: "coefficient"
  DataFrame shape: (N_years × N_substances)  ×  (189 countries × 21 NACE sectors)
  Row MultiIndex:    ["Year", "Variable"]
  Column MultiIndex: ["GeoRegion", "NACE"]
  Values: float64 (year-specific ELU/unit, EU-deflator adjusted)

key: "unit"
  DataFrame index:   Variable name strings
  DataFrame columns: year strings
  Values: strings like "2015ELU/kg", "2023ELU/kg" (frozen for forecast years)
```

### Variable name convention

```
EPS_{Category}_{Substance}, in {unit} (Steen2015)
```

Example: `EPS_InorganicGases_CO2, in ELU/kg (Steen2015)`

---

## Usage

### Run all indicators (parallel)

```bash
pip install pandas openpyxl tables numpy
python run_all_eps_factors.py --max-workers 4
```

### Run a single indicator

```bash
python indicators/001_prepare_inorganic_gases_eps.py
```

### Read outputs in Python

```python
import pandas as pd

coeff = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="coefficient")
units = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="unit")

# CO2 coefficient for 2020, any country/sector
co2_var = [v for v in coeff.index.get_level_values("Variable") if "CO2" in v][0]
print(coeff.loc[("2020", co2_var)].iloc[0])   # → -0.1440 ELU/kg (2020 EUR)
```

### List available indicators

```bash
python run_all_eps_factors.py --list
```

---

## Source data

> Steen, B. (2015). *A new impact assessment version for the EPS system —
> EPS 2015d.1 — Including climate impacts from secondary particles.*
> Swedish Life Cycle Center Report 2015:4a.
> Chalmers University of Technology, Gothenburg, Sweden.

The source XLSX files are not redistributed here (© Swedish Life Cycle Center 2015).
The derived coefficient matrices in `output/` are produced by re-implementing
the Excel calculation logic in Python and are made available under **CC BY 4.0**.

---

## Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for the full derivation, formula documentation,
and notes on limitations (no country variation, frozen forecast deflators, unit conventions).

---

---

*Generated with [Claude Code](https://claude.ai/claude-code)*
