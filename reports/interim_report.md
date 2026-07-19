# Interim Report — Ethiopia Financial Inclusion Forecast

**Course:** 10 Academy AI Mastery — Week 11  
**Date:** 19 Jul 2026  
**Repository:** https://github.com/Guyatu1627/ethiopia-fi-forecast  

## 1. Data enrichment summary
We retained the unified schema (observations / events / targets + impact_links) and enriched it for forecasting:

- Historical **Usage** points (`USG_DIGITAL_PAYMENT` 2014/2017/2021) plus the 2024 Findex 35% anchor
- Gender and urban/rural Access disaggregations
- Derived registered–vs–survey mobile-money gap
- Two new events (agent/KYC facilitation; QR merchant expansion) with pillars left empty
- New/refined impact links; Telebirr→Access magnitude revised downward to match the +3pp Findex slowdown

Full documentation: `data_enrichment_log.md`.

## 2. At least five key EDA insights
1. Access decelerated to **+3pp** (2021–2024) after earlier double-digit gains.
2. Operator registrations far exceed survey MM ownership (**9.45%**).
3. Usage (digital payments) rose faster than Access, reaching **~35%** in 2024.
4. Gender gap narrowed but remains material.
5. Urban–rural Access gap (~32pp) constrains national averages.
6. Event overlays suggest stronger Usage/payments responses than survey ownership responses.

Details & charts: `notebooks/02_task2_eda.ipynb`, `reports/eda_key_insights.md`.

## 3. Preliminary event–indicator observations
- Telebirr/M-Pesa map to MM users and digital payments more than to Findex Access.
- Interoperability and merchant acceptance are leading Usage levers.
- Raw Access impact sums overstate 2021–2024 ownership change → refine before forecasting.

## 4. Data limitations
Sparse Findex cadence; medium-confidence historical Usage compilations; operator≠survey definitions; short enabler series; non-causal impact magnitudes.  
See `reports/data_quality_assessment.md`.

## Deliverables status (interim)
- Task 1 enriched dataset + enrichment log
- Task 2 EDA notebook + insights + quality assessment
- Git branches / PRs per challenge workflow
