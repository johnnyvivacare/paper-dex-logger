#!/usr/bin/env python3
"""Separate opportunity paper experiment. Public data only; never submits trades."""
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


# Strategy rules are experimental hypotheses, not predicted returns.
CONFIG.update({"strategy": "opportunity-v1", "entry_score": 65,
               "rotation_gap": 20, "min_hold": 1800, "rotation_cooldown": 1800})
EXCLUDED = {"So11111111111111111111111111111111111111112",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"}

def signed(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None

def observation(pair, token, now, pool=None):
    q = quote(pair, token, pool)
    if not q:
        return None
    tx = (pair.get("txns") or {}).get("m5") or {}
    fields = [number(tx.get("buys")), number(tx.get("sells")),
              number((pair.get("volume") or {}).get("m5")),
              signed((pair.get("priceChange") or {}).get("m5")),
              number(pair.get("pairCreatedAt"))]
    return dict(q, ts=now, buys=fields[0], sells=fields[1],
                volume=fields[2], change=fields[3], created=fields[4])

def rating(current, samples, now):
    if any(current.get(k) is None for k in ("buys", "sells", "volume", "change", "created")):
        return None, False
    previous = [x for x in samples if x["pool"] == current["pool"]
                and 60 <= now - x["ts"] <= 900 and x.get("volume") is not None]
    if not previous:
        return None, False
    old = max(previous, key=lambda x: x["ts"])
    count = current["buys"] + current["sells"]
    ratio = current["buys"] / max(1, count)
    momentum = current["price"] / old["price"] - 1
    growth = current["volume"] / max(old["volume"], 1) - 1
    liquidity_change = current["liquidity"] / old["liquidity"] - 1
    clamp = lambda x: max(0, min(1, x))
    score = round(35 * clamp((ratio - .5) / .25)
                  + 25 * clamp(momentum / .05)
                  + 20 * clamp(growth / .25)
                  + 10 * clamp(current["liquidity"] / 200000)
                  + 10 * clamp(count / 100), 2)
    age = now - current["created"] / 1000
    eligible = (1800 <= age <= 72 * 3600 and current["liquidity"] >= 50000
                and current["volume"] >= 5000 and count >= 20 and ratio >= .55
                and 0 < current["change"] <= 20 and 0 < momentum <= .20
                and liquidity_change >= -.10 and score >= CONFIG["entry_score"])
    return score, eligible

def close_position(state, token, q, now, reason):
    p = state["positions"].pop(token)
    value = sale_value(p["units"], q)
    state["cash"] += value
    state["realized"] += value - p["cost"]
    state["sold"][token] = now
    state["trades"].append(dict(side="sell", token=token, ts=now, usd=value,
                               pnl=value-p["cost"], reason=reason, pool=p["pool"]))

def open_position(state, token, q, score, now):
    cost = CONFIG["size"]
    p = dict(pool=q["pool"], entered=now, cost=cost, units=entry_units(cost, q),
             previous_quote=now, entry_score=score)
    mark(p, q, now)
    state["positions"][token] = p
    state["cash"] -= cost
    state["trades"].append(dict(side="buy", token=token, ts=now, usd=cost,
                               score=score, pool=q["pool"]))

def allocate(state, observations, ranked, now, errors):
    # Never sell because of absent data or finance an entry from an unpriced holding.
    if errors:
        return
    for score, token in sorted(ranked, reverse=True):
        if token in state["positions"] or now-state["sold"].get(token, 0) < 3600:
            continue
        if len(state["positions"]) < CONFIG["slots"] and state["cash"] >= CONFIG["size"]:
            open_position(state, token, observations[token], score, now)
            continue
        if now-state["last_rotation"] < CONFIG["rotation_cooldown"]:
            continue
        weak = [(p["score"], t) for t,p in state["positions"].items()
                if t in observations and p.get("score") is not None
                and now-p["entered"] >= CONFIG["min_hold"]
                and state["cash"]+sale_value(p["units"], observations[t]) >= CONFIG["size"]]
        if not weak:
            continue
        weakest, old = min(weak)
        if score < weakest + CONFIG["rotation_gap"]:
            continue
        close_position(state, old, observations[old], now, "rotation: stronger score")
        open_position(state, token, observations[token], score, now)
        state["last_rotation"] = now

def cycle(state):
    errors, observations, ranked = [], {}, []
    # Fixed pools for open positions; fetch them before candidate discovery.
    for token,p in list(state["positions"].items()):
        data = safe_fetch("/latest/dex/pairs/solana/"+p["pool"], errors)
        pairs = data.get("pairs") if isinstance(data, dict) else None
        current = None
        for pair in pairs or []:
            current = observation(pair, token, int(time.time()), p["pool"])
            if current:
                break
        if current is None:
            p["status"] = "unresolved: no usable pool quote"
            continue
        observations[token] = current
        mark(p, current, current["ts"])
        reason = exit_reason(p, current["ts"])
        if reason:
            close_position(state, token, current, current["ts"], reason)
        time.sleep(.25)
    tokens = set()
    for endpoint in ("/token-profiles/latest/v1", "/token-boosts/latest/v1"):
        data = safe_fetch(endpoint, errors)
        if not isinstance(data, list):
            errors.append("Discovery unavailable: "+endpoint)
            continue
        for item in data:
            t = item.get("tokenAddress") if isinstance(item, dict) else None
            if isinstance(item,dict) and item.get("chainId") == "solana" and isinstance(t,str) and ADDR.fullmatch(t):
                tokens.add(t)
    # Cap requests; revisit least recently scanned tokens first.
    candidates = sorted(tokens-EXCLUDED-set(observations),
                        key=lambda t: (state["scanned"].get(t, 0), t))[:30]
    for token in candidates:
        # An unresolved held token must never switch to a different pool.
        if token in state["positions"]:
            continue
        data = safe_fetch("/token-pairs/v1/solana/"+token, errors)
        now = int(time.time())
        state["scanned"][token] = now
        if not isinstance(data,list):
            errors.append("Candidate pairs unavailable: "+token)
            continue
        choices = [observation(p,token,now) for p in data]
        choices = [q for q in choices if q and q["liquidity"] >= 50000]
        if choices:
            observations[token] = max(choices, key=lambda q:q["liquidity"])
        time.sleep(.25)
    now = int(time.time())
    for token,q in observations.items():
        samples = state["samples"].get(token, [])
        score, eligible = rating(q, samples, q["ts"])
        if token in state["positions"]:
            state["positions"][token]["score"] = score
        # Quotes gathered early in a slow cycle cannot fund a rotation.
        if now-q["ts"] > 60:
            if token in state["positions"]:
                state["positions"][token]["score"] = None
            continue
        if eligible:
            ranked.append((score, token))
        state["samples"][token] = (samples+[q])[-40:]
    allocate(state, observations, ranked, now, errors)
    state["samples"] = {t:s for t,s in state["samples"].items() if s and now-s[-1]["ts"] < 3600}
    state["scanned"] = {t:ts for t,ts in state["scanned"].items() if now-ts < 86400}
    state["cycles"] += 1
    state["last_run"], state["errors"] = now, errors
    fresh, stale, unresolved = totals(state,now)
    state["history"].append(dict(ts=now,cash=state["cash"],fresh_estimate=fresh,
                                stale_estimate=stale,unresolved=unresolved))
    state["ranked"] = sorted(ranked,reverse=True)[:10]

def report(state, now):
    fresh, stale, unresolved = totals(state,now)
    lines = ["# Opportunity paper experiment — $500 USD", "",
             "Started: "+stamp(state["started"]), "Last collection: "+stamp(state["last_run"]),
             "Cycles: "+str(state["cycles"]), "",
             "| Item | USD |", "|---|---:|",
             "| Cash | %.2f |" % state["cash"],
             "| Realized simulated P/L | %+.2f |" % state["realized"],
             "| Recent estimated position value | %.2f |" % fresh,
             "| Unresolved last marks (not cash) | %.2f |" % stale, "",
             "Open positions: %s; unresolved: %s." % (len(state["positions"]),unresolved)]
    if not unresolved:
        lines.append("Estimated equity: $%.2f; estimated P/L: $%+.2f." %
                     (state["cash"]+fresh,state["cash"]+fresh-500))
    else:
        lines.append("Total equity is uncertain because some positions are unresolved.")
    lines += ["", "## Positions", "", "| Token | Entry score | Current score |",
              "|---|---:|---:|"]
    for t,p in state["positions"].items():
        lines.append("| %s | %s | %s |" % (t,p["entry_score"],p.get("score")))
    lines += ["", "## Recent trades", ""]
    for tr in state["trades"][-10:]:
        lines.append("- %s %s %s: $%.2f (%s)" %
                     (stamp(tr["ts"]),tr["side"],tr["token"],tr["usd"],
                      tr.get("reason","score "+str(tr.get("score")))))
    lines += ["", "Experimental score, NOT a probability of profit. Profiles/boosts are a limited promotional sample, not all new tokens or verified memes.",
              "Pairs aged 30 minutes–72 hours; reported liquidity >=$50k; 5m volume >=$5k; buying and positive momentum required. Missing fields or history prevent entry.",
              "$50 entries, 10 slots maximum. Hold cash if no candidates qualify. Exit at observed +100%, -50%, or 24 hours. Rotate only after 30 minutes held, a 20-point score advantage, and a 30-minute rotation cooldown. One-hour token reentry cooldown.",
              "Paper only; no wallet, signing, or transactions. Same approximate pool-impact and cost model as the baseline: 0.3% fee, $0.01 gas, 0.5% extra slippage each side. No executable swap quotes, sellability checks, or rug prediction.",
              "Unavailable prices remain unresolved, not assumed sales. GitHub scheduling and API delays create monitoring gaps. Compare returns from matching timestamps, not different start balances/dates.", ""]
    lines += ["Errors: "+str(len(state["errors"]))] + ["- "+e for e in state["errors"]]
    return "\n".join(lines)+"\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="opportunity-data")
    args = parser.parse_args()
    directory = Path(args.data)
    path = directory/"state.json"
    state = load(path,int(time.time()))
    for key,default in (("samples",{}),("scanned",{}),("sold",{}),("last_rotation",0)):
        state.setdefault(key,default)
    cycle(state)
    save(path,state)
    output = report(state,int(time.time()))
    (directory/"REPORT.md").write_text(output)
    print(output)

if __name__ == "__main__":
    main()
