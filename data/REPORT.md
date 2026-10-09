# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: not collected yet
Cycles: 0

| Item | USD |
|---|---:|
| Paper cash | 1000.00 |
| Realised simulated P/L | +0.00 |
| Open positions, recent estimated sale value | 0.00 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 0; unresolved: 0.
Estimated paper equity: $1000.00; estimated P/L: $+0.00.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $1000.00
Maximum observed portfolio decline since upgrade: 0.00%
Latest / largest saved-cycle gap: 0s / 0s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 0.0000 |
| Gas | 0.0000 |
| Pool impact | 0.0000 |
| Extra slippage | 0.0000 |
| Total entry + exit drag | 0.0000 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

