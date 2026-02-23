# Input Files Methodology — EPS Value Factors

**EPS 2015d.1 — Environmental Priority Strategies characterisation factors
as transitionvaluation-compatible coefficient matrices**

---

## Overview

The single primary input is the official EPS 2015d.1 dataset published by
the Swedish Life Cycle Center:

> Steen, B. (2015). *A new impact assessment version for the EPS system —
> EPS 2015d.1 — Including climate impacts from secondary particles.*
> Swedish Life Cycle Center Report 2015:4a.
> Chalmers University of Technology, Gothenburg, Sweden.

The dataset is distributed as a Microsoft Excel workbook. Two variants exist:

| File | Contents |
|------|----------|
| `2015_4a-EPS-2015d.1-Including-climate-impacts-from-secondary-particles (1).xlsx` | **Primary** — includes secondary-particle climate impacts |
| `old/2015_4b-EPS-2015dx.1-excluding-climate-impacts-from-secondary-particles-1.xlsx` | Alternative — excludes secondary-particle climate impacts |

All 12 indicator scripts use the primary variant (`4a`) by default. The
`eps_xlsx_without_secondary` path in `config.COMMON_PATHS` allows switching.

---

## XLSX Workbook Structure

The workbook contains 16 worksheets. Two sheets provide background information;
14 sheets contain substance-level EPS data.

### Informational Sheets

#### Sheet 1 — Introduction (`1. Introduction`)

Provides the conceptual description of the EPS method, including:

- Definition of Environmental Load Units (ELU): 1 ELU = 1 EUR societal
  damage at 2015 price levels.
- Hierarchy of safeguard subjects: human health, ecosystem production
  capacity, biodiversity, abiotic resources, cultural values.
- Explanation of the pathway structure: each emission is characterised
  via a chain of environmental mechanisms (Fate → Exposure → Effect →
  Damage → Monetary value).
- Scope and limitations of EPS 2015d.1 relative to earlier EPS versions.

**This sheet is not parsed by the pipeline.** It is consulted for methodology
documentation purposes.

#### Sheet 2 — State Indicators (`2. State indicators`)

Defines the monetary value assigned to each state indicator unit, expressed
in EUR (2015 price levels). These values are the monetary weighting factors
used in the pathway-level formula.

Example values from Sheet 2:

| State Indicator | Monetary Value | Unit |
|-----------------|---------------|------|
| Human health — severe morbidity | 50,000 | EUR/year of suffering |
| Human health — mortality (YOLL) | 75,000 | EUR/YOLL |
| Ecosystem production capacity | 10 | EUR/PDF·m²·yr |
| Biodiversity — potentially disappeared fraction | 1,000,000 | EUR/PDF·yr |
| Mineral and fossil resources | Market price dependent | EUR/kg |
| Cultural values — crop loss | 1 | EUR/kg crop |
| Noise (annoyance) | 100 | EUR/(person·W) |

**This sheet is not parsed by the pipeline** (the monetary values are
already embedded in the pre-computed pathway damage costs in each substance
sheet). It is used for documentation and QA cross-referencing.

---

### Substance Sheets (Sheets 3–16)

Each substance sheet contains one or more of:

1. A **pathway table** — one row per (substance, safeguard subject, pathway)
   with columns for extent of impact, contribution factor, and damage cost.
2. A **summary row** (labelled "all" or "all/all") — the pre-computed EPS
   index for each substance, equal to the sum of all pathway damage costs.

The pipeline reads the pathway table, re-derives the EPS index from pathway
sums, and validates against the summary row (tolerance < 0.1 %).

---

#### Sheet 3 — Fossil Resources (`3. Fossil res`)

**Parser type:** Special (hard-coded positions)
**Substances:** 4

| Substance | Row | Col | Description |
|-----------|-----|-----|-------------|
| Fossil oil | 14 | 4 | Damage cost EUR/kg |
| Fossil coal | 43 | 4 | External + internal cost SUM (current technology) |
| Lignite | 46 | 4 | Damage cost EUR/kg |
| Natural gas | 59 | 4 | Total cost EUR/kg CH4 |

This sheet is a computation worksheet rather than a standard lookup table.
The EPS index for each fossil resource is derived from the incremental scarcity
cost: the cost of extracting the marginal unit of the resource, representing
the loss of future availability to humanity.

**Special parser:** `_load_fossil_resources()` reads cell values from the
hard-coded row/column positions listed above.

---

#### Sheet 6 — Other Elements (`6. Other elements`)

**Parser type:** Generic
**Substances:** 77
**Unit:** ELU/kg

Contains mineral and metal elements: Ag, Al, Au, B, Ba, Be, Bi, Cd, Ce, Co,
Cr, Cu, Dy, Er, Eu, Fe, Ga, Gd, Ge, Hf, Ho, In, Ir, La, Li, Lu, Mg, Mn,
Mo, Nb, Nd, Ni, Os, Pb, Pd, Pr, Pt, Re, Rh, Ru, Sb, Sc, Se, Si, Sm, Sn,
Sr, Ta, Tb, Te, Th, Ti, Tl, Tm, U, V, W, Y, Yb, Zn, Zr, and others.

EPS indices are derived from resource scarcity costs. For metals, the
marginal cost model considers ore grade depletion and energy requirements
for mining and processing.

---

#### Sheet 7 — Emissions to Water (`7. Em to water`)

**Parser type:** Generic
**Substances:** 14
**Unit:** ELU/kg

Covers substance emissions to freshwater and seawater. Damage pathways
include:

- Ecotoxicity to aquatic organisms (PDF·m²·yr metric)
- Human toxicity via drinking water and fish consumption
- Eutrophication of aquatic ecosystems

Substances include: BOD, COD, chlorinated solvents, mercury (to water),
phosphorus, nitrogen compounds, and others.

---

#### Sheet 8 — Inorganic Gases (`8. Inorganic gases`)

**Parser type:** Generic
**Substances:** 16
**Unit:** ELU/kg

Key emissions to air: CO2, CO, CH4, N2O, SO2, NOx, NH3, H2S, and others.

This is the most important sheet for climate-related assessment. The
EPS 2015d.1 variant (`4a`) includes climate impacts from secondary
aerosol formation, which adds to the SO2, NOx, and NH3 coefficients
compared to the `4b` variant.

CO2 worked example (see METHODOLOGY.md for full derivation):

| Pathway | Extent | Contribution | Monetary | Damage Cost |
|---------|--------|-------------|---------|-------------|
| Global warming → human health | 1.79×10⁻³ yr/kg | 1/75,000 | 75,000 EUR/YOLL | 0.1440 ELU/kg |
| … | … | … | … | … |
| **Total EPS_index[CO2]** | | | | **0.1440 ELU/kg** |

---

#### Sheet 9 — Particles (`9. Particles`)

**Parser type:** Generic
**Substances:** 14
**Unit:** ELU/kg

Particulate matter fractions and airborne heavy metals: PM2.5, PM10,
PM2.5–10 (coarse), and metals including As, Cd, Cr(VI), Ni, Pb, Hg (air).

The particle damage pathway runs: emission → atmospheric dispersion →
inhalation → respiratory and cardiovascular health effects → years of
life lost (YOLL) and morbidity → EUR damage.

---

#### Sheet 10 — Volatile Organic Compounds (`10. VOC`)

**Parser type:** Generic
**Substances:** 144
**Unit:** ELU/kg

144 individual VOC species, including: benzene, toluene, xylenes,
ethylene, propylene, formaldehyde, acetaldehyde, styrene, 1,3-butadiene,
and numerous other aromatic and aliphatic hydrocarbons.

Damage pathways include: photochemical ozone formation (human health
and ecosystem), direct toxicity, and carcinogenicity.

---

#### Sheet 11 — Halogenated Organics (`11. Halo. org.`)

**Parser type:** Generic
**Substances:** 283
**Unit:** ELU/kg

CFCs (CFC-11, CFC-12, …), HCFCs (HCFC-22, …), HFCs (HFC-134a, …),
perfluorocarbons (CF4, C2F6, …), halons (Halon-1211, …), and
chlorinated solvents (TCE, PCE, DCM, …).

Damage pathways include: stratospheric ozone depletion → UV-B radiation
increase → skin cancer and cataracts; global warming potential → human
health and ecosystem impacts.

---

#### Sheet 12 — Pesticides (`12. Pesticides`)

**Parser type:** Generic
**Substances:** 302
**Unit:** ELU/kg

Approximately 302 pesticide active substances, including: organophosphates
(malathion, parathion, chlorpyrifos), organochlorines (DDT, lindane),
pyrethroids (cypermethrin, deltamethrin), herbicides (glyphosate, 2,4-D,
atrazine), fungicides (captan, mancozeb), and others.

Damage pathways: ecotoxicity to terrestrial and aquatic organisms
(PDF·m²·yr); human toxicity via food residues and occupational exposure.

---

#### Sheet 13 — Noise (`13. Noise`)

**Parser type:** Generic
**Substances:** 2
**Unit:** ELU/W

Two noise metrics:
- `Road traffic noise` (long-term average)
- `Train noise`

The functional unit is the relative acoustic power of the noise source (W).
Damage pathway: noise level → population annoyance → loss of wellbeing
(EUR/person/year of serious annoyance) → ELU/W.

---

#### Sheet 14 — Radionuclides (`14. Radionuclids`)

**Parser type:** Special (column position)
**Substances:** 11
**Unit:** ELU/TBq

Radionuclides from nuclear fuel cycle air emissions: Kr-85, Xe-133,
I-131, I-129, C-14, H-3 (tritium), Ru-106, Cs-137, Sr-90, Ra-226,
U-238, and others.

Damage pathway: release to air → collective effective dose (man·Sv)
via inhalation and ground shine → cancer incidence and YOLL.

**Special parser:** `_load_radionuclides()` reads the "Damage cost, EUR/TBq"
column (column index 6) starting from row 3 (rows 0–2 are section title,
header, and unit rows). Stops at the "Emissions to water" section header,
which Steen (2015) marks as "negligable [sic] impact" and excludes.

---

#### Sheet 15 — Land Use (`15. Land use`)

**Parser type:** Generic
**Substances:** 23
**Unit:** ELU/m²yr

Land use types (transformation and occupation categories): arable land,
forest — multiple land-use classification schemes. Damage pathway:
land use → potentially disappeared fraction of species (PDF) × area × time
→ biodiversity damage.

---

#### Sheet 16 — Waste (`16. waste`)

**Parser type:** Special (hard-coded rows)
**Substances:** 2
**Unit:** ELU/unit

| Substance | Row | Col | Description |
|-----------|-----|-----|-------------|
| Litter to ground | 6 | 9 | per number of items |
| Plastic litter to water | 7 | 9 | per kg |

Damage pathways: visual pollution (cultural value impairment); ecotoxicity
from plastics in the marine environment; entanglement and ingestion by
wildlife.

---

## Reading the XLSX in Python

The pipeline reads the XLSX using `openpyxl` with `data_only=True` to
retrieve computed cell values rather than formula strings:

```python
import openpyxl

wb = openpyxl.load_workbook(
    xlsx_path,
    read_only=True,    # memory-efficient streaming mode
    data_only=True,    # return cached cell values, not formula strings
)
ws = wb[sheet_name]
raw_rows = [tuple(cell.value for cell in row) for row in ws.iter_rows()]
wb.close()
```

**Important:** `data_only=True` requires that the XLSX was last saved with
Excel calculating all formula results. If the file was saved from LibreOffice
or another application that did not cache formula results, cell values may
be `None`. Always verify with the reference workbook provided by the Swedish
Life Cycle Center.

---

## Source File Validation Checklist

Before running the pipeline, verify:

- [ ] XLSX file name matches the path in `config.COMMON_PATHS["eps_xlsx_with_secondary"]`
- [ ] File is accessible and not locked by another process
- [ ] File was last saved from Excel (not LibreOffice) so formula results are cached
- [ ] Sheet names match exactly: `3. Fossil res`, `6. Other elements`, …, `16. waste`
- [ ] Sheet count is 16 (not 15 or 17)
- [ ] CO2 EPS index in sheet `8. Inorganic gases` ≈ 0.144 ELU/kg (sanity check)

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
