# Solana paper test — $500 USD

Started: 2026-10-07 21:37 UTC
Last collection: 2026-10-09 00:35 UTC
Cycles: 615

| Item | USD |
|---|---:|
| Paper cash | 231.14 |
| Realised simulated P/L | -118.86 |
| Open positions, recent estimated sale value | 129.60 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 3; unresolved: 0.
Estimated paper equity: $360.75; estimated P/L: $-139.25.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $50 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-08 06:06:30 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $396.30
Current equity with quotes <=120s old: $360.75
Maximum observed portfolio decline since upgrade: 13.55%
Latest / largest saved-cycle gap: 30s / 1879s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 1.7807 |
| Gas | 0.1200 |
| Pool impact | 0.5458 |
| Extra slippage | 2.9579 |
| Total entry + exit drag | 5.4044 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-08 09:33:34 UTC buy HKZDfZnkHZxd9agRDNPyDv4iT6LmAurJnpRtj9wpump: $50.00; liquidity filter and second observation
- 2026-10-08 15:38:01 UTC sell 7ypCq2CJ4fnbtS3z2B1W1UT2he5E3u7Md6Gy1ri7uGrQ: $24.89; stop loss
- 2026-10-08 16:27:34 UTC sell 5tCju6YNxHq5zrA6tGndr6F7TK42mpUFmeE31cSFpump: $62.06; trailing pullback
- 2026-10-08 18:06:06 UTC sell CscZaq5twomhUkvCY8Jdd1tge32L4Yj9FbkFFEZQpump: $24.54; stop loss
- 2026-10-08 18:06:36 UTC sell HbPDWSqu8hpVMX6gMjwMDGe5rVgicWo3Qh3Jaojypump: $62.89; trailing pullback
- 2026-10-08 19:16:42 UTC sell HKZDfZnkHZxd9agRDNPyDv4iT6LmAurJnpRtj9wpump: $56.36; trailing pullback
- 2026-10-08 21:44:12 UTC sell 2UfBjNeDwzZsoUnr3hNKF4vkzAgiGmBNYCAxLq72cPa2: $47.00; time limit
- 2026-10-08 21:44:12 UTC sell H74CYmXgMkYHYuSRsZt6RJb4NYp2u72Vw8BS5huApump: $50.16; time limit
- 2026-10-09 00:32:16 UTC buy 5MS2zt6GU3KU4r8qn2gZc8W2yKdtPkLVxFDRe8WJpump: $50.00; liquidity filter and second observation
- 2026-10-09 00:32:16 UTC buy 5GefefPX1mDs6ZJB1apYmz6fCTCiNJpHturZ9bvFpump: $50.00; liquidity filter and second observation
