#!/usr/bin/env python3
"""Solana paper experiment v2. Public data only; no wallet or trading API.
Compatible with: python3 dexlog.py cycle --jsonl data
Report: python3 dexlog.py report --jsonl data
Old JSONL logs are preserved. New state is data/paper_v2.json.
"""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import time
import urllib.request

API = "https://api.dexscreener.com"
ADDR = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
CONFIG = {
    "budget": 500.0, "size": 50.0, "slots": 10,
    "min_liquidity": 50000.0,
    "take_profit": 1.0, "stop_loss": -0.5, "max_hold_hours": 24,
    "fee": 0.003, "gas": 0.01, "extra_slippage": 0.005,
    "stale_seconds": 1800, "pending_seconds": 7200,
}
# Fees, gas and impact are MODEL ASSUMPTIONS, not executable swap quotes.


def stamp(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (TypeError, ValueError):
        return None


def fetch(path):
    for attempt in range(3):
        try:
            req = urllib.request.Request(API + path, headers={"User-Agent": "paper-study/2"})
            with urllib.request.urlopen(req, timeout=12) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def safe_fetch(path, errors):
    try:
        return fetch(path)
    except Exception as exc:
        errors.append(path + ": " + type(exc).__name__)
        return None


def new_state(now):
    return {
        "version": 2, "started": now, "config": dict(CONFIG),
        "cash": CONFIG["budget"], "realized": 0.0,
        "positions": {}, "pending": {}, "seen": {},
        "trades": [], "cycles": 0, "last_run": None,
        "errors": [], "history": [],
    }


def load(path, now):
    if not path.exists():
        return new_state(now)
    state = json.loads(path.read_text())
    if state.get("version") != 2 or state.get("config") != CONFIG:
        raise ValueError("State/config mismatch. Do not overwrite the existing experiment.")
    return state


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as handle:
        json.dump(state, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def quote(pair, token, pool=None):
    if not isinstance(pair, dict) or pair.get("chainId") != "solana":
        return None
    if (pair.get("baseToken") or {}).get("address") != token:
        return None  # Solana addresses are case-sensitive.
    address = pair.get("pairAddress", "")
    if not isinstance(address, str) or not ADDR.fullmatch(address):
        return None
    if pool is not None and address != pool:
        return None
    price = number(pair.get("priceUsd"))
    liquidity = number((pair.get("liquidity") or {}).get("usd"))
    if not price or not liquidity:
        return None
    return {"price": price, "liquidity": liquidity, "pool": address}


def pool_quote(token, pool, errors):
    result = safe_fetch("/latest/dex/pairs/solana/" + pool, errors)
    if result is None:
        return None, "API error"
    if not isinstance(result, dict) or not isinstance(result.get("pairs"), list):
        errors.append("Malformed pair response: " + pool)
        return None, "invalid response"
    for pair in result["pairs"]:
        q = quote(pair, token, pool)
        if q:
            return q, "observed"
    return None, "pool missing or price/liquidity unavailable"


def entry_units(cost, q):
    net = max((cost - CONFIG["gas"]) * (1 - CONFIG["fee"]), 0)
    reserve = q["liquidity"] / 2
    return net / (1 + net / reserve) / q["price"] * (1 - CONFIG["extra_slippage"])


def sale_value(units, q):
    gross = units * q["price"]
    reserve = q["liquidity"] / 2
    estimated = gross / (1 + gross / reserve)
    return max(estimated * (1 - CONFIG["fee"]) *
               (1 - CONFIG["extra_slippage"]) - CONFIG["gas"], 0)


def mark(position, q, now):
    position["mark"] = sale_value(position["units"], q)
    position["last_quote"] = now
    position["status"] = "observed"


def exit_reason(position, now):
    change = position["mark"] / position["cost"] - 1
    if change >= CONFIG["take_profit"]:
        return "take profit"
    if change <= CONFIG["stop_loss"]:
        return "stop loss"
    if now - position["entered"] >= CONFIG["max_hold_hours"] * 3600:
        return "time limit"
    return None


def totals(state, now):
    fresh = stale = 0.0
    unresolved = 0
    for p in state["positions"].values():
        if p["status"] != "observed" or now - p["last_quote"] > CONFIG["stale_seconds"]:
            stale += p["mark"]
            unresolved += 1
        else:
            fresh += p["mark"]
    return fresh, stale, unresolved


def cycle(state):
    errors = []
    # Existing positions always get priority and never age off the watchlist.
    for token, p in list(state["positions"].items()):
        q, status = pool_quote(token, p["pool"], errors)
        observed = int(time.time())
        if q is None:
            p["status"] = status
            continue  # Cannot infer a loss or execute an exit without a usable quote.
        mark(p, q, observed)
        reason = exit_reason(p, observed)
        if reason:
            proceeds = p["mark"]
            state["cash"] += proceeds
            state["realized"] += proceeds - p["cost"]
            state["trades"].append({
                "side": "sell", "ts": observed, "token": token, "pool": p["pool"],
                "usd": proceeds, "pnl": proceeds - p["cost"], "reason": reason,
                "quote": q, "entry_ts": p["entered"],
                "observation_gap_seconds": observed - p.get("previous_quote", p["entered"]),
            })
            del state["positions"][token]
        else:
            p["previous_quote"] = observed
        time.sleep(0.25)

    # A candidate must be observed again in a later cycle before paper entry.
    # It must still have the same pool and adequate reported liquidity.
    for token, candidate in list(state["pending"].items()):
        now = int(time.time())
        if now - candidate["discovered"] > CONFIG["pending_seconds"]:
            del state["pending"][token]
            continue
        if errors or len(state["positions"]) >= CONFIG["slots"] or state["cash"] < CONFIG["size"]:
            continue
        if now - candidate["discovered"] < 60:
            continue
        q, status = pool_quote(token, candidate["pool"], errors)
        if q is None or q["liquidity"] < CONFIG["min_liquidity"]:
            continue
        now = int(time.time())
        cost = CONFIG["size"]
        position = {
            "pool": q["pool"], "entered": now, "cost": cost,
            "units": entry_units(cost, q), "previous_quote": now,
        }
        mark(position, q, now)
        state["positions"][token] = position
        state["cash"] -= cost
        state["trades"].append({
            "side": "buy", "ts": now, "token": token, "pool": q["pool"],
            "usd": cost, "quote": q, "discovered": candidate["discovered"],
        })
        del state["pending"][token]
        time.sleep(0.25)

    # Profiles and boosts are a limited/promotional discovery sample,
    # NOT all new tokens and NOT a verified list of memecoins.
    discovered = set()
    for endpoint in ("/token-profiles/latest/v1", "/token-boosts/latest/v1"):
        result = safe_fetch(endpoint, errors)
        if result is None:
            continue
        if not isinstance(result, list):
            errors.append("Invalid discovery response: " + endpoint)
            continue
        for item in result:
            if not isinstance(item, dict):
                continue
            token = item.get("tokenAddress")
            if item.get("chainId") == "solana" and isinstance(token, str) and ADDR.fullmatch(token):
                discovered.add(token)
        time.sleep(1.1)

    # At most 10 candidates await a second observation; no repeated token entries.
    if not errors:
        for token in sorted(discovered):
            if len(state["pending"]) >= CONFIG["slots"]:
                break
            if token in state["seen"]:
                continue
            result = safe_fetch("/token-pairs/v1/solana/" + token, errors)
            if result is None:
                break
            if not isinstance(result, list):
                errors.append("Invalid token-pairs response")
                break
            choices = [q for pair in result if (q := quote(pair, token)) is not None]
            state["seen"][token] = int(time.time())
            choices = [q for q in choices if q["liquidity"] >= CONFIG["min_liquidity"]]
            if choices:
                best = max(choices, key=lambda q: (q["liquidity"], q["pool"]))
                state["pending"][token] = {
                    "pool": best["pool"], "discovered": int(time.time()),
                }
            time.sleep(0.25)

    now = int(time.time())
    state["cycles"] += 1
    state["last_run"] = now
    state["errors"] = errors
    fresh, stale, unresolved = totals(state, now)
    state["history"].append({
        "ts": now, "cash": state["cash"], "realized": state["realized"],
        "fresh_estimate": fresh, "stale_estimate": stale, "unresolved": unresolved,
        "open": len(state["positions"]), "errors": errors,
    })


def report(state, now):
    fresh, stale, unresolved = totals(state, now)
    last = stamp(state["last_run"]) if state["last_run"] else "not collected yet"
    lines = [
        "# Solana paper test — $500 USD",
        "",
        "Started: " + stamp(state["started"]),
        "Last collection: " + last,
        "Cycles: " + str(state["cycles"]),
        "",
        "| Item | USD |", "|---|---:|",
        "| Paper cash | %.2f |" % state["cash"],
        "| Realised simulated P/L | %+.2f |" % state["realized"],
        "| Open positions, recent estimated sale value | %.2f |" % fresh,
        "| Unresolved positions, last estimated value ONLY | %.2f |" % stale,
        "",
        "Open positions: %d; unresolved: %d." % (len(state["positions"]), unresolved),
    ]
    if unresolved:
        lines.append("Total portfolio value is uncertain. Stale estimates are not available cash.")
    else:
        total = state["cash"] + fresh
        lines.append("Estimated paper equity: $%.2f; estimated P/L: $%+.2f." %
                     (total, total - CONFIG["budget"]))
    lines += [
        "",
        "Rule: Solana profiles/boosts; reported liquidity >= $50,000; "
        "$50 per entry; at most 10 positions; one entry per token. "
        "Confirm the same pool on a later cycle before buying.",
        "Exit at an observed estimated +100%, -50%, or after 24 hours. "
        "Exits use the next available observation, not an assumed stop fill.",
        "",
        "All sales and P/L are hypothetical. No sellability checks or swap quotes. "
        "Reported liquidity may be misleading. The pool-impact formula, 0.3% fee, "
        "$0.01 gas and 0.5% extra slippage per side are assumptions.",
        "USD is the accounting currency; this model does not hold a SOL reserve "
        "or simulate SOL-to-token routing. Old experiment logs are retained.",
        "",
    ]
    if state["errors"]:
        lines += ["Latest collection was incomplete:"] + ["- " + e for e in state["errors"]]
    else:
        lines.append("No request errors recorded in the latest cycle.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["cycle", "report"], nargs="?", default="report")
    parser.add_argument("--jsonl", default="data", help="existing workflow data folder")
    args = parser.parse_args()
    directory = Path(args.jsonl)
    path = directory / "paper_v2_run2.json"
    if args.command == "report" and not path.exists():
        print("V2 has not started. Its first successful cycle creates the separate $500 account.")
        return
    state = load(path, int(time.time()))
    if args.command == "cycle":
        cycle(state)
        save(path, state)
    output = report(state, int(time.time()))
    if args.command == "cycle":
        (directory / "REPORT.md").write_text(output)
    print(output)


if __name__ == "__main__":
    main()
