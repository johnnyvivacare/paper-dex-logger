# Solana paper test — $500 USD

Started: 2026-10-07 21:37 UTC
Last collection: 2026-10-08 08:53 UTC
Cycles: 271

| Item | USD |
|---|---:|
| Paper cash | 40.76 |
| Realised simulated P/L | -109.24 |
| Open positions, recent estimated sale value | 356.56 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 7; unresolved: 0.
Estimated paper equity: $397.32; estimated P/L: $-102.68.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $50 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-08 06:06:30 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $396.30
Current equity with quotes <=120s old: $397.32
Maximum observed portfolio decline since upgrade: 4.31%
Latest / largest saved-cycle gap: 30s / 1435s.
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
10% drawdown from the preceding 24h observed equity peak pauses new entries for 6h; existing exits continue. A continuing breach can renew the pause.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-07 23:00:00 UTC sell 8gtnEi3QyW1Y1HgDLQWs1dQahEbNiCBtY7wZcbXZpump: $19.34; stop loss; pre-upgrade
- 2026-10-08 01:49:06 UTC buy HXqxTwCzREUXNK4CbNDgNEUEh2jLzFKdC4tvTuojpump: $50.00; liquidity filter and second observation; pre-upgrade
- 2026-10-08 03:26:32 UTC sell HXqxTwCzREUXNK4CbNDgNEUEh2jLzFKdC4tvTuojpump: $100.41; take profit; pre-upgrade
- 2026-10-08 03:26:32 UTC buy 6Mix12LiHrQFojaQEnfPUC65Qkwd6X4Y5Qg93oFbordr: $50.00; liquidity filter and second observation; pre-upgrade
- 2026-10-08 03:28:02 UTC buy FtQLXvPbWo8Gs2XsHkRZd1ihgjgRaojZ2HwARL2gpump: $50.00; liquidity filter and second observation; pre-upgrade
- 2026-10-08 03:45:04 UTC sell 6Mix12LiHrQFojaQEnfPUC65Qkwd6X4Y5Qg93oFbordr: $23.78; stop loss; pre-upgrade
- 2026-10-08 03:45:05 UTC sell FtQLXvPbWo8Gs2XsHkRZd1ihgjgRaojZ2HwARL2gpump: $0.33; stop loss; pre-upgrade
- 2026-10-08 04:02:17 UTC sell CWKbSd7jwMXXexP3pbwLAWMzr4HXAXTvt4R9pk2Vyyyc: $22.01; stop loss; pre-upgrade
- 2026-10-08 04:26:24 UTC buy 5tCju6YNxHq5zrA6tGndr6F7TK42mpUFmeE31cSFpump: $50.00; liquidity filter and second observation; pre-upgrade
- 2026-10-08 05:24:54 UTC sell 9XKzy4KahcZaGJPJtz1PtqGPB3CiseoBrx7TcQhEpump: $24.89; stop loss; pre-upgrade
