# Impact Modeling Methodology

## Approach
1. Join `impact_link` rows to events via `parent_id`.
2. Build an **association matrix** (events × indicators) using `impact_estimate` (pp or count as coded).
3. Map each shock onto calendar years with lag:
   - `step_after_lag` for Access ownership
   - `linear_ramp` for Usage adoption
4. Validate against observed deltas (Telebirr-era MM and Access).
5. Refine magnitudes (Telebirr→Access reduced to ~4pp) and apply forecast scaling.

## Sources for estimates
- Local operator / EthSwitch / NBE reporting (empirical)
- Kenya M-Pesa literature (comparable_country)
- NFIS-II policy targets (policy)
- Challenge Market Nuances (registered vs active, P2P-for-commerce)

## Validation (predicted vs observed)
| Check | Observed | Model implication |
|-------|----------|-------------------|
| MM ownership 2021→2024 | +4.75pp | Product shocks matter for MM Access |
| Account ownership 2021→2024 | +3pp | Raw Access impact sums overstate survey change → refine/scale |
| Digital payments → 35% (2024) | Strong Usage rise | Usage impacts more transferable than Access |

## Key assumptions
- Additive event effects
- Constant lag horizons
- Partial pass-through from registrations to Findex
- No full saturation/interaction model

## Uncertainties
Sparse history, definition mismatch, macro shocks (FX), and uncertain future interoperability uptake.
