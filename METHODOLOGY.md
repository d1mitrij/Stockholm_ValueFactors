# EPS Calculator — Methodology

## Overview

This tool applies the **Environmental Priority Strategies (EPS) 2015d.1**
characterisation factors to a Life Cycle Inventory (LCI) to compute
environmental impacts expressed in Environmental Load Units (ELU).

## Source Data

| File | Description |
|---|---|
| `2015_4a-EPS-2015d.1-Including-climate-impacts-from-secondary-particles.xlsx` | EPS 2015d.1 — **includes** secondary-particle climate impacts (recommended) |
| `2015_4b-EPS-2015dx.1-excluding-climate-impacts-from-secondary-particles.xlsx` | EPS 2015dx.1 — **excludes** secondary-particle climate impacts |

Source: Steen, B. (2015). *A new impact assessment version for the EPS system — EPS 2015d.1.*
Swedish Life Cycle Center Report 2015:4a. Chalmers University of Technology.

## Core Formula

```
Impact [ELU] = Quantity [unit] × EPS_index [ELU/unit]
```

The EPS index (characterisation factor) converts a physical emission or
resource use quantity into a monetised societal damage expressed in ELU,
where **1 ELU = 1 EUR of societal damage** (Steen 2015).

### Multi-Pathway Aggregation

Each substance has multiple impact pathways (e.g. CO₂ affects YOLL via heat
stress, malnutrition, flooding, etc.). The XLSX aggregates all pathways into
a single **EPS default index** in the row flagged `indicator = "all"`:

```
EPS_index_substance = Σ (pathway_characterisation_factor × damage_cost)
```

This tool reads the pre-aggregated "all / all" row from the source XLSX and
does **not** re-derive per-pathway contributions.

## Impact Categories (Sheets)

| Sheet | Category |
|---|---|
| 3. Fossil res | Fossil resources |
| 4. Al | Aluminium |
| 5. Fe | Iron |
| 6. Other elements | Other elements (Ag, Au, As, …) |
| 7. Em to water | Emissions to water (BOD, COD, nutrients …) |
| 8. Inorganic gases | CO₂, CO, NOₓ, SO₂, HCl, NH₃, … |
| 9. Particles | PM>10, PM10, PM2.5, … |
| 10. VOC | Volatile organic compounds |
| 11. Halo. org. | Halogenated organics (CFCs, HCFCs, …) |
| 12. Pesticides | ~200 active substances |
| 13. Noise | Road traffic noise |
| 14. Radionuclids | Radioactive emissions to air |
| 15. Land use | Land transformation and occupation |
| 16. Waste | Littering to soil and water |

## Processing Pipeline

```
Stage 1  Configuration     config.py        — paths, column keywords
Stage 2  Data Loading      eps_loader.py    — reads XLSX, extracts EPS indices
Stage 3  Inventory Load    calculator.py    — reads inventory CSV
Stage 4  Calculation       calculator.py    — matches substances, computes ELU
Stage 5  Output Export     reporter.py      — CSV, Excel, console report
```

## Inventory CSV Format

| Column | Required | Description |
|---|---|---|
| `substance` | ✓ | Name matching an EPS substance (case-insensitive) |
| `quantity` | ✓ | Amount in the unit implied by the EPS index (usually kg) |
| `unit` | — | Documentation only |
| `description` | — | Free-text note |
| `compartment` | — | e.g. "air", "water", "soil" |

## Matching Logic

1. **Exact** case-insensitive name match
2. **Partial substring** match (warns if ambiguous)
3. **Word-overlap** match (highest word-overlap score wins)

Unmatched substances are reported in the console output and flagged in the
results CSV with `matched = False`.

## Output Files

| File | Contents |
|---|---|
| `output/results_detail.csv` | Per-substance results with EPS index and impact |
| `output/results_summary.csv` | Impact totals grouped by category |
| `output/eps_factors.csv` | Full extracted EPS factor table |
| `output/report.xlsx` | Multi-sheet Excel with all above + raw XLSX data |

## Limitations

- The EPS system uses **societal welfare economics** valuation, not legal
  liability or market prices.
- Characterisation factors are expressed per **kg** for most substances;
  verify units before interpreting results.
- NOₓ factors are negative in some versions because nitrate deposition can
  stimulate vegetation growth (ecosystem service benefit).
- This tool does not apply temporal discounting or scenario weighting.

## References

- Steen, B. (2015). EPS 2015d.1 methodology report. Swedish Life Cycle Center.
- ISO 14044:2006 — Life cycle assessment, requirements and guidelines.
