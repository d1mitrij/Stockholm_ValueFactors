# Architecture Decision Records — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as transitionvaluation-compatible coefficient matrices**

---

## Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Re-derive EPS indices from pathway rows | Accepted |
| ADR-002 | Mirror the WifOR five-stage pipeline | Accepted |
| ADR-003 | Broadcast D[s] uniformly across all GeoRegion × NACE | Accepted |
| ADR-004 | Apply EU HICP deflator (GDP, EU27) | Accepted |
| ADR-005 | Freeze deflator at last known year for forecasts | Accepted |
| ADR-006 | Two-pass column detection (HIGH / FALLBACK priority) | Accepted |
| ADR-007 | Special parsers for three non-standard sheets | Accepted |
| ADR-008 | Vectorised numpy operations for coefficient population | Accepted |
| ADR-009 | Cap Excel output at 50 representative columns | Accepted |
| ADR-010 | Use blosc-compressed HDF5 for full-matrix storage | Accepted |
| ADR-011 | Use `ThreadPoolExecutor` for parallel indicator runs | Accepted |
| ADR-012 | Adopt A21 NACE macro-classification for sector dimension | Accepted |

---

## ADR-001 — Re-derive EPS indices from pathway rows

**Status:** Accepted
**Date:** 2026-02-23

### Context

The EPS 2015d.1 XLSX contains both pre-computed EPS index totals (the "all / all"
summary rows) and the individual (substance, indicator, pathway) rows from which
those totals are derived. Reading pre-computed totals would be faster to implement
but would produce coefficients that cannot be traced back to the underlying
physical and monetary assumptions.

### Decision

The pipeline re-implements the Excel summation formula in Python, aggregating
`damage_cost_eur` across all pathway rows per substance:

```
EPS_index[s] = Σ_{i,p} damage_cost[s,i,p]
```

The re-derived value is compared to the source "all / all" total for every
substance. Discrepancies above 0.1 % are logged as warnings.

### Consequences

- Full traceability: each coefficient can be traced to its pathways.
- QA built in: re-derivation discrepancies surface numerical rounding
  in the source Excel.
- Slightly more complex parser (must distinguish pathway rows from summary rows),
  but the added complexity is isolated to `pipeline.load_eps_sheet()`.

---

## ADR-002 — Mirror the WifOR five-stage pipeline

**Status:** Accepted
**Date:** 2026-02-23

### Context

The [transitionvaluation](https://github.com/Greenings/transitionvaluation)
project uses a consistent five-stage pipeline that is documented and understood
by the team working with the WifOR Value Factors submodule. Adopting the same
structure makes integration straightforward and reduces the learning curve for
new contributors.

### Decision

`pipeline.py` implements the five stages in the same order and with the same
function signatures as the WifOR pipeline:

| Stage | WifOR function | EPS equivalent |
|-------|---------------|----------------|
| 1 Configuration | `get_indicator_config()` | `config.get_indicator_config()` |
| 2 Data Loading | `load_sheet()` | `load_eps_sheet()` |
| 3 Coefficient Matrix | `create_coefficient_dataframe()` + `populate_coefficients()` | identical names |
| 4 Inflation Adjustment | `apply_deflation()` | identical name |
| 5 Output Export | `save_results()` | identical name |

Each of the 12 indicator scripts (`001_…_eps.py` to `012_…_eps.py`) is a
thin wrapper that calls `pipeline.run_indicator(key)`, mirroring the WifOR
pattern.

### Consequences

- Drop-in compatibility with the transitionvaluation loading code.
- The `config.py` INDICATORS dict, `COMMON_PARAMS`, and `COMMON_PATHS`
  follow the same key naming conventions, so `get_indicator_config()` returns
  a flat dict with the same keys.
- Some WifOR pipeline concepts (e.g., country-specific `D[i, c]` matrices)
  are collapsed to a global `D[s]` broadcast because EPS has no country
  variation — this simplification is explicitly documented in `pipeline.py`.

---

## ADR-003 — Broadcast D[s] uniformly across all GeoRegion × NACE

**Status:** Accepted
**Date:** 2026-02-23

### Context

The WifOR pipeline supports country-specific damage cost coefficients
`D[i, c]` because several of the WifOR indicators (wages, resource rents)
vary by country. EPS 2015 characterisation factors are deliberately global:
Steen (2015) derives a single EPS index per substance that applies worldwide.

### Decision

After loading `D[s]` from the source XLSX, `populate_coefficients()` broadcasts
the value identically across all 189 country columns and all 21 NACE sector
columns using numpy broadcasting:

```python
arr[row_start:row_end, :] = d_values[:, np.newaxis]
```

The full (189 × 21 = 3,969) column structure is maintained in the output
DataFrames for compatibility with MRIO / EORA26-style analysis frameworks.

### Consequences

- Output format is fully compatible with the WifOR transitionvaluation loader.
- Storage and computation cost is proportional to (countries × sectors), but
  this is acceptable given blosc-compressed HDF5 storage.
- The Excel output notes this uniformity explicitly so that analysts do not
  interpret variation across country columns as meaningful.

---

## ADR-004 — Apply EU HICP deflator (GDP, EU27)

**Status:** Accepted
**Date:** 2026-02-23

### Context

EPS 2015 monetary values are expressed in EUR at 2015 price levels. To produce
coefficients that are comparable with WifOR outputs (which use year-specific
EUR values), an inflation adjustment must be applied.

### Decision

Use the Eurostat GDP deflator for EU27, expressed in the base year 2015 = 100.0.
This matches the WifOR convention for European LCIA datasets.

Source: Eurostat `nama_10_gdp` series (GDP deflator, EU27).

Known values (2014–2023):

| Year | Index (2015 = 100) | Factor I[y] |
|------|--------------------|-------------|
| 2014 | 98.6 | 0.9860 |
| 2015 | 100.0 | 1.0000 |
| 2016 | 101.0 | 1.0100 |
| 2017 | 102.5 | 1.0250 |
| 2018 | 104.6 | 1.0460 |
| 2019 | 106.3 | 1.0630 |
| 2020 | 106.9 | 1.0690 |
| 2021 | 109.4 | 1.0940 |
| 2022 | 117.3 | 1.1730 |
| 2023 | 124.1 | 1.2410 |

### Consequences

- Coefficients for years with real deflator data are labelled `{y}ELU/{unit}`.
- Forecast year coefficients are labelled with the last known deflator year
  (see ADR-005).

---

## ADR-005 — Freeze deflator at last known year for forecasts

**Status:** Accepted
**Date:** 2026-02-23

### Context

The year series extends to 2050 and 2100 (long-horizon assessment years
required by the transitionvaluation framework). No GDP deflator forecast
is available with sufficient confidence for 2024–2100.

### Decision

Forecast years beyond 2023 are assigned the last known deflator value (index
124.1, factor 1.2410). This matches the WifOR behaviour for forecast years.
Unit strings for forecast years are labelled `"2023ELU/{unit}"` to signal
that the 2023 factor was applied.

### Consequences

- Long-horizon coefficients (2050, 2100) are approximations: they represent
  the real damage cost at 2023 price levels, not at future price levels.
- Analysts using forecast years should note this limitation.
  It is documented in METHODOLOGY.md, section "Inflation adjustment".

---

## ADR-006 — Two-pass column detection (HIGH / FALLBACK priority)

**Status:** Accepted
**Date:** 2026-02-23

### Context

Several EPS worksheets contain a column labelled "Damage cost (EUR/kg)" that
appears to the left of the column labelled "EPS default index (ELU/kg)".
A single-pass keyword search matching "damage cost" would return the wrong
column.

The original single-pass implementation produced all-zero substance_df results
for the inorganic gases sheet because the "damage cost" column (col 10) was
matched instead of the "EPS default index" column (col 11).

### Decision

`pipeline._find_col()` uses a two-pass detection strategy:

1. **HIGH priority** — scan all header cells for any of:
   `["eps", "default index", "elu/", "weighting factor"]`
2. **FALLBACK** — only if no HIGH-priority match found, scan for:
   `["damage cost"]`

This ensures the EPS index column is always preferred over the intermediate
damage cost column.

### Consequences

- Correct column detection on all 12 sheets.
- The priority list is defined once in `_find_col()` and is easy to extend
  if new sheet layouts are encountered in future EPS versions.

---

## ADR-007 — Special parsers for three non-standard sheets

**Status:** Accepted
**Date:** 2026-02-23

### Context

Three worksheets in the EPS 2015 XLSX do not follow the standard tabular
layout expected by the generic parser:

| Sheet | Issue |
|-------|-------|
| `3. Fossil res` | Computation worksheet; EPS indices at hard-coded row/col positions |
| `14. Radionuclids` | Damage cost column is at col 6, not a standard header row |
| `16. waste` | Only 2 substances at rows 6–7, col 9 |

### Decision

`pipeline._SPECIAL_SHEET_LOADERS` maps sheet names to dedicated parser functions
(`_load_fossil_resources`, `_load_radionuclides`, `_load_waste`) that hard-code
the known cell positions. The dispatch happens before the generic parser is
attempted:

```python
if sheet_name in _SPECIAL_SHEET_LOADERS:
    return _SPECIAL_SHEET_LOADERS[sheet_name](raw_rows)
```

### Consequences

- All 12 sheets produce non-empty `substance_df` results.
- Special parsers are fragile to changes in the source XLSX layout — if Steen
  (2015) is updated, the row/col constants must be reviewed.
- Cell positions are documented with comments inside each special parser.

---

## ADR-008 — Vectorised numpy operations for coefficient population

**Status:** Accepted
**Date:** 2026-02-23

### Context

Large EPS categories contain hundreds of substances (pesticides: 302, halogenated
organics: 283, VOC: 144). The initial implementation used pandas `.loc` slicing
to populate the coefficient matrix one `(year, variable)` row at a time, which
triggered O(N_year × N_substance) individual MultiIndex lookups.

Benchmarks showed this took over 90 seconds for pesticides on the development
machine and caused a subprocess timeout in the parallel runner.

### Decision

`populate_coefficients()` and `apply_deflation()` both obtain a direct numpy
view of the DataFrame's underlying array and operate on it in-place:

```python
# populate_coefficients
arr = coeff.to_numpy(copy=False)
for i_year in range(len(years)):
    arr[i_year*N_sub : (i_year+1)*N_sub, :] = d_values[:, np.newaxis]

# apply_deflation
i_col = np.repeat([inflation_factors[y] for y in years], N_sub).reshape(-1, 1)
arr *= i_col   # single broadcast multiply
```

### Consequences

- Coefficient population: O(N_year) outer loops, each writing a (N_sub × N_col)
  array slice. For pesticides (19 years × 302 subs): ~10 ms instead of ~90 s.
- `apply_deflation()` reduces to a single broadcast multiply: ~1 ms per indicator.
- The numpy view (`copy=False`) means in-place modification is reflected
  immediately in the DataFrame without an additional copy.

---

## ADR-009 — Cap Excel output at 50 representative columns

**Status:** Accepted
**Date:** 2026-02-23

### Context

A full coefficient matrix for pesticides contains
(19 years × 302 substances) × (189 countries × 21 sectors) =
5,738 rows × 3,969 columns = 22.7 million cells.

Writing this to Excel with `pandas.ExcelWriter` took 3,667 seconds (≈ 61 minutes)
during testing, making per-indicator Excel output impractical for large sheets.

### Decision

`save_results()` caps the Excel "Coefficients" sheet at 50 GeoRegion × NACE
columns (the first 50 of 3,969). Because EPS 2015 is a global characterisation
factor (D[s] is identical for all countries), these 50 columns are fully
representative of the entire matrix.

A "Notes" sheet in the same XLSX documents the truncation:
```
Note: Showing 50 of 3969 GeoRegion×NACE columns.
All columns hold the same value (EPS 2015 is a global CF — no country variation).
Full data in the companion .h5 file.
```

The full matrix is always written to the companion HDF5 file.

### Consequences

- Excel write time: ≤ 20 seconds per indicator (down from > 60 minutes).
- HDF5 files remain the authoritative data source for downstream analysis.
- Analysts who load the Excel directly see a valid, representative subset.

---

## ADR-010 — Use blosc-compressed HDF5 for full-matrix storage

**Status:** Accepted
**Date:** 2026-02-23

### Context

The full coefficient matrix for the pesticides indicator
(5,738 × 3,969 = 22.7 M cells of float64) would occupy ~182 MB uncompressed.
Storing 12 such files uncompressed would total several GB in the `output/`
directory.

### Decision

HDF5 files are written with `complevel=4, complib="blosc"` via PyTables:

```python
coeff_final.to_hdf(hdf5_path, key="coefficient", mode="w", complevel=4, complib="blosc")
```

Blosc is a block-oriented compressor optimised for numerical arrays that
achieves high compression ratios with fast decompression.

### Consequences

- Typical compression ratios of 10–50× for uniform EPS arrays
  (all country columns identical, so the data is highly redundant).
- Load times are comparable to uncompressed reads on modern hardware.
- Requires the `tables` (PyTables) package; listed in the installation
  prerequisites.

---

## ADR-011 — Use `ThreadPoolExecutor` for parallel indicator runs

**Status:** Accepted
**Date:** 2026-02-23

### Context

The 12 indicator scripts are independent of each other (no shared mutable
state) and dominated by I/O (reading the source XLSX) and CPU-bound numpy
operations. Running them sequentially takes approximately 575 seconds.

### Decision

`run_all_eps_factors.py` runs all 12 scripts via `concurrent.futures.ThreadPoolExecutor`:

```python
with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
    futures = {pool.submit(run_one, script): script for script in scripts}
```

Each script is run as a subprocess (`subprocess.run`) to avoid shared-state
issues with the openpyxl workbook objects.

Default `--max-workers 4` is chosen conservatively; disk I/O is the
bottleneck when all workers read the same large XLSX simultaneously.

### Consequences

- Typical wall-clock time: ~110 seconds for all 12 indicators (default 4 workers).
- `ProcessPoolExecutor` was considered but rejected: subprocess-based parallelism
  is simpler and avoids serialisation issues with openpyxl/pandas objects.
- The parallel runner writes a timestamped execution log with per-indicator
  timing and captured stderr output.

---

## ADR-012 — Adopt A21 NACE macro-classification for sector dimension

**Status:** Accepted
**Date:** 2026-02-23

### Context

EPS 2015 characterisation factors have no sector variation: the same EPS index
applies to emissions from agriculture as from manufacturing. A sector dimension
must still be present in the output because MRIO frameworks (EORA26, Exiobase)
require a consistent (GeoRegion, NACE) column structure.

### Decision

Use the NACE A21 macro-classification (21 sectors), matching the WifOR
transitionvaluation convention. The sectors are defined in `config.NACE_SECTORS`
and labelled with standard NACE codes (A, B, C10-C12, …, O-U).

### Consequences

- Direct compatibility with EORA26-style supply-use tables (EORA uses the A21
  aggregation as its primary sector classification).
- All 21 NACE columns hold the same coefficient value for a given (year, substance)
  row — this is a consequence of EPS being globally uniform, not a limitation of
  the output format.

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
