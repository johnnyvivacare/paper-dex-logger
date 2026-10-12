# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-12 21:50 UTC
Cycles: 2135

| Item | USD |
|---|---:|
| Paper cash | 93.43 |
| Realised simulated P/L | -806.57 |
| Open positions, recent estimated sale value | 104.60 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 1; unresolved: 0.
Estimated paper equity: $198.03; estimated P/L: $-801.97.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $198.03
Maximum observed portfolio decline since upgrade: 81.35%
Latest / largest saved-cycle gap: 27s / 2331s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 17.7405 |
| Gas | 0.6700 |
| Pool impact | 15.0168 |
| Extra slippage | 29.4348 |
| Total entry + exit drag | 62.8621 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-11 10:57:59 UTC sell 9Ro2AeikFisoMqyE2HjcPhgUnXvZqRwZgRxtsgsLpump: $0.37; stop loss
- 2026-10-11 20:00:12 UTC sell 6eR6nCiDPAxqKPR28VabmbhbkYcBMq19w3cWcWTmyUkk: $106.32; time limit
- 2026-10-11 20:00:13 UTC buy syQqkspvb2PRr1meJ5pJDmhgxwc4hUou2TMjjrTmeta: $100.00; liquidity filter and second observation
- 2026-10-11 20:21:57 UTC sell E6vtwCUtcNJdQEPGY8vWKahtu2sfwxQ4j68pUKm7pump: $96.23; time limit
- 2026-10-11 21:43:56 UTC buy 2j5SaS7xy776qCBpyPQbZjyQSAtKiFgrwjfErthnW2ZM: $100.00; liquidity filter and second observation
- 2026-10-12 20:03:54 UTC sell syQqkspvb2PRr1meJ5pJDmhgxwc4hUou2TMjjrTmeta: $92.82; time limit
- 2026-10-12 20:03:54 UTC buy hKyXZVKmrBDPhKKhdSaaGf1qrFwUkwjqrdzRc63farm: $100.00; liquidity filter and second observation
- 2026-10-12 21:49:54 UTC sell 2j5SaS7xy776qCBpyPQbZjyQSAtKiFgrwjfErthnW2ZM: $53.14; time limit
- 2026-10-12 21:49:55 UTC sell hKyXZVKmrBDPhKKhdSaaGf1qrFwUkwjqrdzRc63farm: $101.45; trailing pullback
- 2026-10-12 21:49:55 UTC buy AjpPZo85HmHrGTcC4hrVRwMR4WteBywRqZWZEkdFpump: $100.00; liquidity filter and second observation
