# paper-dex-logger

**Paper only.** Nothing in this repository can trade. There is no wallet, no private key,
no exchange credential. Every ~15 minutes a GitHub Action polls DexScreener's public API for
freshly listed tokens, scores each with `rugscan.py`, snapshots price / liquidity / volume for
every token seen in the last 48 h, and appends the rows to `data/*.jsonl`.

`python3 dexlog.py report --jsonl data` replays **pre-registered** rules against that log,
with a hypothetical $500 budget, $50 per position, 10 slots, real DEX fees, gas, and price
impact. A token that vanishes from the API or whose liquidity hits zero is worth $0.
Rules and their registration dates are in the docstring of `dexlog.py`. The yardstick printed
alongside is $500 simply held in SOL over the same window.
