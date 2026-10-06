#!/usr/bin/env python3
"""DEX risk screener -- flags known rug/scam PATTERNS from DexScreener fields.

IMPORTANT LIMIT: this scores risk, it does not predict rugs, and its accuracy
cannot be measured.  Tokens that already died vanish from the API, so there is
no historical sample to validate against -- the survivorship problem is total.
Treat output as "avoid these", never as "the unflagged ones are safe".

The strongest rug signals are NOT in this data at all: mint authority, LP lock,
ownership renounce, honeypot sell-blocks and holder concentration all require
reading the contract on-chain.
"""
import json, re, time, urllib.request

UA = {"User-Agent": "research/0.1"}
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))

MAJORS = ("BITCOIN","ETHEREUM","TETHER","SOLANA","USDC","BNB","XRP","DOGE","CARDANO")


def score(p):
    """Return (risk_points, [reasons]).  Higher = more of the pattern."""
    r, why = 0, []
    liq = (p.get("liquidity") or {}).get("usd") or 0
    fdv = p.get("fdv") or 0
    vol = (p.get("volume") or {}).get("h24") or 0
    tx  = (p.get("txns") or {}).get("h24") or {}
    buys, sells = tx.get("buys", 0), tx.get("sells", 0)
    sym = ((p.get("baseToken") or {}).get("symbol") or "")
    nm  = ((p.get("baseToken") or {}).get("name") or "").upper()
    age = (time.time()*1000 - (p.get("pairCreatedAt") or 0)) / 86400000

    if liq < 10_000:              r += 3; why.append("liquidity <$10k")
    elif liq < 50_000:            r += 2; why.append("liquidity <$50k")
    # "Big valuation propped on a tiny pool" only means something when the
    # pool is actually tiny.  Every real major has FDV >> any single pool
    # (ETH: ~$320B vs a $110M pool), so gate on absolute pool size, not FDV --
    # a fake with a $500M "market cap" and a $20k pool must still trip this.
    if liq < 5_000_000:
        if liq and fdv/max(liq,1) > 50:  r += 3; why.append("FDV %.0fx liquidity" % (fdv/liq))
        elif liq and fdv/max(liq,1) > 10: r += 1; why.append("FDV %.0fx liquidity" % (fdv/liq))
    if liq and vol/max(liq,1) > 10:  r += 2; why.append("24h volume %.0fx liquidity (wash?)" % (vol/liq))
    # Spoofed-liquidity signature -- found live: a 'LINK' and a 'Ripple' on
    # Solana each showing $1.5B liquidity.  Nearly the whole supply sits in
    # the pool priced off a sliver of real quote, so liquidity ~= FDV and
    # turnover is near zero.  DexScreener reports reserves x price and shows
    # billions you could never sell into.  A LOW-liquidity check misses this.
    if fdv > 1_000_000:
        share = liq / fdv
        if share > 0.8:   r += 5; why.append("liquidity = %.0f%% of FDV (supply parked in pool)" % (100*share))
        elif share > 0.4: r += 3; why.append("liquidity = %.0f%% of FDV" % (100*share))
    if liq > 1_000_000 and vol / liq < 0.001:
        r += 3; why.append("claims $%s liquidity, %.4f%% daily turnover" % (format(round(liq), ","), 100*vol/liq))
    if age < 2:                   r += 2; why.append("pair <2 days old")
    elif age < 14:                r += 1; why.append("pair <14 days old")
    if sells and buys/max(sells,1) < 0.4: r += 1; why.append("sells %.1fx buys" % (sells/max(buys,1)))
    hits = sum(1 for m in MAJORS if m in nm)
    if hits >= 2:                 r += 3; why.append("name stuffed w/ %d major tickers" % hits)
    if len(sym) > 12 or re.search(r"(?i)(1000x|safe|moon|elon|pump|inu)", sym+nm):
        r += 1; why.append("hype naming")
    return r, why



def main():
    # Sample newly-surfaced tokens -- the population this is actually for
    addrs, chains = [], {}
    try:
        for t in get("https://api.dexscreener.com/token-profiles/latest/v1")[:40]:
            if t.get("tokenAddress"):
                addrs.append(t["tokenAddress"]); chains[t["tokenAddress"]] = t.get("chainId")
    except Exception as e:
        print("profiles endpoint failed:", e)

    pairs, seen = [], set()
    for a in addrs[:30]:
        try:
            for p in (get("https://api.dexscreener.com/latest/dex/tokens/%s" % a).get("pairs") or [])[:1]:
                if p.get("pairAddress") not in seen:
                    seen.add(p.get("pairAddress")); pairs.append(p)
        except Exception:
            pass
        time.sleep(0.25)

    print("scored %d freshly-listed tokens\n" % len(pairs))
    rows = sorted(((score(p)[0], score(p)[1], p) for p in pairs), reverse=True, key=lambda x: x[0])
    band = lambda r: "EXTREME" if r >= 8 else "HIGH" if r >= 5 else "MEDIUM" if r >= 3 else "lower"
    for r, why, p in rows[:14]:
        sym = ((p.get("baseToken") or {}).get("symbol") or "?")[:14]
        liq = (p.get("liquidity") or {}).get("usd") or 0
        print("  %-8s %2d  %-14s liq $%-11s %s"
              % (band(r), r, sym, format(round(liq), ","), "; ".join(why[:3])))

    n = len(rows) or 1
    print("\n  %.0f%% scored HIGH or EXTREME risk." % (100*sum(1 for r,_,_ in rows if r>=5)/n))
    print("  %.0f%% had under $50k liquidity." % (100*sum(1 for _,_,p in rows
          if ((p.get('liquidity') or {}).get('usd') or 0) < 50_000)/n))


if __name__ == "__main__":
    main()
