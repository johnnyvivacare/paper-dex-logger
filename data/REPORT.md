# Solana paper test — $1,000 USD

Started: 2026-10-09 00:41 UTC
Last collection: 2026-10-10 00:31 UTC
Cycles: 538

| Item | USD |
|---|---:|
| Paper cash | 27.69 |
| Realised simulated P/L | -272.31 |
| Open positions, recent estimated sale value | 629.18 |
| Unresolved positions, last estimated value ONLY | 0.00 |

Open positions: 7; unresolved: 0.
Estimated paper equity: $656.87; estimated P/L: $-343.13.

Rule: Solana profiles/boosts; reported liquidity >= $50,000; $100 per entry; at most 10 positions; one entry per token. Confirm the same pool on a later cycle before buying.
Exit at an observed estimated +100%, -50%, or after 24 hours. Exits use the next available observation, not an assumed stop fill.

All sales and P/L are hypothetical. No sellability checks or swap quotes. Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, $0.01 gas and 0.5% extra slippage per side are assumptions.
USD is the accounting currency; this model does not hold a SOL reserve or simulate SOL-to-token routing. Old experiment logs are retained.

No request errors recorded in the latest cycle.

## Controls upgrade controls-1

Enabled: 2026-10-09 00:41:02 UTC. Existing balance and history preserved.
Metrics below cover only the period since this upgrade.
Initial valued equity: $1000.00
Current equity with quotes <=120s old: $656.87
Maximum observed portfolio decline since upgrade: 40.70%
Latest / largest saved-cycle gap: 1769s / 1769s.
Cycles with uncertain equity: 0.
New entries: allowed by controls

### Modeled costs since upgrade

| Component | USD |
|---|---:|
| Fees | 9.1077 |
| Gas | 0.3300 |
| Pool impact | 8.7291 |
| Extra slippage | 15.1058 |
| Total entry + exit drag | 33.2726 |

Costs above are assumptions already included in P/L, not extra charges or actual swap fees.
Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.
Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.
Loss-based entry pause: DISABLED for this paper experiment. Qualifying purchases continue after drawdowns; entry filters, data checks and exit rules still apply.
Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.
Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.

### Latest decisions

- 2026-10-09 17:37:05 UTC buy AyYNfPtftg2zDP4ZbgcoQMggQtwLh4zpfVVmUJs2thto: $100.00; liquidity filter and second observation
- 2026-10-09 18:57:45 UTC buy ripsRNKEFLPkf7E8pLYcbxWcxDdgtNBDQgqKkEDCvnG: $100.00; liquidity filter and second observation
- 2026-10-09 19:16:44 UTC sell ripsRNKEFLPkf7E8pLYcbxWcxDdgtNBDQgqKkEDCvnG: $55.38; reported liquidity drop
- 2026-10-09 19:56:52 UTC buy 258hQ12j9UeGdiEaJzYuMjrgPFbsveNuK72uVKAR3DQj: $100.00; liquidity filter and second observation
- 2026-10-09 19:56:53 UTC buy FfAYkFVhbm9oTYQpuRuJ6rTdVpCZy53qAKueRfrdpump: $100.00; liquidity filter and second observation
- 2026-10-09 20:11:23 UTC sell FfAYkFVhbm9oTYQpuRuJ6rTdVpCZy53qAKueRfrdpump: $201.71; take profit
- 2026-10-09 20:54:07 UTC buy 9ioR1eGM3ciCs2XZVsvyn5vr4u2M2JufeNQfVa7MiXRC: $100.00; liquidity filter and second observation
- 2026-10-09 21:33:01 UTC buy GfLKLVuhzNcLyQ3zF3fzXWsAU5R5PMCcDRVNmepMpump: $100.00; liquidity filter and second observation
- 2026-10-09 22:08:10 UTC sell GfLKLVuhzNcLyQ3zF3fzXWsAU5R5PMCcDRVNmepMpump: $46.38; stop loss
- 2026-10-09 22:51:22 UTC buy AW3iE4CyNtKj8QKoKSHDTkkAekZMhFxsjzA5dtbNaneg: $100.00; liquidity filter and second observation
