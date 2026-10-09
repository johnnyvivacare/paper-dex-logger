# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-09 15:29 UTC
Cycles: 326

| Item | USD |
|---|---:|
| Paper cash | 524.93 |
| Realised simulated P/L | -275.07 |
| Open positions, recent estimated sale value | 144.27 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 2; unresolved: 0.
Estimated paper equity: $669.20; estimated P/L: $-330.80.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $669.20
Maximum observed portfolio decline since upgrade: 33.35%
Latest / largest saved-cycle gap: 29s / 1506s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 5.1898 |
| Gas | 0.2000 |
| Pool impact | 5.0729 |
| Extra slippage | 8.6075 |
| Total entry + exit drag | 19.0702 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-09 03:47:05 UTC sell k3TjSYCXLPMZBajZGNhAG3ccuE7L3PYMdPFifZqpump: $0.70; stop loss
- 2026-10-09 04:04:12 UTC sell HMYd9tosnUXuNHmq7pXmoePRVBLBBjA3JBfydq6upump: $109.82; trailing pullback
- 2026-10-09 06:36:22 UTC buy 8TiMkgvsrat9tM2esko8zVTt99LZLpefUM4SnZaziXaQ: $100.00; liquidity filter and second observation
- 2026-10-09 07:27:17 UTC sell 8TiMkgvsrat9tM2esko8zVTt99LZLpefUM4SnZaziXaQ: $156.07; trailing pullback
- 2026-10-09 08:06:01 UTC buy 9XKzy4KahcZaGJPJtz1PtqGPB3CiseoBrx7TcQhEpump: $100.00; liquidity filter and second observation
- 2026-10-09 10:19:28 UTC buy CDFAVmJZK1eGoF3KxGa8yNVaSQDoRoAQnBNSGcjhpump: $100.00; liquidity filter and second observation
- 2026-10-09 10:58:26 UTC sell CDFAVmJZK1eGoF3KxGa8yNVaSQDoRoAQnBNSGcjhpump: $0.48; stop loss
- 2026-10-09 14:26:19 UTC buy 9vHPLDY6wa9ZkNBNZoWcv2AABdiNj97tpHc3u56npump: $100.00; liquidity filter and second observation
- 2026-10-09 14:53:44 UTC sell 9vHPLDY6wa9ZkNBNZoWcv2AABdiNj97tpHc3u56npump: $107.74; trailing pullback
- 2026-10-09 15:27:42 UTC sell 9XKzy4KahcZaGJPJtz1PtqGPB3CiseoBrx7TcQhEpump: $109.36; trailing pullback
