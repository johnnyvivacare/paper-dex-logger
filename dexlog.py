#!/usr/bin/env python3
"""Solana paper experiment v2. Public data only; no wallet or trading API.
Compatible with: python3 dexlog.py cycle --jsonl data
Report: python3 dexlog.py report --jsonl data
Old JSONL logs are preserved. Current state remains data/paper_v2_run2.json.
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
    ctrl_observe(position, q, now)


def exit_reason(position, now):
    change = position["mark"] / position["cost"] - 1
    if change >= CONFIG["take_profit"]:
        return "take profit"
    if change <= CONFIG["stop_loss"]:
        return "stop loss"
    extra_reason = ctrl_exit_reason(position)
    if extra_reason:
        return extra_reason
    if now - position["entered"] >= CONFIG["max_hold_hours"] * 3600:
        return "time limit"
    return None


def totals(state, now):
    fresh = stale = 0.0
    unresolved = 0
    for p in state["positions"].values():
        if p["status"] != "observed" or not 0 <= now - p["last_quote"] <= ctrl_RULES["quote_max_age"]:
            stale += p["mark"]
            unresolved += 1
        else:
            fresh += p["mark"]
    return fresh, stale, unresolved


def cycle(state):
    ctrl_begin(state, int(time.time()))
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
                "controls_version": ctrl_VERSION,
                "cost_estimate": ctrl_sell_costs(p["units"], proceeds, q, CONFIG),
                "observation_gap_seconds": observed - p.get("previous_quote", p["entered"]),
            })
            del state["positions"][token]
        else:
            p["previous_quote"] = observed
        time.sleep(0.25)

    # A candidate must be observed again in a later cycle before paper entry.
    # It must still have the same pool and adequate reported liquidity.
    ctrl_entries_allowed(state, int(time.time()), errors)
    for token, candidate in list(state["pending"].items()):
        now = int(time.time())
        if now - candidate["discovered"] > CONFIG["pending_seconds"]:
            del state["pending"][token]
            continue
        if (not ctrl_entries_allowed(state, now, errors)
                or len(state["positions"]) >= CONFIG["slots"] or state["cash"] < CONFIG["size"]):
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
            "controls_version": ctrl_VERSION,
            "cost_estimate": ctrl_buy_costs(cost, position["units"], q, CONFIG),
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
    ctrl_finish(state, now)


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
    return "\n".join(lines) + "\n" + ctrl_report(state, now)


# Embedded controls: keep this file standalone for GitHub uploads.
"""Shared paper-only controls. Independent implementation; no transaction APIs."""
import datetime as dt
import math

ctrl_VERSION = "controls-1"
ctrl_RULES = dict(trail_arm=.25, trail_drop=.20, liquidity_drop=.35,
             loss_pause_drawdown=.10, loss_window_seconds=86400,
             pause_seconds=21600, quote_max_age=120)

def ctrl_valuation(state, now):
    total = state["cash"]
    unresolved = 0
    for p in state["positions"].values():
        value = p.get("mark")
        if (p.get("status") != "observed" or not isinstance(value, (float, int))
                or not math.isfinite(value) or value < 0
                or not 0 <= now-p.get("last_quote", 0) <= ctrl_RULES["quote_max_age"]):
            unresolved += 1
        else:
            total += value
    return (None if unresolved else total), unresolved

def ctrl_begin(state, now):
    if "controls" not in state:
        state["controls"] = dict(
            version=ctrl_VERSION, rules=dict(ctrl_RULES), enabled_at=now,
            initial_cash=state["cash"], prior_trades=len(state["trades"]),
            prior_cycles=state["cycles"], initial_equity=None,
            equity_peak=None, max_drawdown=0., points=[], pause_until=0,
            pauses=[], last_cycle=None, last_gap=0, max_gap=0,
            blocked=[], costs=dict(entry=0., exit=0., fees=0., gas=0.,
                                   impact=0., slippage=0.),
            accounted_trades=len(state["trades"]), valued_cycles=0,
            unresolved_cycles=0)
        state.setdefault("upgrades", []).append(dict(
            version=ctrl_VERSION, ts=now, rules=dict(ctrl_RULES),
            cash=state["cash"], positions=len(state["positions"]),
            previous_trades=len(state["trades"])))
    c = state["controls"]
    if c["version"] != ctrl_VERSION or c["rules"] != ctrl_RULES:
        raise ValueError("Controls version mismatch; explicit migration required")
    return c

def ctrl_observe(p, q, now):
    # Called only after a usable quote. Never invent historical peaks.
    prior = p.get("controls_mark")
    net = p["mark"]
    if prior is None:
        prior = p["controls_mark"] = dict(
            since=now, peak_net=net, peak_liquidity=q["liquidity"],
            armed=False, last=now, max_gap=0)
    prior["max_gap"] = max(prior["max_gap"], now-prior["last"])
    prior["last"] = now
    prior["peak_net"] = max(prior["peak_net"], net)
    prior["peak_liquidity"] = max(prior["peak_liquidity"], q["liquidity"])
    prior["liquidity"] = q["liquidity"]
    if net >= p["cost"]*(1+ctrl_RULES["trail_arm"]):
        prior["armed"] = True

def ctrl_exit_reason(p):
    m = p.get("controls_mark")
    if not m:
        return None
    if m["liquidity"] <= m["peak_liquidity"]*(1-ctrl_RULES["liquidity_drop"]):
        return "reported liquidity drop"
    if m["armed"] and p["mark"] <= m["peak_net"]*(1-ctrl_RULES["trail_drop"]):
        return "trailing pullback"
    return None

def ctrl_checkpoint(state, now):
    c = ctrl_begin(state, now)
    equity, unresolved = ctrl_valuation(state, now)
    c["points"] = [p for p in c["points"] if now-p["ts"] <= ctrl_RULES["loss_window_seconds"]]
    if equity is not None:
        if c["initial_equity"] is None:
            c["initial_equity"] = equity
        peak = max([equity]+[p["equity"] for p in c["points"]])
        decline = 0 if peak <= 0 else 1-equity/peak
        if decline + 1e-12 >= ctrl_RULES["loss_pause_drawdown"] and now >= c["pause_until"]:
            c["pause_until"] = now+ctrl_RULES["pause_seconds"]
            c["pauses"].append(dict(ts=now, until=c["pause_until"],
                                   drawdown=decline, equity=equity))
        c["points"].append(dict(ts=now, equity=equity))
        c["equity_peak"] = max(equity, c["equity_peak"] or equity)
        if c["equity_peak"] > 0:
            c["max_drawdown"] = max(c["max_drawdown"], 1-equity/c["equity_peak"])
    return equity, unresolved

def ctrl_entries_allowed(state, now, errors):
    _, unresolved = ctrl_checkpoint(state, now)
    c = state["controls"]
    reasons = []
    if errors:
        reasons.append("request errors")
    if unresolved:
        reasons.append("unresolved or old position quotes")
    if now < c["pause_until"]:
        reasons.append("portfolio loss pause")
    c["blocked"] = reasons
    return not reasons

def ctrl_buy_costs(cost, units, q, config):
    gas = min(cost,config["gas"])
    fee = (cost-gas)*config["fee"]
    net = cost-gas-fee
    impacted = net/(1+net/(q["liquidity"]/2))
    slippage = impacted*config["extra_slippage"]
    return dict(total=cost-units*q["price"], fees=fee, gas=gas,
                impact=net-impacted, slippage=slippage)

def ctrl_sell_costs(units, proceeds, q, config):
    gross = units*q["price"]
    impacted = gross/(1+gross/(q["liquidity"]/2))
    fee = impacted*config["fee"]
    slippage = (impacted-fee)*config["extra_slippage"]
    gas = min(config["gas"], max(0, impacted-fee-slippage))
    return dict(total=gross-proceeds, fees=fee, gas=gas,
                impact=gross-impacted, slippage=slippage)

def ctrl_finish(state, now):
    c = ctrl_begin(state, now)
    equity, unresolved = ctrl_checkpoint(state, now)
    if c["last_cycle"] is not None:
        c["last_gap"] = max(0,now-c["last_cycle"])
        c["max_gap"] = max(c["max_gap"],c["last_gap"])
    c["last_cycle"] = now
    c["unresolved_cycles" if unresolved else "valued_cycles"] += 1
    for trade in state["trades"][c["accounted_trades"]:]:
        costs = trade.get("cost_estimate")
        if costs:
            c["costs"]["entry" if trade["side"] == "buy" else "exit"] += costs["total"]
            for k in ("fees","gas","impact","slippage"):
                c["costs"][k] += costs[k]
    c["accounted_trades"] = len(state["trades"])
    state["history"][-1].update(controls_version=ctrl_VERSION, observed_equity=equity,
                                entries_blocked=list(c["blocked"]))
    # Log one decision per cycle; all older trade records remain unchanged.
    c["last_value"], c["unresolved"] = equity, unresolved

def ctrl_utc(ts):
    return dt.datetime.fromtimestamp(ts,dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def ctrl_report(state, now):
    c = state.get("controls")
    if not c:
        return "\nControls upgrade has not run yet.\n"
    equity, unresolved = ctrl_valuation(state, now)
    paused = now<c["pause_until"]
    costs = c["costs"]
    lines = ["", "## Controls upgrade "+ctrl_VERSION, "",
             "Enabled: "+ctrl_utc(c["enabled_at"])+". Existing balance and history preserved.",
             "Metrics below cover only the period since this upgrade.",
             "Initial valued equity: "+("unavailable" if c["initial_equity"] is None
                                       else "$%.2f" % c["initial_equity"]),
             "Current equity with quotes <=120s old: "+
             ("uncertain (%d unresolved/old quotes)" % unresolved if equity is None
              else "$%.2f" % equity),
             "Maximum observed portfolio decline since upgrade: %.2f%%" % (100*c["max_drawdown"]),
             "Latest / largest saved-cycle gap: %ss / %ss." % (c["last_gap"],c["max_gap"]),
             "Cycles with uncertain equity: %s." % c["unresolved_cycles"],
             "New entries: "+("PAUSED until "+ctrl_utc(c["pause_until"]) if paused else
                               ("blocked: "+", ".join(c["blocked"]) if c["blocked"] else "allowed by controls")),
             "", "### Modeled costs since upgrade", "",
             "| Component | USD |", "|---|---:|",
             "| Fees | %.4f |" % costs["fees"],
             "| Gas | %.4f |" % costs["gas"],
             "| Pool impact | %.4f |" % costs["impact"],
             "| Extra slippage | %.4f |" % costs["slippage"],
             "| Total entry + exit drag | %.4f |" % (costs["entry"]+costs["exit"]),
             "", "Costs above are assumptions already included in P/L, not extra charges or actual swap fees.",
             "Trailing exit: arms at +25% net, triggers on 20% pullback from the observed net peak.",
             "Reported liquidity exit: 35% decline from the observed liquidity peak. A USD liquidity drop is not proof of a rug.",
             "10% drawdown from the preceding 24h observed equity peak pauses new entries for 6h; existing exits continue. A continuing breach can renew the pause.",
             "Original +100% target, -50% stop and 24h holding limit remain. Fills use the next observed estimated sale value; thresholds never guarantee proceeds.",
             "Observed peaks, drawdown and costs start at upgrade time. Gaps can hide larger losses and peaks. Missing prices never count as completed sales.",
             "", "### Latest decisions", ""]
    for t in state["trades"][-10:]:
        reason = t.get("reason")
        if not reason:
            reason = "opportunity score "+str(t["score"]) if "score" in t else "liquidity filter and second observation"
        lines.append("- "+ctrl_utc(t["ts"])+" "+t["side"]+" "+t["token"]+
                     ": $%.2f; " % t["usd"]+reason+
                     ("; pre-upgrade" if t.get("controls_version") != ctrl_VERSION else ""))
    return "\n".join(lines)+"\n"


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
