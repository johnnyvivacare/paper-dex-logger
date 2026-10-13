# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-13 23:28 UTC
Cycles: 2629

| Item | USD |
|---|---:|
| Paper cash | 34.90 |
| Realised simulated P/L | -765.10 |
| Open positions, recent estimated sale value | 221.58 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 2; unresolved: 0.
Estimated paper equity: $256.47; estimated P/L: $-743.53.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $256.47
Maximum observed portfolio decline since upgrade: 81.93%
Latest / largest saved-cycle gap: 30s / 2331s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 21.1779 |
| Gas | 0.7800 |
| Pool impact | 17.0464 |
| Extra slippage | 35.1409 |
| Total entry + exit drag | 74.1452 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-12 22:08:05 UTC buy CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump: $100.00; liquidity filter and second observation
- 2026-10-13 01:07:13 UTC sell CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump: $202.95; take profit
- 2026-10-13 01:07:13 UTC buy 7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump: $100.00; liquidity filter and second observation
- 2026-10-13 03:24:50 UTC buy 8sWe4GzK1YqG3vyzKHf8ZyB1WB5asofw2o6TqgFePtPo: $100.00; liquidity filter and second observation
- 2026-10-13 10:43:44 UTC sell 7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump: $136.14; trailing pullback
- 2026-10-13 10:43:45 UTC buy 83xGH23oFrEFsovtpnEYPHc4iYvtyVpquwV91A8bYuRu: $100.00; liquidity filter and second observation
- 2026-10-13 12:18:41 UTC sell 8sWe4GzK1YqG3vyzKHf8ZyB1WB5asofw2o6TqgFePtPo: $112.28; reported liquidity drop
- 2026-10-13 12:52:24 UTC buy HCkhfdDNF2dqMxxtL51AzgWU26MBNkUkEzGAHtqkpump: $100.00; liquidity filter and second observation
- 2026-10-13 13:48:46 UTC buy C54wJMbzGCHrHfPAmLyrJNSEgtQ7CmhbQeh5fGhpump: $100.00; liquidity filter and second observation
- 2026-10-13 14:37:54 UTC sell C54wJMbzGCHrHfPAmLyrJNSEgtQ7CmhbQeh5fGhpump: $0.19; stop loss
