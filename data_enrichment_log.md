# Data Enrichment Log

Documentation of additions and corrections to `ethiopia_fi_unified_data` / `impact_links`.

**Collector:** Guyatu  
**Collection date:** 2026-07-19  
**Schema note:** Events keep `pillar` empty; effects are modeled only via `impact_link` rows (`parent_id` → event).

---

## Corrections

| record_id | Change | Why |
|-----------|--------|-----|
| REC_0008 | Set `collected_by=Guyatu`; clarified notes | Core Usage observation used for forecasting |
| IMP_0001 | Reduced Telebirr→`ACC_OWNERSHIP` estimate from 15pp to **4pp** (medium) | Align with observed Findex Access slowdown (+3pp, 2021–2024) |
| IMP_0015 | Set `collected_by=Guyatu` | Attribution cleanup |

---

## New observations

### REC_0036 — `USG_DIGITAL_PAYMENT` (2014, 2%)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **original_text:** Ethiopia digital payment use was very low in early Findex waves; ~2% used digital payments around 2014 (compiled from Findex country tables / secondary reporting).
- **confidence:** medium
- **collected_by / collection_date:** Guyatu / 2026-07-19
- **notes:** Historical Usage anchor for sparse-series forecasting.

### REC_0037 — `USG_DIGITAL_PAYMENT` (2017, 8%)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **original_text:** Digital payment adoption in Ethiopia remained single-digit in 2017 Findex reporting (~8% made/received digital payments, secondary compilation).
- **confidence:** medium
- **collected_by / collection_date:** Guyatu / 2026-07-19
- **notes:** Pre-mobile-money-scale Usage point.

### REC_0038 — `USG_DIGITAL_PAYMENT` (2021, 18%)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **original_text:** Around 2021, digital payment use among Ethiopian adults was still limited (~18% made or received a digital payment; compiled from Findex 2021 country materials).
- **confidence:** medium
- **collected_by / collection_date:** Guyatu / 2026-07-19
- **notes:** Usage baseline near Telebirr launch window.

### REC_0008 — `USG_DIGITAL_PAYMENT` (2024, 35%) *(retained / documented)*
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **original_text:** 35% of Ethiopian adults made or received a digital payment in the past 12 months, according to Global Findex 2024.
- **confidence:** high
- **collected_by / collection_date:** Guyatu / 2026-07-19
- **notes:** Primary Usage target series endpoint.

### REC_0039 / REC_0040 — Male/Female `ACC_OWNERSHIP` (2021)
- **Male 55% / Female 35%** (≈20pp gap, consistent with `GEN_GAP_ACC`)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **why useful:** Gender-gap trajectory for Access equity analysis.

### REC_0041 / REC_0042 — Male/Female `ACC_OWNERSHIP` (2024)
- **Male ~56% / Female ~42%** (gap narrowed vs 2021)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **why useful:** Tests whether inclusion gains are closing gender disparities.

### REC_0043 / REC_0044 — Urban/Rural `ACC_OWNERSHIP` (2024)
- **Urban ~72% / Rural ~40%**
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **why useful:** Explains national Access stagnation — rural adults remain underserved.

### REC_0045 — Registered vs survey MM gap (2024, 44.55pp derived)
- **source_url:** https://www.worldbank.org/en/publication/globalfindex (combined with operator Telebirr user counts)
- **original_text:** Telebirr alone reports 54M registered users while survey MM account ownership is only 9.45% of adults — large registered-vs-active/survey gap.
- **confidence:** medium
- **why useful:** Central hypothesis for 2021–2024 Access slowdown despite “65M+ accounts.”

---

## New events (pillar left empty)

### EVT_0011 — Agent Banking / KYC Simplification Push (2022-03-01)
- **category:** regulation
- **source_url:** https://nbe.gov.et
- **confidence:** low
- **why useful:** Regulatory friction reduction for onboarding.

### EVT_0012 — National QR / Merchant Acceptance Expansion (2024-06-01)
- **category:** infrastructure
- **source_url:** https://ethswitch.com
- **confidence:** medium
- **why useful:** Usage intensity (P2P-for-commerce) beyond account opening.

---

## New impact links

| record_id | parent_id | indicator | estimate | lag | evidence |
|-----------|-----------|-----------|----------|-----|----------|
| IMP_0016 | EVT_0001 | USG_DIGITAL_PAYMENT | +10pp | 18m | comparable_country (Kenya) |
| IMP_0017 | EVT_0009 | ACC_OWNERSHIP | +3pp | 36m | policy |
| IMP_0018 | EVT_0012 | USG_DIGITAL_PAYMENT | +4pp | 6m | empirical |
| IMP_0019 | EVT_0011 | ACC_OWNERSHIP | +2pp | 12m | policy |
| IMP_0015 | EVT_0003 | USG_DIGITAL_PAYMENT | +8pp | 12m | comparable_country (Kenya) *(existing, retained)* |

---

## Why these additions matter for forecasting

1. **Usage history** (2014–2024) enables trend + event-augmented forecasts instead of a single 2024 anchor.
2. **Gender/urban-rural splits** explain why national Access moved only +3pp despite mobile-money registration growth.
3. **Refined impact magnitudes** prevent over-predicting Findex Access from operator user counts.
4. **Merchant/QR + regulation events** capture Usage drivers that are not pure product launches.

---

## Dataset reconstruction note

Where the original starter workbook was incomplete in the workspace, core Findex and event rows were reconstructed from the Week 11 challenge brief and public Findex figures, then enriched as above. Always prefer the CSVs in `data/raw/` and `data/processed/` as the working source of truth.
