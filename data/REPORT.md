# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-09 01:48 UTC
Cycles: 21

| Item | USD |
|---|---:|
| Paper cash | 491.74 |
| Realised simulated P/L | -108.26 |
| Open positions, recent estimated sale value | 387.05 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 4; unresolved: 0.
Estimated paper equity: $878.79; estimated P/L: $-121.21.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $878.79
Maximum observed portfolio decline since upgrade: 12.83%
Latest / largest saved-cycle gap: 30s / 1206s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 2.0773 |
| Gas | 0.0800 |
| Pool impact | 1.9664 |
| Extra slippage | 3.4431 |
| Total entry + exit drag | 7.5668 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-09 01:01:01 UTC buy 4tCtbCyQc5Pp8V72VrW1MP7yTHTGpCutVZMsFvAsEssa: $100.00; liquidity filter and second observation
- 2026-10-09 01:01:01 UTC buy 5GefefPX1mDs6ZJB1apYmz6fCTCiNJpHturZ9bvFpump: $100.00; liquidity filter and second observation
- 2026-10-09 01:01:02 UTC buy Y9ccqrALa5Yr3Bxzv8NQe37KP1Yy9uTCSJuap4Cpump: $100.00; liquidity filter and second observation
- 2026-10-09 01:02:32 UTC buy HMYd9tosnUXuNHmq7pXmoePRVBLBBjA3JBfydq6upump: $100.00; liquidity filter and second observation
- 2026-10-09 01:04:02 UTC buy 9oxWMhM4QN1hLGNutaTFcBjMjJce6QxrvVxAcGW6pump: $100.00; liquidity filter and second observation
- 2026-10-09 01:26:07 UTC buy HbPDWSqu8hpVMX6gMjwMDGe5rVgicWo3Qh3Jaojypump: $100.00; liquidity filter and second observation
- 2026-10-09 01:47:04 UTC sell 4tCtbCyQc5Pp8V72VrW1MP7yTHTGpCutVZMsFvAsEssa: $43.71; stop loss
- 2026-10-09 01:47:05 UTC sell Y9ccqrALa5Yr3Bxzv8NQe37KP1Yy9uTCSJuap4Cpump: $48.03; stop loss
