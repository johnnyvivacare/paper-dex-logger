# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-10 22:18 UTC
Cycles: 1088

| Item | USD |
|---|---:|
| Paper cash | 66.33 |
| Realised simulated P/L | -533.67 |
| Open positions, recent estimated sale value | 404.89 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 4; unresolved: 0.
Estimated paper equity: $471.22; estimated P/L: $-528.78.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $471.22
Maximum observed portfolio decline since upgrade: 58.40%
Latest / largest saved-cycle gap: 30s / 1769s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 14.0439 |
| Gas | 0.5200 |
| Pool impact | 12.8070 |
| Extra slippage | 23.2983 |
| Total entry + exit drag | 50.6693 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-10 11:48:45 UTC buy HZ9n1kjjxvkV92Y2pUx6AKp2FqKKW1hMmhM6QTQppump: $100.00; liquidity filter and second observation
- 2026-10-10 12:02:23 UTC sell HZ9n1kjjxvkV92Y2pUx6AKp2FqKKW1hMmhM6QTQppump: $20.73; stop loss
- 2026-10-10 16:33:39 UTC sell AhuPBbDHo2B77qehebV6AzsULve7ghpV41tovqhgpump: $107.42; time limit
- 2026-10-10 16:33:41 UTC buy EpFTb2XcGiMyGLykZ9VYmyPWz2AHEwAggqSbwJpypump: $100.00; liquidity filter and second observation
- 2026-10-10 17:40:21 UTC sell AyYNfPtftg2zDP4ZbgcoQMggQtwLh4zpfVVmUJs2thto: $99.10; time limit
- 2026-10-10 17:40:22 UTC sell EpFTb2XcGiMyGLykZ9VYmyPWz2AHEwAggqSbwJpypump: $94.07; trailing pullback
- 2026-10-10 19:02:40 UTC buy HwJyyniKKDRLXxjRSzyLtpvxzqecqrhrbcSbKRm7STNK: $100.00; liquidity filter and second observation
- 2026-10-10 19:54:21 UTC buy 6eR6nCiDPAxqKPR28VabmbhbkYcBMq19w3cWcWTmyUkk: $100.00; liquidity filter and second observation
- 2026-10-10 20:11:16 UTC sell 258hQ12j9UeGdiEaJzYuMjrgPFbsveNuK72uVKAR3DQj: $74.72; time limit
- 2026-10-10 20:11:17 UTC buy E6vtwCUtcNJdQEPGY8vWKahtu2sfwxQ4j68pUKm7pump: $100.00; liquidity filter and second observation
