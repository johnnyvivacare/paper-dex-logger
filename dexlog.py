#!/usr/bin/env python3
"""Paper-only DEX logger.  No wallet, no keys, no trades -- ever.

    python3 dexlog.py cycle    # pull fresh tokens, score, snapshot everything watched
    python3 dexlog.py report   # run the PRE-REGISTERED paper rules against the log
    python3 dexlog.py cycle  --jsonl data   # ephemeral runner: rebuild db from data/*.jsonl, run, append
    python3 dexlog.py report --jsonl data   # rebuild from jsonl, then report (set DEXLOG_DB for a clean file)
    python3 dexlog.py export --jsonl data   # one-time: dump the whole local db as jsonl (cloud seed)

PRE-REGISTERED RULES (written before any data was seen -- no hindsight tuning):
  budget $500, $50 per position, max 10 open, enter at first-seen price, FIFO.
  MOON      enter every new token.  exit +100% / -50% / 24h, whichever hits first.
  FILTERED  as MOON, but only tokens the scanner scored < 5 (not HIGH/EXTREME).
  HOLD      enter every new token, never sell, mark to latest price.
  -- registered 2026-10-06 05:14 UTC, AFTER seeing Fri->Mon data: evaluated ONLY on tokens first seen after it --
  QUICK     all tokens.  exit +50% / -30% / 6h.             ("get in, get out")
  PATIENT   all tokens.  exit +200% / -50% / 72h.           (let winners run)
  LIQUID    only first-seen liquidity >= $50k.  +100% / -50% / 24h.
  SOLANA    only chain == solana.  +100% / -50% / 24h.
  TRAILING  all tokens.  trailing stop -30% from peak, 48h max.
  costs     0.3% DEX fee each way; gas per chain; price impact size/(liq/2+size) each way.
  vanished from the API, or liquidity -> 0  ==  position worth $0 (could not exit).
  OPTIMISTIC: assumes every sell executes.  Honeypots make some real exits impossible.
"""
import json, os, re, sqlite3, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rugscan

DB = os.environ.get("DEXLOG_DB", os.path.join(HERE, "dex.db"))
UA = {"User-Agent": "paper-research/0.1"}
WATCH_HOURS, MAX_WATCH = 48, 1500
ADDR_OK = re.compile(r"^[A-Za-z0-9]{20,64}$")   # the promo feed can put prose in tokenAddress; it broke a URL


def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25))


def db():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS tokens (chain TEXT, addr TEXT, symbol TEXT, name TEXT,
      first_seen INTEGER, first_price REAL, first_liq REAL, first_fdv REAL,
      first_score INTEGER, first_reasons TEXT, pair_addr TEXT, pair_created INTEGER,
      PRIMARY KEY (chain, addr));
    CREATE TABLE IF NOT EXISTS snapshots (ts INTEGER, chain TEXT, addr TEXT, price REAL,
      liq REAL, fdv REAL, vol24 REAL, buys24 INTEGER, sells24 INTEGER, score INTEGER,
      present INTEGER, PRIMARY KEY (ts, chain, addr));
    CREATE TABLE IF NOT EXISTS runs (ts INTEGER PRIMARY KEY, new_tokens INTEGER,
      watched INTEGER, api_calls INTEGER, note TEXT);
    """)
    return c


def cycle():
    now, c, calls, new = int(time.time()), db(), 0, 0
    existing = {(r[0], r[1]) for r in c.execute("SELECT chain, addr FROM tokens")}
    known = {(r[0], r[1]) for r in c.execute(
        "SELECT chain, addr FROM tokens WHERE first_seen > ?", (now - WATCH_HOURS * 3600,))}

    found = set()
    for src in ("token-profiles/latest/v1", "token-boosts/latest/v1"):
        try:
            for t in get("https://api.dexscreener.com/" + src):
                if t.get("tokenAddress") and t.get("chainId") and ADDR_OK.match(t["tokenAddress"]):
                    found.add((t["chainId"], t["tokenAddress"]))
            calls += 1
        except Exception as e:
            print("  discovery %s failed: %s" % (src, e))
        time.sleep(0.3)

    todo = sorted(found | known)[:MAX_WATCH]
    bychain = {}
    for ch, ad in todo:
        bychain.setdefault(ch, []).append(ad)

    for ch, addrs in bychain.items():
        for i in range(0, len(addrs), 30):
            batch = addrs[i:i + 30]
            lc = {a.lower(): a for a in batch}
            try:
                pairs = get("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(batch)).get("pairs") or []
                calls += 1
            except Exception as e:
                print("  batch failed (%s): %s" % (ch, e)); pairs = []
            byaddr = {}
            for p in pairs:
                if p.get("chainId") != ch: continue
                a = lc.get(((p.get("baseToken") or {}).get("address") or "").lower())
                if a: byaddr.setdefault(a, []).append(p)
            for a in batch:
                ps = byaddr.get(a)
                if ps:
                    bp = max(ps, key=lambda p: ((p.get("liquidity") or {}).get("usd") or 0))
                    sc, why = rugscan.score(bp)
                    price = float(bp.get("priceUsd") or 0)
                    liq = (bp.get("liquidity") or {}).get("usd") or 0
                    fdv = bp.get("fdv") or 0
                    vol = (bp.get("volume") or {}).get("h24") or 0
                    tx = (bp.get("txns") or {}).get("h24") or {}
                    bt = bp.get("baseToken") or {}
                    if (ch, a) not in existing:
                        c.execute("INSERT OR IGNORE INTO tokens VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                  (ch, a, bt.get("symbol"), bt.get("name"), now, price, liq, fdv,
                                   sc, "; ".join(why), bp.get("pairAddress"), bp.get("pairCreatedAt")))
                        existing.add((ch, a)); new += 1
                    c.execute("INSERT OR REPLACE INTO snapshots VALUES (?,?,?,?,?,?,?,?,?,?,1)",
                              (now, ch, a, price, liq, fdv, vol, tx.get("buys", 0), tx.get("sells", 0), sc))
                elif (ch, a) in known:
                    c.execute("INSERT OR REPLACE INTO snapshots VALUES (?,?,?,?,?,?,?,?,?,?,0)",
                              (now, ch, a, None, 0, None, None, None, None, None))
            c.commit()
            time.sleep(0.25)

    c.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?)", (now, new, len(todo), calls, "ok"))
    c.commit()
    print("%s  new=%d  watched=%d  calls=%d" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(now)), new, len(todo), calls))
    return now


GAS = {"solana": 0.01, "ethereum": 3.0, "base": 0.05, "bsc": 0.05, "arbitrum": 0.10, "polygon": 0.02}
FEE, SIZE, BUDGET, SLOTS = 0.003, 50.0, 500.0, 10
REG2 = 1791263675   # 2026-10-06 05:14 UTC -- rules registered here count only tokens first seen after this


def impact(size, liq):
    return size / (liq / 2 + size) if liq > 0 else 1.0


def outcome(tok, snaps, tp, sl, maxh, hold, trail=None):
    """One token, one $50 position, independent of slot availability.
    Returns (exit_ts or None, value, label)."""
    ch, a, sym, t0, p0, liq0, sc = tok
    gas = GAS.get(ch, 0.5)
    units = (SIZE - SIZE * FEE - gas) * (1 - impact(SIZE, liq0)) / p0
    last, peak = None, p0
    for ts, price, liq, present in snaps:
        if ts <= t0: continue
        if not present or not liq or not price:
            return ts, 0.0, "rug"
        gross = units * price
        val = max(gross * (1 - impact(gross, liq)) * (1 - FEE) - gas, 0.0)
        last = (ts, val)
        ret = price / p0 - 1
        peak = max(peak, price)
        if not hold:
            if ret >= tp: return ts, val, "tp"
            if ret <= sl: return ts, val, "sl"
            if trail is not None and price / peak - 1 <= trail: return ts, val, "trail"
            if ts - t0 >= maxh * 3600: return ts, val, "timeout"
    return (None, last[1], "open") if last else (None, SIZE * (1 - FEE) - gas, "open")


def simulate(name, toks, snaps, filt, tp, sl, maxh, hold, trail=None):
    cash, open_, st = BUDGET, [], dict(entered=0, tp=0, sl=0, timeout=0, trail=0, rug=0, open=0, skipped=0)
    realized = 0.0
    for tok in toks:
        if not filt(tok): continue
        t0 = tok[3]
        still = []
        for ex_ts, val, lab in open_:
            if ex_ts is not None and ex_ts <= t0:
                cash += val; realized += val - SIZE; st[lab] += 1
            else:
                still.append((ex_ts, val, lab))
        open_ = still
        if len(open_) >= SLOTS or cash < SIZE:
            st["skipped"] += 1; continue
        cash -= SIZE; st["entered"] += 1
        open_.append(outcome(tok, snaps.get((tok[0], tok[1]), []), tp, sl, maxh, hold, trail))
    unreal = 0.0
    for ex_ts, val, lab in open_:
        if ex_ts is None: unreal += val; st["open"] += 1
        else: cash += val; realized += val - SIZE; st[lab] += 1
    equity = cash + unreal
    print("  %-9s  equity $%7.2f  (%+6.1f%%)   in %3d | tp %2d  sl %2d  trail %2d  time %2d  RUG %2d  open %2d | skip %d"
          % (name, equity, (equity / BUDGET - 1) * 100, st["entered"], st["tp"], st["sl"],
             st["trail"], st["timeout"], st["rug"], st["open"], st["skipped"]))


def benchmark(t_first, t_last):
    """$500 simply held in SOL over the log's window, after round-trip fees -- the yardstick."""
    try:
        res = get("https://api.kraken.com/0/public/OHLC?pair=SOLUSD&interval=60")["result"]
        rows = res[[k for k in res if k != "last"][0]]
        bars = [(int(r[0]), float(r[1]), float(r[4])) for r in rows]
        w = [b for b in bars if b[0] + 3600 > t_first and b[0] <= t_last + 3600]
        if not w: return None
        entry, last = w[0][1], w[-1][2]
        return entry, last, BUDGET * (1 - 0.004) * (last / entry) * (1 - 0.004)
    except Exception:
        return None


def report():
    c = db()
    runs = c.execute("SELECT COUNT(*), MIN(ts), MAX(ts) FROM runs").fetchone()
    ntok = c.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
    nsnap = c.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    gone = c.execute("SELECT COUNT(DISTINCT chain||addr) FROM snapshots WHERE present=0").fetchone()[0]
    f = lambda t: time.strftime("%a %m-%d %H:%M", time.gmtime(t)) if t else "-"
    print("log: %d cycles  %s -> %s UTC | %d tokens  %d snapshots | %d vanished from API\n"
          % (runs[0], f(runs[1]), f(runs[2]), ntok, nsnap, gone))
    bm = benchmark(runs[1], runs[2]) if runs[1] else None
    if bm:
        print("BENCHMARK  $500 simply held in SOL, same window:  $%.2f -> $%.2f   =  $%.2f  (%+.2f)\n"
              % (bm[0], bm[1], bm[2], bm[2] - BUDGET))
    toks = c.execute("SELECT chain, addr, symbol, first_seen, first_price, first_liq, first_score"
                     " FROM tokens WHERE first_price > 0 AND first_liq > 0 ORDER BY first_seen").fetchall()
    nomkt = ntok - len(toks)
    snaps = {}
    for ts, ch, a, price, liq, present in c.execute(
            "SELECT ts, chain, addr, price, liq, present FROM snapshots ORDER BY ts"):
        snaps.setdefault((ch, a), []).append((ts, price, liq, present))
    print("paper rules, $%.0f budget, $%.0f/position, %d slots  (%d tokens had no market at discovery)\n"
          % (BUDGET, SIZE, SLOTS, nomkt))
    ALL = lambda t: True
    print("  -- registered Fri 10-02 (all tokens) --")
    simulate("MOON",     toks, snaps, ALL,                        1.0, -0.5, 24, False)
    simulate("FILTERED", toks, snaps, lambda t: t[6] < 5,         1.0, -0.5, 24, False)
    simulate("HOLD",     toks, snaps, ALL,                        9e9, -9e9, 9e9, True)
    since = lambda t: t[3] >= REG2
    print("  -- registered %s (tokens first seen after that only) --" % time.strftime("%a %m-%d %H:%M", time.gmtime(REG2)))
    simulate("QUICK",    toks, snaps, since,                                     0.5, -0.3, 6, False)
    simulate("PATIENT",  toks, snaps, since,                                     2.0, -0.5, 72, False)
    simulate("LIQUID",   toks, snaps, lambda t: since(t) and t[5] >= 50_000,     1.0, -0.5, 24, False)
    simulate("SOLANA",   toks, snaps, lambda t: since(t) and t[0] == "solana",   1.0, -0.5, 24, False)
    simulate("TRAILING", toks, snaps, since,                                     9e9, -9e9, 48, False, trail=-0.3)
    print("\n  (optimistic: assumes every sell executes; honeypots are not modelled)")


TOKEN_COLS = ("chain", "addr", "symbol", "name", "first_seen", "first_price", "first_liq", "first_fdv",
              "first_score", "first_reasons", "pair_addr", "pair_created")
SNAP_COLS = ("ts", "chain", "addr", "price", "liq", "fdv", "vol24", "buys24", "sells24", "score", "present")
RUN_COLS = ("ts", "new_tokens", "watched", "api_calls", "note")
TABLES = (("tokens", TOKEN_COLS, "first_seen"), ("snapshots", SNAP_COLS, "ts"), ("runs", RUN_COLS, "ts"))


def load_jsonl(d):
    """Rebuild the db from append-only JSONL -- for runners with no persistent disk."""
    c = db()
    for name, cols, _ in TABLES:
        f = os.path.join(d, name + ".jsonl")
        if not os.path.exists(f): continue
        rows = []
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    o = json.loads(line); rows.append(tuple(o.get(k) for k in cols))
        c.executemany("INSERT OR IGNORE INTO %s VALUES (%s)" % (name, ",".join("?" * len(cols))), rows)
    c.commit()


def dump_jsonl(d, ts):
    """Append only THIS run's rows, so each commit is a few KB of text."""
    os.makedirs(d, exist_ok=True); c = db()
    for name, cols, tscol in TABLES:
        with open(os.path.join(d, name + ".jsonl"), "a") as fh:
            for row in c.execute("SELECT %s FROM %s WHERE %s=?" % (",".join(cols), name, tscol), (ts,)):
                fh.write(json.dumps(dict(zip(cols, row)), separators=(",", ":")) + "\n")


def export_jsonl(d):
    """One-time: write the ENTIRE local db as JSONL -- the seed for the cloud copy."""
    os.makedirs(d, exist_ok=True); c = db()
    for name, cols, tscol in TABLES:
        n = 0
        with open(os.path.join(d, name + ".jsonl"), "w") as fh:
            for row in c.execute("SELECT %s FROM %s ORDER BY %s" % (",".join(cols), name, tscol)):
                fh.write(json.dumps(dict(zip(cols, row)), separators=(",", ":")) + "\n"); n += 1
        print("  %-10s %6d rows -> %s" % (name, n, os.path.join(d, name + ".jsonl")))


if __name__ == "__main__":
    args, jsonl = sys.argv[1:], None
    if "--jsonl" in args:
        i = args.index("--jsonl"); jsonl = args[i + 1]; del args[i:i + 2]
    cmd = args[0] if args else "report"
    if cmd == "export":
        export_jsonl(jsonl or "data"); sys.exit()
    if jsonl:
        load_jsonl(jsonl)
    if cmd == "cycle":
        ts = cycle()
        if jsonl: dump_jsonl(jsonl, ts)
    else:
        report()
