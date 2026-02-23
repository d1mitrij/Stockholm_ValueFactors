# Troubleshooting — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as transitionvaluation-compatible coefficient matrices**

---

Each issue is listed with:

- **Symptom** — what you observe
- **Cause** — root cause
- **Solution** — corrective action

---

## Issue 1 — `FileNotFoundError` on source XLSX

**Symptom**
```
FileNotFoundError: [Errno 2] No such file or directory:
  '.../steen-vf1/2015_4a-EPS-2015d.1-...(1).xlsx'
```

**Cause**
The source XLSX is not redistributed in this repository (© Swedish Life Cycle
Center 2015). It must be obtained directly from the publisher and placed in the
correct location.

**Solution**
1. Obtain the EPS 2015d.1 XLSX from the Swedish Life Cycle Center.
2. Place it in the project root: `/path/to/steen-vf1/`
3. Verify the file name matches exactly what is configured in `config.COMMON_PATHS`:
   ```python
   "eps_xlsx_with_secondary": ROOT_DIR / "2015_4a-EPS-2015d.1-Including-climate-impacts-from-secondary-particles (1).xlsx"
   ```
4. If the file name differs, update `config.py` rather than renaming the file.

---

## Issue 2 — All EPS indices are zero

**Symptom**
Pipeline completes without error but HDF5 contains a matrix of all zeros.

**Cause**
The EPS index column in the source sheet was not detected. The generic parser's
`_find_col()` returned −1 (no match) and all numeric reads defaulted to 0.

**Solution**
1. Open the source XLSX and inspect the header row of the affected sheet.
2. Check what the EPS index column is labelled (e.g., "EPS default index", "ELU/kg",
   "Weighting factor").
3. Verify that the label contains one of the HIGH-priority keywords in
   `pipeline._find_col()`:
   ```python
   HIGH = ["eps", "default index", "elu/", "weighting factor"]
   ```
4. If not, add the relevant keyword to the `HIGH` list.

Note: the two-pass detection (ADR-006) was introduced precisely to fix this
symptom when "damage cost" was matched before "EPS default index".

---

## Issue 3 — `substance_df` is empty for sheets 3, 14, or 16

**Symptom**
```
ERROR    pipeline: No EPS data extracted for indicator 'fossil_resources'
```

**Cause**
The generic parser did not find a standard header row in these non-standard
sheets. The special parsers should have been dispatched but weren't — typically
because the sheet name in `config.INDICATORS` does not exactly match the
workbook sheet name.

**Solution**
1. Run the following to list the actual sheet names in the workbook:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook("path/to/file.xlsx", read_only=True)
   print(wb.sheetnames)
   wb.close()
   ```
2. Compare with the `sheet_name` values in `config.INDICATORS` and with the
   keys in `pipeline._SPECIAL_SHEET_LOADERS`.
3. Update the sheet name in `config.py` if it differs.

---

## Issue 4 — Radionuclides returns 0 substances

**Symptom**
```
INFO  Loaded sheet '14. Radionuclids' → 0 substances (special parser)
```

**Cause**
The `_load_radionuclides` parser reads damage cost values from column index 6.
If the workbook layout has changed, or if a different XLSX variant is used,
column 6 may not contain numeric damage cost values.

**Solution**
1. Open the XLSX and examine sheet `14. Radionuclids`.
2. Locate the "Damage cost, EUR/TBq" column and count its 0-based column index.
3. Update the constant in `pipeline._load_radionuclides()`:
   ```python
   DAMAGE_COST_COL = 6    # ← change if layout has shifted
   ```

---

## Issue 5 — Subprocess timeout for large sheets

**Symptom**
```
[FAIL] pesticides    600.1s  012_prepare_pesticides_eps.py
       STDERR: ...  TimeoutExpired
```

**Cause**
The default subprocess timeout is 600 seconds. On machines with slow I/O or
limited CPU, the pesticides indicator (302 substances × 19 years × 3,969 columns)
may exceed this limit.

**Solution**
Increase the timeout:
```bash
python run_all_eps_factors.py --timeout 1200 --max-workers 2
```

Alternatively, run the script directly (no timeout):
```bash
python indicators/006_prepare_pesticides_eps.py
```

If performance is chronically slow, verify that numpy vectorisation is active
(see Issue 8 below).

---

## Issue 6 — Excel write takes many hours

**Symptom**
The `to_excel` call for a large indicator (e.g., pesticides) takes 30+ minutes.

**Cause**
The `excel_max_cols` cap in `save_results()` was overridden or removed,
causing `openpyxl` to write all 3,969 country-sector columns.

**Solution**
Verify that `save_results()` applies the column cap:
```python
if n_cols > excel_max_cols:    # excel_max_cols defaults to 50
    coeff_excel = coeff_final.iloc[:, :excel_max_cols]
```

If the full matrix is needed in Excel (not recommended for large indicators),
write it in chunks or use a different format (CSV, Parquet).

The full matrix is always available in the companion HDF5 file.

---

## Issue 7 — Unit string reads `"2015EUR/ELU/kg"` instead of `"2015ELU/kg"`

**Symptom**
Unit strings in the HDF5 or Excel contain a double-slash:
```
"2015EUR/ELU/kg"
```

**Cause**
An older version of `pipeline.build_unit_frame()` used:
```python
f"{y}EUR/{unit_base}"  # with unit_base = "ELU/kg" → "2015EUR/ELU/kg"
```

**Solution**
The current version strips the leading `"ELU/"` prefix from `unit_base`:
```python
phys_unit = unit_base.lstrip("ELU/") if unit_base.startswith("ELU/") else unit_base
# "ELU/kg" → "kg"
f"{y}ELU/{phys_unit}"  # → "2015ELU/kg"
```

If you see double-slash unit strings, your `pipeline.py` is out of date.
Re-run the indicator after updating the file.

---

## Issue 8 — Coefficient population runs slowly (no numpy speedup)

**Symptom**
`populate_coefficients()` takes minutes per indicator instead of milliseconds.

**Cause**
If `numpy` is not installed or `coeff.to_numpy(copy=False)` returns a copy
instead of a view (can happen with certain DataFrame dtypes or index types),
the vectorised assignment may not modify the DataFrame in place.

**Solution**
1. Verify numpy is installed:
   ```bash
   python -c "import numpy; print(numpy.__version__)"
   ```
2. Check that `coeff.dtypes` is uniformly `float64` (not `object`):
   ```python
   print(coeff.dtypes.unique())
   # Expected: [dtype('float64')]
   ```
3. The DataFrame is initialised with `dtype=float` in `create_coefficient_dataframe()`.
   If it has been modified and changed to `object` dtype, re-create it:
   ```python
   coeff = coeff.astype(float)
   ```

---

## Issue 9 — `ModuleNotFoundError: No module named 'tables'`

**Symptom**
```
ModuleNotFoundError: No module named 'tables'
```

**Cause**
HDF5 support in pandas requires the `tables` (PyTables) package, which is not
installed by default.

**Solution**
```bash
pip install tables
```

Or install all required packages at once:
```bash
pip install pandas openpyxl tables numpy
```

---

## Issue 10 — HDF5 file is unreadable after a failed run

**Symptom**
```
OSError: Unable to open file (file signature not found)
```
or
```
HDF5ExtError: HDF5 error back trace
```

**Cause**
The HDF5 file was partially written during a run that terminated early
(e.g., keyboard interrupt, disk full).

**Solution**
Delete the corrupt file and re-run:
```bash
rm output/NNN_eps_{indicator}.h5
python indicators/NNN_prepare_{indicator}_eps.py
```

HDF5 files are written atomically by `pandas.to_hdf` (mode `"w"` creates
a new file; if interrupted, the old file may be corrupt). Always re-run
from scratch after an interrupted write.

---

## Issue 11 — `KeyError: 'Unknown indicator'`

**Symptom**
```
KeyError: "Unknown indicator 'my_key'. Valid keys: ['inorganic_gases', ...]"
```

**Cause**
The `indicator_key` passed to `pipeline.run_indicator()` does not match any
key in `config.INDICATORS`.

**Solution**
List valid keys:
```bash
python run_all_eps_factors.py --list
```

Or in Python:
```python
from config import list_indicators
for key, script_id, desc in list_indicators():
    print(key, script_id, desc)
```

---

## Issue 12 — Warning: derivation error > 0.1 %

**Symptom**
```
WARNING  pipeline: Sheet '10. VOC': 3 substance(s) have >0.1% derivation error:
         ['Isoprene', 'alpha-Pinene', 'Limonene']
```

**Cause**
The re-derived EPS index (sum of pathway damage costs) differs from the
pre-computed "all/all" summary value in the source XLSX by more than 0.1 %.
This can occur due to floating-point rounding in the Excel formula chain.

**Action**
This is a warning only — the pipeline uses the re-derived value, which is
based on explicit pathway data. Investigate the flagged substances in the
source XLSX to determine whether the discrepancy is a rounding artefact or
an error in the source data. For VOC substances, discrepancies at the 0.1–1 %
level are typically floating-point rounding in the Excel model.

---

## Issue 13 — `openpyxl` reads `None` for all data cells

**Symptom**
All `substance_df` rows contain NaN values despite the XLSX appearing correct
when opened in Excel.

**Cause**
The file was last saved from LibreOffice Calc or another application that
did not cache formula results. `openpyxl` with `data_only=True` returns `None`
for cells that contain formulas with no cached result.

**Solution**
Open the file in Microsoft Excel (not LibreOffice), press Ctrl+Alt+F9 to force
recalculation, then save. Re-run the pipeline.

Alternatively, use LibreOffice's macro interface to recalculate and save in
`.xlsx` format with results cached.

---

## Issue 14 — `run_all_eps_factors.py --only` has no effect

**Symptom**
`--only inorganic_gases` flag still runs all 12 indicators.

**Cause**
The `--only` filter matches on the indicator *key* (e.g., `inorganic_gases`),
not on the script file name. If the wrong value is passed, all scripts match.

**Solution**
Use the exact key from `config.INDICATORS`:
```bash
python run_all_eps_factors.py --only inorganic_gases particles
```

List available keys:
```bash
python run_all_eps_factors.py --list
```

---

## Issue 15 — Negative values in `substance_df["eps_index"]`

**Symptom**
Some substances show a positive `eps_index` value before sign is applied.

**Cause**
This is correct: the `eps_index` in `substance_df` is the raw damage cost
from the XLSX (always positive, since it represents the magnitude of harm).
The sign is applied in `populate_coefficients()` via the `sign` parameter.
After sign application, all EPS damage coefficients are negative (sign = −1.0).

**Action**
No action required. Verify with:
```python
import pandas as pd
coeff = pd.read_hdf("output/001_eps_inorganic_gases.h5", key="coefficient")
assert (coeff < 0).all().all(), "Expected all-negative coefficients"
```

---

## Issue 16 — `PermissionError` writing to `output/`

**Symptom**
```
PermissionError: [Errno 13] Permission denied: 'output/001_eps_inorganic_gases.h5'
```

**Cause**
An existing HDF5 file in `output/` is open in another process (e.g., a Jupyter
notebook that has not closed the file handle), or write permissions are missing.

**Solution**
1. Close any open HDF5 file handles:
   ```python
   # In Jupyter: ensure all HDFStore objects are closed
   store.close()
   ```
2. Check file permissions: `ls -l output/`
3. If locked by another process: `lsof output/001_eps_inorganic_gases.h5`
   and kill the process if appropriate.

---

## Issue 17 — Execution log shows `[FAIL]` with no stderr

**Symptom**
```
[FAIL] inorganic_gases   0.3s  001_prepare_inorganic_gases_eps.py
       STDERR: (empty)
```

**Cause**
The subprocess failed to start, typically because `python` is not on `PATH`
or the script has a syntax error at import time.

**Solution**
1. Test the script directly:
   ```bash
   python indicators/001_prepare_inorganic_gases_eps.py
   ```
2. Check for syntax errors:
   ```bash
   python -m py_compile indicators/001_prepare_inorganic_gases_eps.py
   ```
3. Verify the Python executable:
   ```bash
   which python && python --version
   ```

---

## Issue 18 — Country count differs from expected 189

**Symptom**
```
INFO  Countries : 188 | Sectors: 21
```
instead of the expected 189.

**Cause**
`config.COUNTRIES` contains 189 entries in the released version. If you see
a different count, the list may have been modified or a duplicate removed.

**Solution**
```python
from config import COUNTRIES
print(len(COUNTRIES))         # should be 189
print(len(set(COUNTRIES)))    # should equal len(COUNTRIES) — no duplicates
```

If counts differ, restore `config.COUNTRIES` from the repository.

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
