# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-18 08:57 UTC
Cycles: 4168

| Item | USD |
|---|---:|
| Paper cash | 64.73 |
| Realised simulated P/L | -935.27 |
| Open positions, recent estimated sale value | 0.00 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 0; unresolved: 0.
Estimated paper equity: $64.73; estimated P/L: $-935.27.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $64.73
Maximum observed portfolio decline since upgrade: 93.53%
Latest / largest saved-cycle gap: 30s / 2966s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 24.2803 |
| Gas | 0.9000 |
| Pool impact | 19.4799 |
| Extra slippage | 40.2901 |
| Total entry + exit drag | 84.9504 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-14 12:52:26 UTC sell HCkhfdDNF2dqMxxtL51AzgWU26MBNkUkEzGAHtqkpump: $93.72; time limit
- 2026-10-14 12:53:57 UTC buy GZw7LxHtQKSQ1YsGnpNH7SovnBF8X6poYgavHwrmRekp: $100.00; liquidity filter and second observation
- 2026-10-15 03:05:08 UTC sell GZw7LxHtQKSQ1YsGnpNH7SovnBF8X6poYgavHwrmRekp: $61.83; reported liquidity drop
- 2026-10-15 11:26:35 UTC sell HKZDfZnkHZxd9agRDNPyDv4iT6LmAurJnpRtj9wpump: $114.09; time limit
- 2026-10-15 11:26:35 UTC buy 4crYPsDdW4cDLHsa5nNEuNJHrhDZKssuK25nmAZ4uHz3: $100.00; liquidity filter and second observation
- 2026-10-15 11:28:05 UTC buy 2ay4jNY3JxfuXJzhZ8DrAKkGzpirgD7Dv2ccL9zmpump: $100.00; liquidity filter and second observation
- 2026-10-15 15:25:54 UTC sell 2ay4jNY3JxfuXJzhZ8DrAKkGzpirgD7Dv2ccL9zmpump: $49.79; stop loss
- 2026-10-16 11:50:06 UTC sell 4crYPsDdW4cDLHsa5nNEuNJHrhDZKssuK25nmAZ4uHz3: $102.38; time limit
- 2026-10-16 11:50:06 UTC buy pFibPnQk8ekCCtuBoQFJqeJjHVo92dAME3uH8A4pump: $100.00; liquidity filter and second observation
- 2026-10-16 13:08:04 UTC sell pFibPnQk8ekCCtuBoQFJqeJjHVo92dAME3uH8A4pump: $0.14; stop loss
