# EDA Key Insights (≥5)

Evidence-backed findings from Task 2 exploratory analysis.

## 1. Access growth stalled after 2021
Account ownership rose +11pp (2017→2021) then only **+3pp** (2021→2024: 46%→49%) despite Telebirr and M-Pesa scale-up.  
**Evidence:** `ACC_OWNERSHIP` Findex series; growth-rate table in `02_task2_eda.ipynb`.

## 2. Registered accounts ≠ financial inclusion
Telebirr reports **54M+** registered users while survey mobile-money ownership is **9.45%**. The derived registered–survey gap highlights dormancy, duplicates, and definition mismatch.  
**Evidence:** `USG_TELEBIRR_USERS`, `ACC_MM_ACCOUNT`, `USG_REG_SURVEY_GAP`.

## 3. Usage is expanding faster than Access
Digital payment adoption rises from low single digits (2014) to **~35%** (2024). Payment behavior is shifting even while ownership stagnates.  
**Evidence:** `USG_DIGITAL_PAYMENT` enriched series; P2P/ATM crossover milestone.

## 4. Gender gap narrowing but unfinished
Male–female ownership gap ~**20pp** in 2021; female ownership improves toward the low-40s by 2024 while male rates stay mid-50s.  
**Evidence:** `ACC_OWNERSHIP_M/F`, `GEN_GAP_ACC`.

## 5. Rural exclusion anchors the national average
Urban ownership (~**72%**) vs rural (~**40%**) in 2024 implies national Access cannot accelerate without rural delivery.  
**Evidence:** `ACC_OWNERSHIP_URBAN/RURAL`.

## 6. Events map more cleanly to Usage intensity than Findex Access
Product launches and interoperability show clearer links to MM users / P2P volumes than to survey ownership.  
**Evidence:** `impact_links` + event overlay charts.

## 7. Hypotheses for impact modeling
- Active-use conversion > new registrations for Findex gains  
- Merchant acceptance / interoperability raise Usage without proportional Access gains  
- Affordability/FX shocks can offset product-launch benefits  

See `reports/data_quality_assessment.md` for limitations.
