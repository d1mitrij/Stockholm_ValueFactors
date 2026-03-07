# EPS 2015d.1 Value Factors — Methodology

**Organisation:** Greenings
**Version:** 1.0
**Last Updated:** 2026-02-23
**Contact:** dimitrij.euler@greenings.org

---

## 1. Conceptual Foundation: Damage to Society

### 1.1 Theoretical Basis

The EPS (Environmental Priority Strategies) method quantifies the **societal damage**
caused by environmental pressures — emissions, resource extraction, land use, noise —
in monetary units called Environmental Load Units (ELU), where 1 ELU ≈ 1 EUR of
welfare loss to society.

This is a **damage cost** approach, not a legal liability or market-price approach:

| Concept | Damage to Society (EPS) | Legal Liability | Market Price |
|---|---|---|---|
| Basis | Welfare economics | Regulatory threshold | Supply and demand |
| Scope | Global, long-term | Jurisdiction-specific | Current |
| Metric | ELU (≈ EUR/unit pressure) | EUR per event | EUR/unit |
| Sign | Negative for damages | Positive cost | Positive price |
| Reference | Steen (2015) | Jurisdiction law | Market data |

### 1.2 Safeguard Subjects

The EPS method protects five **safeguard subjects** — values that society seeks to
preserve. Every state indicator is assigned to one safeguard subject.

| Safeguard Subject | Description |
|---|---|
| Ecosystem services | Provisioning (food, wood, water) and cultural (quality time, biodiversity) services |
| Abiotic resources | Mineral and fossil resource stocks, valued by extraction cost differential |
| Human health | Life expectancy (YOLL) and disability-adjusted quality of life |
| Economic assets | Technology infrastructure capacity and cost efficiency |
| Biodiversity | Species-level extinction equivalents (NEX) |

---

## 2. State Indicators and Monetary Values

State indicators are the endpoints of impact pathways. Each carries a monetary weight
in ELU per indicator unit, derived from willingness-to-pay (WTP) studies, replacement
cost analysis, or production cost differentials.

### 2.1 Selected monetary values (Sheet 2, EPS 2015d.1)

| State Indicator | Safeguard Subject | Unit | ELU/unit | Uncertainty factor |
|---|---|---|---|---|
| YOLL (years of life lost) | Human health | personyears | 50,000 | 1.5 |
| Working capacity | Human health | personyears | 58,800 | 1.6 |
| Malnutrition | Human health | personyears | 9,550 | 1.1 |
| Diarrhea | Human health | personyears | 5,250 | 1.2 |
| Asthma cases | Human health | personyears | 2,150 | 2.0 |
| COPD severe | Human health | personyears | 19,150 | 2.0 |
| Cancer | Human health | personyears | 10,000 | 2.0 |
| Skin cancer | Human health | personyears | 2,500 | 1.3 |
| Crop growth capacity | Ecosystem services | kg | 0.22 | 2.0 |
| Fish & meat production | Ecosystem services | kg | 2.10 | 2.1 |
| Wood growth capacity | Ecosystem services | kg | 0.04 | 1.4 |
| Drinking water | Access to water | kg | 0.002 | 2.0 |
| Irrigation water | Access to water | kg | 0.001 | 2.0 |
| NEX (species extinction) | Biodiversity | dimensionless | 56,000,000,000 | 3.0 |
| Housing availability | Economic | m² | 2,000 | 2.0 |
| Fossil oil reserves | Abiotic resources | kg | 0.47 | 1.4 |
| Iron ore reserves | Abiotic resources | kg | 0.81 | 2.0 |

Full table: Sheet 2 of the source workbook.

---

## 3. Mathematical Framework

### 3.1 Pathway derivation formula

For each substance `s`, the EPS characterisation factor is derived by summing
damage costs across all impact pathways:

```
EPS_index[s] = Σ_{indicator i, pathway p} damage_cost[s, i, p]

where:
  damage_cost[s, i, p]  =  pathway_cf[s, i, p]  ×  monetary_value[i]
  pathway_cf[s, i, p]   =  extent_of_impact[s, i, p]  ×  contribution_mean[s, i]

and:
  extent_of_impact  =  change in state indicator i caused by substance s via pathway p
                       [personyears, kg, m², or dimensionless]
  contribution_mean =  1 / reference_stock
                       (e.g. 1 / world_population for YOLL pathways)
  monetary_value[i] =  ELU per state indicator unit  (from Section 2 above)
```

Example — CO₂, YOLL pathway, heat stress:

```
extent_of_impact  =  597,256,000 personyears   (global YOLL from heat stress)
contribution_mean =  2.265e-16 per kg CO₂      (= 1 / global CO₂ stock proxy)
pathway_cf        =  597,256,000 × 2.265e-16   =  1.353e-07 personyears/kg CO₂
damage_cost       =  1.353e-07 × 50,000 ELU/PY =  6.764e-03 ELU/kg CO₂

Sum across all CO₂ pathways (YOLL, crop, water, NEX, …) = 0.13478 ELU/kg CO₂
```

### 3.2 Value factor formula

After deriving `EPS_index[s]`, the value factor coefficient is computed as:

```
C[y, s, c, n]  =  Sign(s)  ×  EPS_index[s]  ×  I[y]

where:
  y   =  year (2014–2030, 2050, 2100)
  s   =  substance
  c   =  ISO3 country code (189 countries; EPS is globally uniform, so D[s,c] = D[s])
  n   =  NACE sector code (21 sectors; EPS has no sector differentiation)
  Sign(s)  =  -1.0 for all damage substances (all EPS categories)
  I[y]     =  EU HICP deflator[y] / EU HICP deflator[2015]
```

### 3.3 Inflation adjustment

EPS 2015 values are expressed in 2015 EUR. The inflation factor `I[y]` re-expresses
them in year-`y` nominal EUR using the EU Harmonised Index of Consumer Prices (HICP):

```
I[y] = HICP_EU[y] / HICP_EU[2015]

Selected values (base = 2015 = 100.0):
  2014 → 98.6/100.0  = 0.986
  2015 → 100.0/100.0 = 1.000   (base year)
  2020 → 106.9/100.0 = 1.069
  2023 → 124.1/100.0 = 1.241
  2025+→ 124.1/100.0 = 1.241   (frozen at last available year)
```

Forecast years (2024–2030, 2050, 2100) are frozen at the 2023 value, as no Eurostat
data is available beyond that release.

---

## 4. Indicator-Specific Methodologies

### 001 — Inorganic Gases (`8. Inorganic gases`)

**Methodology overview:**
Inorganic gas emissions to air are characterised via multiple damage pathways covering
climate change (heat stress, flooding, undernutrition), human health (YOLL, working
capacity, diarrhoea), ecosystem provisioning (crop, water, NEX), and infrastructure
(housing, energy access). Each pathway's contribution is summed to yield the EPS index.

**Processing algorithm:**
1. Load pathway rows (substance, indicator, pathway, extent_mean, contribution_mean, damage_cost_eur)
2. Sum `damage_cost_eur` across all pathways per substance → `EPS_index[s]`
3. Apply `Sign = -1.0` (all inorganic gases cause societal damage)
4. Broadcast uniformly across 189 countries × 21 NACE sectors
5. Apply EU HICP inflation factor per year

**Damage cost components (example: CO₂):**

| Indicator | Pathway | Damage cost (ELU/kg) |
|---|---|---|
| YOLL | Heat stress | 0.006764 |
| YOLL | Cold moderation | −0.000064 |
| YOLL | Undernutrition | 0.025016 |
| YOLL | Flooding | 0.000589 |
| Malnutrition | Food supply | 0.022843 |
| Working capacity | Heat stress | 0.068566 |
| Crop | Climate change + sea level | 0.002399 |
| NEX | Habitat change | 0.000013 |
| … | … | … |
| **Total EPS index** | | **0.13478 ELU/kg** |

**Substances covered:** CO₂, CO, NOₓ, N₂O, SO₂, H₂S, HF, HCl, NH₃, Hg (trace),
Hg (bulk), HBr, HCN, O₃, HNO₂, HNO₃

**Output unit:** `ELU/kg` (2015 EUR equivalent)

---

### 002 — Particles (`9. Particles`)

**Methodology overview:**
Particulate matter emissions are characterised for direct health effects (YOLL from
acute and chronic exposure, asthma, COPD) and indirect climate effects via GWP.
Heavy metal particles (As, Cd, Cr, Cu, Pb, Zn) include toxicological pathways.

**Processing algorithm:**
1. Identify "all" summary rows per substance (aggregated EPS index)
2. For particles lacking a summary row, derive from pathway damage cost sums
3. Apply `Sign = -1.0` and broadcast across all countries/sectors
4. Apply EU HICP inflation

**Substances covered:** PM>10, PM10, PM2.5, ultrafine PM, As, Cd, Cr, Cu, Pb, Zn, PAH,
plus size-fractionated variants

**Output unit:** `ELU/kg`

---

### 003 — Volatile Organic Compounds (`10. VOC`)

**Methodology overview:**
VOC impacts are calculated via three intermediate potentials: Global Warming Potential
(GWP100), Photochemical Ozone Creation Potential (POCP), and Particle Formation
Potential (PFP). Each potential bridges from the VOC to the existing CO₂, NOₓ,
and particulate matter characterisation factors.

```
damage_cost_VOC[s, pathway] = potential[s] × EPS_index[reference_substance, pathway]

  GWP100[s]  →  scales CO₂ climate-change pathways
  POCP[s]    →  scales NOₓ oxidant pathways (crop loss, YOLL/oxidants)
  PFP[s]     →  scales PM2.5 secondary-particle pathways (YOLL, asthma, COPD)
```

**Substances covered:** 144 VOCs including alkanes, aromatics, alcohols, aldehydes,
terpenes, and chlorinated solvents

**Output unit:** `ELU/kg`

---

### 004 — Halogenated Organics (`11. Halo. org.`)

**Methodology overview:**
Halogenated organic compounds (CFCs, HCFCs, HFCs, PFCs) are characterised via two
potentials: GWP100 (climate change pathways, same as CO₂) and ODP
(Ozone Depletion Potential, driving YOLL/ozone depletion, skin cancer, low vision).

```
damage_cost[s] = GWP100[s] × CO₂_climate_pathways
               + ODP[s]    × ozone_depletion_pathways
```

**Substances covered:** 283 halogenated compounds including CFCs (11, 12, 113, 114,
115), HCFCs (22, 141b, 142b), HFCs (134a, 152a, 227ea), PFCs, halons, and
chlorinated solvents

**Output unit:** `ELU/kg`

---

### 005 — Emissions to Water (`7. Em to water`)

**Methodology overview:**
Substance emissions to freshwater and seawater are characterised across two pathways:
oxygen deficiency (affecting fish & meat production) and eutrophication (affecting
biodiversity via NEX). The compartment (fresh/sea) determines the pathway extent
and contribution factors.

**Substances covered:** BOD (freshwater, seawater), COD, nitrogen compounds,
phosphorus compounds, heavy metals to water, chlorinated solvents to water

**Output unit:** `ELU/kg`

---

### 006 — Pesticides (`12. Pesticides`)

**Methodology overview:**
Pesticide characterisation uses an acute toxicity potency factor derived from oral
LD50 values, then applies to YOLL (acute poisoning deaths), chronic disability
(poisoning personyears), ore extraction impacts (As, Cu, Hg, Pb, Zn released by
manufacturing), and biodiversity loss (NEX).

```
potency_factor[s] = 400 / LD50_rat_oral[s]   (mg/kg reference: 400 mg/kg)

damage_cost[s] = potency_factor[s] × (YOLL_factor + poisoning_factor
               + ore_extraction_factor + NEX_factor)
```

**Substances covered:** ~302 active pesticide substances identified by CAS registry
number (CASRN), including herbicides, insecticides, fungicides, and plant growth
regulators. IARC carcinogenicity classifications are noted where applicable.

**Output unit:** `ELU/kg`

---

### 007 — Noise (`13. Noise`)

**Methodology overview:**
Road traffic noise is characterised in terms of relative power (10^(dBA/10)) rather
than kg. The damage pathway runs through YOLL via sleep disturbance, with a
contribution factor derived from population exposure at European traffic densities.

```
damage_cost = extent_of_YOLL × contribution × monetary_YOLL
            = 1,296,000 personyears × 1.715e-17 per unit × 50,000 ELU/PY
            = 1.111e-06 ELU per relative power unit
```

**Output unit:** `ELU/W` (relative power = 10^(dBA/10))

---

### 008 — Radionuclides (`14. Radionuclids`)

**Methodology overview:**
Characterisation of radioactive emissions to air from the nuclear fuel cycle.
The derivation chain: collective dose (manSv/TBq) → YOLL and cancer personyears →
damage costs (EUR/TBq).

```
YOLL  [personyears/TBq] = collective_dose[manSv/TBq] × YOLL_per_manSv
Cancer[personyears/TBq] = collective_dose[manSv/TBq] × cancer_per_manSv
damage_cost[EUR/TBq]    = YOLL × 50,000 + cancer × 10,000
```

**Substances covered:** C-14, H-3, I-129, Kr-85, Pb-210, Po-210, Ra-226,
Rn-222, Th-230, U-234, U-238

**Output unit:** `ELU/TBq`

---

### 009 — Land Use (`15. Land use`)

**Methodology overview:**
Land use impacts are characterised for transformation and occupation activities by
their effects on: (1) climate change (via GHG emissions from soil carbon), (2) crop
and wood production capacity, (3) drinking water provision capacity, and (4) biodiversity
(NEX).

**Activity types covered:** 23 land use categories including residential and commercial
developments (by city size), arable farming, intensive/extensive grazing, forestry,
mining, and infrastructure corridors

**Output unit:** `ELU/m²yr`

---

### 010 — Fossil Resources (`3. Fossil res`)

**Methodology overview:**
Fossil resource depletion is valued by the **production cost differential** between
current extraction and the next-best sustainable alternative (biomass-based processes
or near-sustainable production). External costs (depletion of co-extracted ores,
mining land use, emissions) plus internal process costs are summed.

| Resource | EPS index | Basis |
|---|---|---|
| Fossil oil | 0.47 ELU/kg | External + internal cost differential |
| Fossil coal | 0.184 ELU/kg | Cost differential (current technology) |
| Lignite | 0.098 ELU/kg | Cost differential |
| Natural gas | 0.277 ELU/kg | Total cost EUR/kg CH₄ |

**Output unit:** `ELU/kg`

---

### 011 — Other Elements (`6. Other elements`)

**Methodology overview:**
Mineral element extraction is valued by the **crustal scarcity method**: the higher
the ratio of element price to its crustal abundance, the greater the depletion cost.
The weighting factor reflects the economic effort required to extract one further
kilogram from the Earth's upper continental crust at average concentration.

```
EPS_index[element] = element_price_USD/kg / crustal_abundance_mg/kg × scarcity_factor
```

**Substances covered:** 77 elements from Ag (silver) to Zr (zirconium), including
rare earth elements, platinum-group metals, and industrially critical elements

**Output unit:** `ELU/kg`

---

### 012 — Waste (`16. waste`)

**Methodology overview:**
Waste impacts in EPS are normally evaluated via the substances that make up the waste.
An exception is **littering** — unmanaged waste to ground or water — where a common
impact applies regardless of chemical composition (working capacity loss from
microplastic ingestion; reduction of fish & meat production capacity).

| Category | EPS index | Unit |
|---|---|---|
| Litter to ground | 0.00746 ELU | per item |
| Plastic litter to water | 0.80 ELU | per kg |

**Output unit:** `ELU/unit`

---

## 5. Data Processing Pipeline

The five-stage pipeline is implemented in `pipeline.py` and called from each indicator
script. The five stages are:

```python
# Stage 1 — Configuration
cfg = config.get_indicator_config("inorganic_gases")
years, countries, nace = cfg["years"], cfg["countries"], cfg["nace"]

# Stage 2 — Data Loading
pathway_df, substance_df = load_eps_sheet(cfg["eps_xlsx_with_secondary"],
                                          cfg["sheet_name"])

# Stage 3 — Coefficient Matrix (vectorised)
variables = [_make_variable_name(category, s, unit) for s in substances]
coeff = create_coefficient_dataframe(years, variables, countries, nace)
coeff = populate_coefficients(coeff, substance_df, years, variables, sign)

# Stage 4 — Inflation Adjustment (vectorised numpy broadcast)
inflation_factors = calculate_inflation_factors(years)
coeff_final = apply_deflation(coeff, inflation_factors, years, variables)
units = build_unit_frame(variables, years, unit_base)

# Stage 5 — Output Export
save_results(coeff_final, units, pathway_df,
             hdf5_path=cfg["hdf5_path"], excel_path=cfg["excel_path"])
```

**Output DataFrame dimensions:**

```
coeff_final:
  rows:    (N_years × N_substances)  =  19 × N_sub
  columns: (N_countries × N_sectors) =  189 × 21 = 3,969
  index:   MultiIndex ["Year", "Variable"]
  columns: MultiIndex ["GeoRegion", "NACE"]
  dtype:   float64, year-nominal ELU/unit
```

---

## 6. Quality Assurance

### 6.1 Built-in validation checks

| Check | Implementation | Expected outcome |
|---|---|---|
| Pathway sum vs. source index | `eps_index_derived` vs. `eps_index_source` | Relative error < 0.1% |
| Sign convention | All damage substances | All coefficients ≤ 0 at 2015 |
| Column uniformity | EPS is globally uniform | All 3,969 columns identical per row |
| Inflation at base year | `I[2015]` | 1.0000 |
| Year coverage | Output index | 19 years: 2014–2030, 2050, 2100 |

### 6.2 Known limitations

- **No country variation.** EPS 2015 characterisation factors are globally uniform.
  The `(GeoRegion, NACE)` column structure covers all 189 countries and 21 sectors,
  but all countries receive identical coefficients. Country-specific damage costs would
  require a value transfer step (PPP or income elasticity adjustment) not present in
  the base EPS 2015 dataset.

- **EUR base currency.** Values are in ELU ≈ EUR (2015 price level). Users comparing
  to USD-denominated datasets should apply an EUR/USD exchange rate for the reference year.

- **Forecast deflation frozen.** Years beyond 2023 use the 2023 EU HICP value.
  Real inflation trends after 2023 are not projected.

- **Uncertainty factors.** The source workbook documents uncertainty factors
  (geometric standard deviation, column `Uncertainty factor` in Sheet 2) for each
  state indicator. These are preserved in the `pathway_df` output table but are not
  propagated through the coefficient matrix.

---

## 7. References

### Primary source
- Steen, B. (2015). *A new impact assessment version for the EPS system — EPS 2015d.1 —
  Including climate impacts from secondary particles.* Swedish Life Cycle Center
  Report 2015:4a. Chalmers University of Technology, Gothenburg, Sweden.

### Methodology references
- Steen, B. (1999). *A systematic approach to environmental priority strategies in
  product development (EPS). Version 2000 — General system characteristics.*
  Chalmers University of Technology.
- EC-JRC (2011). *ILCD Handbook: Recommendations for Life Cycle Impact Assessment
  in the European context.* Publications Office of the European Union.

### Inflation data
- Eurostat (2024). *GDP deflator, EU27, base year 2015.* Reference: nama_10_gdp.

### Related documentation
- See ARCHITECTURE_DECISIONS.md for pipeline design rationale
- See INPUT_FILES_METHODOLOGY.md for XLSX structure description
- See VALIDATION_REPORT.md for completed validation checklists
- See ALGORITHMS_VISUAL.md for pipeline flowcharts

---

*Document Version 1.0 | Last Updated 2026-02-23 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
