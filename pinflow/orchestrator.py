"""
PinFlow orchestrator — the bot's spine.

Control flow lives here (deterministic, debuggable). Claude is called only to
*think* at 3 points: score candidates, write listing copy, write the SEO blog.
Auth = your Claude Max subscription via headless `claude -p` (NO api key).

Runs today as a DRY LOOP: research/publish are stubs, state is a local JSON
file. Swap the TODO sections for Supabase + Shopify + a real research source
when the spine feels solid.
"""

import json, subprocess, shutil, time, os, sys, pathlib, math
import urllib.request, urllib.parse, urllib.error

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console: allow emoji

# ---------------------------------------------------------------- CONFIG
CLAUDE_BIN   = shutil.which("claude") or "claude"        # resolves claude.cmd on Windows
WORKDIR      = pathlib.Path(__file__).with_name("bot_workdir")  # clean dir => less overhead
STATE_FILE   = pathlib.Path(__file__).with_name("state.json")
SCORING_MODEL = "opus"      # few, high-value calls
COPY_MODEL    = "sonnet"    # bulk copy/blog => cheaper, spares rate-limit budget
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT", "")
WORKDIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------- CLAUDE
class AuthExpired(Exception): ...

def _call_claude(prompt, model, system, max_turns=1):
    """One headless invocation. Returns the model's text (envelope .result).

    Prompt goes via STDIN (any length / newlines safe). The system prompt must
    stay single-line: newlines in argv get mangled by the Windows claude.CMD shim.
    """
    proc = subprocess.run(
        [CLAUDE_BIN, "-p",
         "--output-format", "json",
         "--model", model,
         "--max-turns", str(max_turns),      # answer, don't loop into tools
         "--append-system-prompt", " ".join(system.split())],  # flatten to one line
        input=prompt,                                  # prompt via stdin, not argv
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=240, cwd=WORKDIR,                      # decode UTF-8, not cp1252
        env={**os.environ, "ANTHROPIC_API_KEY": ""},  # force subscription auth
    )
    out = proc.stdout.lstrip("﻿").strip()         # tolerate BOM
    if not out:
        raise RuntimeError(f"claude produced no output. stderr:\n{proc.stderr[:500]}")
    env = json.loads(out)
    if env.get("api_error_status") == 401 or (
        env.get("is_error") and "authenticat" in (env.get("result") or "").lower()):
        raise AuthExpired(env.get("result"))
    if env.get("is_error"):
        raise RuntimeError(f"claude error: {env.get('result')}")
    return env["result"]

def claude_json(prompt, schema_hint, model=SCORING_MODEL, retries=2):
    """Reasoning call that must return JSON. Repairs invalid output up to `retries`."""
    system = ("You are a precise data function. Output ONLY valid JSON matching "
              f"this schema, no markdown fences, no prose:\n{schema_hint}")
    last = ""
    for _ in range(retries + 1):
        p = prompt if not last else (
            f"{prompt}\n\nYour previous output was invalid JSON:\n{last}\n"
            "Return corrected JSON only.")
        raw = _call_claude(p, model, system)
        s = raw.strip().strip("`")
        if "{" in s and "}" in s:
            s = s[s.find("{"): s.rfind("}") + 1]
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            last = raw
    raise ValueError("Claude did not return valid JSON after retries")

NO_DASH_RULE = "Never use em dashes or en dashes anywhere; use commas or periods instead."

def _no_dashes(s):
    """Strip em/en dashes from generated text (keeps normal hyphens in compounds)."""
    if not isinstance(s, str):
        return s
    for d in ("—", "–"):             # em dash, en dash
        s = s.replace(f" {d} ", ", ").replace(d, ", ")
    return s.replace(" ,", ",").replace(",,", ",")

def claude_text(prompt, model=COPY_MODEL):
    system = "You are a brand copywriter. Return only the requested content, no preamble. " + NO_DASH_RULE
    return _no_dashes(_call_claude(prompt, model, system))

# ---------------------------------------------------------------- STATE (swap for Supabase)
def load_state():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"candidates": []}
def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2))

# ---------------------------------------------------------------- HUMAN CHANNEL (Telegram)
def _tg(method, **params):
    """Call a Telegram Bot API method. Prints instead when no token is set."""
    if not TELEGRAM_TOKEN:
        if method == "sendMessage":
            print("[telegram]\n" + params.get("text", ""))
        return {"ok": True, "result": []}
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode()
    try:
        resp = json.loads(urllib.request.urlopen(url, data=data, timeout=45).read())
    except Exception as e:
        print(f"[telegram:{method}] request failed: {e}"); return {"ok": False, "result": []}
    if not resp.get("ok"):
        print(f"[telegram:{method}] API error: {resp.get('description')}")
    return resp

def alert(text):
    _tg("sendMessage", chat_id=TELEGRAM_CHAT, text=text)

def ask_and_wait(digest, valid_ids, poll_s=25, timeout_min=1440):
    """Send the digest with Approve/Reject buttons; block until you tap one."""
    if not TELEGRAM_TOKEN:                         # dry-run: auto-approve top pick
        print("[telegram]\n" + digest)
        return {"decision": "approve", "id": valid_ids[0]}
    keyboard = {"inline_keyboard":
        [[{"text": f"✅ Approve #{i}", "callback_data": f"approve:{i}"}] for i in valid_ids]
        + [[{"text": "❌ Reject all", "callback_data": "reject:-"}]]}
    prev = _tg("getUpdates", timeout=0).get("result", [])   # skip stale taps
    offset = prev[-1]["update_id"] + 1 if prev else None
    _tg("sendMessage", chat_id=TELEGRAM_CHAT, text=digest,
        reply_markup=json.dumps(keyboard))
    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:                  # long-poll: blocks up to poll_s server-side
        upd = _tg("getUpdates", offset=offset if offset is not None else "",
                  timeout=poll_s, allowed_updates=json.dumps(["callback_query"]))
        for u in upd.get("result", []):
            offset = u["update_id"] + 1
            cq = u.get("callback_query")
            if not cq:
                continue
            action, _, pid = cq.get("data", "").partition(":")
            _tg("answerCallbackQuery", callback_query_id=cq["id"],
                text="Rejected." if action == "reject" else f"Approved #{pid} ✔")
            if action == "reject":
                return {"decision": "reject"}
            if action == "approve" and pid in valid_ids:
                return {"decision": "approve", "id": pid}
    return {"decision": "timeout"}

# ---------------------------------------------------------------- PIPELINE STAGES
# Target: UK, 55+ affluent. Product-shaped, non-medical seeds (no health claims).
SEED_NICHES = ["garden kneeler seat", "easy grip kitchen gadget", "bird feeding station",
               "reading magnifier light", "support seat cushion", "cordless garden tool"]
TARGET_COUNTRY = "gb"   # google geo/region for demand signal
WAREHOUSE_COUNTRIES = "GB,DE,FR,ES,IT,NL,PL,CZ"  # UK + EU stock = fast UK delivery
PREFER_LOCAL_WAREHOUSE = True                    # try local stock first, fall back to global
USD_TO_GBP = 0.79     # CJ costs are USD, store is GBP. Update if FX moves materially.
MARKUP     = 3.2      # retail = cost * markup (covers ads, fees, returns, profit)
MIN_PRICE  = 6.99     # floor so cheap items still clear fixed costs
MODIFIERS = ["", "best", "reusable", "set", "for kitchen"]   # expand Suggest yield per seed
KEYWORDS_STORE = pathlib.Path(__file__).with_name("keywords.json")
CJ_EMAIL   = os.environ.get("CJ_EMAIL", "")
CJ_API_KEY = os.environ.get("CJ_API_KEY", "")
CJ_BASE    = "https://developers.cjdropshipping.com/api2.0/v1"
CJ_TOKEN_CACHE = pathlib.Path(__file__).with_name("cj_token.json")
SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "")            # e.g. yourstore.myshopify.com
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "")   # Dev Dashboard app Client ID
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")  # Client Secret (shpss_...)
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_TOKEN", "")           # optional static shpat_ (legacy)
SHOPIFY_API   = "2025-01"
SHOPIFY_TOKEN_CACHE = pathlib.Path(__file__).with_name("shopify_token.json")

def _http_json(method, url, body=None, headers=None):
    hdr = {"Content-Type": "application/json", **(headers or {})}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=hdr, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def trending_keywords(seeds=SEED_NICHES, geo="GB"):
    """Rising Google Trends queries -> {keyword: momentum 0.5-1.0}. Empty on failure."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("[trends] pytrends not installed; skipping trend signal"); return {}
    out = {}
    try:
        py = TrendReq(hl="en-US", tz=0)
        for seed in seeds:
            py.build_payload([seed], timeframe="now 7-d", geo=geo)
            rising = (py.related_queries().get(seed) or {}).get("rising")
            if rising is None:
                continue
            for _, row in rising.iterrows():
                v = row["value"]
                score = 1.0 if (isinstance(v, str) and "break" in v.lower()) \
                        else min(float(v) / 200.0, 1.0)
                out[str(row["query"]).lower()] = round(max(score, 0.5), 2)
            time.sleep(1)                      # be gentle: Google rate-limits hard
    except Exception as e:
        print(f"[trends] pytrends failed ({type(e).__name__}); using Google Suggest fallback")
    if not out:                                # reliable free fallback: autocomplete popularity
        for seed in seeds:
            for mod in MODIFIERS:              # expand each seed to multiply yield
                q = f"{seed} {mod}".strip()
                for rank, sugg in enumerate(google_suggest(q)[:8]):
                    score = round(max(1.0 - rank * 0.05, 0.6), 2)
                    key = sugg.lower()
                    out[key] = max(out.get(key, 0), score)
                time.sleep(0.2)
    return out

def google_suggest(seed, gl=TARGET_COUNTRY, hl="en-GB"):
    """Free, reliable demand proxy: Google autocomplete completions, popularity-ranked."""
    url = ("https://suggestqueries.google.com/complete/search"
           f"?client=firefox&gl={gl}&hl={hl}&q={urllib.parse.quote(seed)}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        arr = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace"))
        return arr[1] if len(arr) > 1 else []
    except Exception as e:
        print(f"[suggest] '{seed}' failed: {e}"); return []

def clean_keywords(raw, model="haiku"):
    """Cheap Claude pass: drop non-product noise, normalize to product search terms."""
    if not raw:
        return {}
    schema = '{"terms":[{"term":"str","score":0.0}]}'
    prompt = ("From these raw Google queries, keep ONLY ones that map to a physical product "
              "someone could dropship. Drop people, charities, campaigns, brand/store names, "
              "locations, and 'near me' queries. Rewrite each kept query as a short commercial "
              "product search term (2-4 words). Preserve each query's given score.\n"
              "Queries (query: score):\n"
              + "\n".join(f"- {k}: {v}" for k, v in raw.items()))
    try:
        out = claude_json(prompt, schema, model=model)
        cleaned = {t["term"].lower(): float(t.get("score", 0.6))
                   for t in out.get("terms", []) if t.get("term")}
        print(f"[clean] {len(raw)} raw -> {len(cleaned)} product terms")
        return cleaned or raw
    except Exception as e:
        print(f"[clean] cleanup failed ({e}); using raw keywords"); return raw

def _cj_token():
    """Cached CJ access token. CJ limits getAccessToken to ~1/5min, so reuse from disk."""
    if CJ_TOKEN_CACHE.exists():
        try:
            c = json.loads(CJ_TOKEN_CACHE.read_text())
            if c.get("expires", 0) > time.time() + 3600:   # still valid (1h safety margin)
                return c["accessToken"]
        except Exception:
            pass
    try:
        r = _http_json("POST", f"{CJ_BASE}/authentication/getAccessToken",
                       {"email": CJ_EMAIL, "password": CJ_API_KEY})
    except Exception as e:
        print(f"[cj] token fetch failed: {e}"); return None
    tok = (r.get("data") or {}).get("accessToken")
    if tok:                                                  # CJ tokens last ~15d; cache 13
        CJ_TOKEN_CACHE.write_text(json.dumps(
            {"accessToken": tok, "expires": time.time() + 13 * 86400}))
    else:
        print(f"[cj] no token in response: {r.get('message')}")
    return tok

def _cj_price(it):
    raw = str(it.get("sellPrice", "0")).split("-")[0].strip()   # ranges like "2.5--5.0"
    try: return float(raw)
    except ValueError: return 0.0

def cj_search(keyword, token, limit=3, country=""):
    # listV2 = Elasticsearch keyword search (relevant), unlike v1's loose fuzzy match.
    url = (f"{CJ_BASE}/product/listV2?pageNum=1&pageSize=20"
           f"&keyWord={urllib.parse.quote(keyword)}")
    if country:                                   # only products stocked in these warehouses
        url += f"&countryCode={country}"
    try:
        r = _http_json("GET", url, headers={"CJ-Access-Token": token})
    except Exception as e:
        print(f"[cj] search '{keyword}' failed: {e}"); return []
    items = []
    for group in ((r.get("data") or {}).get("content") or []):
        items += group.get("productList") or []
    ships = "local" if country else "global"      # local = fast UK/EU, global = China/slow
    out = [{"title": (it.get("nameEn") or "").strip(), "cost": _cj_price(it), "url": "",
            "image": it.get("bigImage", ""), "pid": it.get("id", ""),
            "listed": it.get("listedNum", 0), "ships": ships}
           for it in items if it.get("nameEn")]
    out.sort(key=lambda x: x["listed"] or 0, reverse=True)   # proven sellers first (null-safe)
    return out[:limit]

def cj_images(pid, token, limit=6):
    """Full image set for a product (listV2 only returns one). Returns a list of URLs."""
    try:
        r = _http_json("GET", f"{CJ_BASE}/product/query?pid={pid}",
                       headers={"CJ-Access-Token": token})
    except Exception as e:
        print(f"[cj] image fetch failed: {e}"); return []
    d = r.get("data") or {}
    imgs = d.get("productImageSet") or []
    if not imgs and d.get("productImage"):
        try: imgs = json.loads(d["productImage"])
        except Exception: imgs = []
    return [u for u in imgs if u][:limit]

def retail_price(usd_cost):
    """Deterministic GBP retail: convert cost, apply markup, charm-round, enforce floor."""
    gbp = (usd_cost or 0) * USD_TO_GBP
    price = math.ceil(gbp * MARKUP) - 0.01          # e.g. 5.40 -> 6.99-style charm price
    return max(price, MIN_PRICE)

def _mock_supplier():
    return [
        {"title": "Reusable Beeswax Food Wraps (3-Pack)",  "cost": 3.1, "url": ""},
        {"title": "Collapsible Silicone Coffee Dripper",   "cost": 2.4, "url": ""},
        {"title": "Magnetic Fridge Meal-Prep Planner",     "cost": 1.9, "url": ""},
        {"title": "Stainless Steel Reusable Straw Set",    "cost": 1.2, "url": ""},
        {"title": "Bamboo Dish Brush w/ Replaceable Head", "cost": 1.6, "url": ""},
        {"title": "Silicone Stretch Lids (6-Pack)",        "cost": 2.0, "url": ""},
    ]

def persist_keywords(fresh, cap=200):
    """Union today's keywords into keywords.json so a thin run is backfilled by history."""
    try:
        hist = json.loads(KEYWORDS_STORE.read_text())
    except Exception:
        hist = {}
    for k, v in fresh.items():
        hist[k] = max(v, hist.get(k, 0))       # keep best score ever seen
    if len(hist) > cap:                         # keep the strongest, bound the file
        hist = dict(sorted(hist.items(), key=lambda x: x[1], reverse=True)[:cap])
    KEYWORDS_STORE.write_text(json.dumps(hist, indent=2, ensure_ascii=False))
    return hist

def _kw_overlap(keyword, title_lower):
    return any(w in title_lower for w in keyword.split() if len(w) > 3)

def research(max_candidates=8):
    """Google Trends demand x supplier supply -> scored candidates."""
    fresh = clean_keywords(trending_keywords())    # raw demand -> clean product terms
    kw = persist_keywords(fresh)                    # union with history; never starves
    print(f"[research] {len(fresh)} fresh + history -> {len(kw)} total keywords")
    top_kw = sorted(kw, key=kw.get, reverse=True)[:6] or SEED_NICHES
    print(f"[research] {len(kw)} rising terms; probing supplier for: {top_kw[:4]}")

    products = []
    if CJ_EMAIL and CJ_API_KEY:
        token = _cj_token()
        if token:
            for k in top_kw:
                local = cj_search(k, token, limit=3, country=WAREHOUSE_COUNTRIES) \
                        if PREFER_LOCAL_WAREHOUSE else []
                fill = cj_search(k, token, limit=3 - len(local)) if len(local) < 3 else []
                products += local + fill       # local (fast) first, global fills the rest
                time.sleep(1)                  # CJ rate limit ~1 req/s
    if not products:                           # no CJ creds, or CJ returned nothing
        print("[research] mock supplier catalog (set CJ_EMAIL/CJ_API_KEY for live sourcing)")
        products = _mock_supplier()

    merged = {}
    for p in products:
        t = p["title"].lower()
        trend = max([m for w, m in kw.items() if _kw_overlap(w, t)] or [0.5])
        if t not in merged or trend > merged[t]["trend"]:
            merged[t] = {"title": p["title"], "cost": p["cost"], "trend": round(trend, 2),
                         "url": p.get("url", ""), "image": p.get("image", ""),
                         "pid": p.get("pid", ""), "ships": p.get("ships", "global")}
    cands = list(merged.values())[:max_candidates]
    for i, c in enumerate(cands, 1):
        c["id"] = str(i)
    return cands

def screen(cands, cost_ceiling=8.0):
    affordable = [c for c in cands if 0 < c["cost"] < cost_ceiling]  # hard margin gate
    good = [c for c in affordable if c["trend"] > 0.6]
    if len(good) < 3:                          # don't starve, but stay within budget
        good = sorted(affordable, key=lambda c: c["trend"], reverse=True)[:5]
    return good[:15]

def score(cands):
    schema = ('{"top_3":[{"id":"str","score":0-100,"pros":["str"],"cons":["str"],'
              '"suggested_price":0.0,"angle":"str","risk_flags":["str"]}]}')
    return claude_json(
        f"Score these dropshipping candidates for a UK store targeting affluent buyers aged 55+, "
        f"on demand durability, competition, margin, and fit for that audience. Products with "
        f"ships='local' (UK/EU warehouse, fast delivery) are strongly preferred over ships='global' "
        f"(China, ~2 week shipping) for this trust-sensitive group. "
        f"Candidates:\n{json.dumps(cands)}",
        schema)["top_3"]

def make_listing(pick):
    schema = ('{"title":"str","description_html":"str","meta_title":"str",'
              '"meta_description":"str","alt_text":"str","keywords":["str"]}')
    price = retail_price(pick.get("cost", 0))
    listing = claude_json(
        f"Write a Shopify product listing for '{pick['title']}', selling at GBP {price:.2f}. "
        f"Angle: {pick['angle']}. Warm, trustworthy, benefit-led voice for UK buyers aged 55+. "
        f"description_html must be semantic HTML: a short intro <p>, then a <ul> of 4 to 6 "
        f"benefit <li> bullets, then a closing reassurance <p>. "
        f"Write all copy in English regardless of the source product name. " + NO_DASH_RULE,
        schema, model=COPY_MODEL)
    return {k: _no_dashes(v) for k, v in listing.items()}   # backstop sanitizer

def _shopify_ready():
    return bool(SHOPIFY_STORE and (SHOPIFY_TOKEN or
                (SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET)))

def _shopify_token():
    """Admin API token via client-credentials grant (24h), cached to disk. Static token wins."""
    if SHOPIFY_TOKEN:
        return SHOPIFY_TOKEN
    if SHOPIFY_TOKEN_CACHE.exists():
        try:
            c = json.loads(SHOPIFY_TOKEN_CACHE.read_text())
            if c.get("expires", 0) > time.time() + 300:      # 5-min safety margin
                return c["accessToken"]
        except Exception:
            pass
    body = urllib.parse.urlencode({"grant_type": "client_credentials",
        "client_id": SHOPIFY_CLIENT_ID, "client_secret": SHOPIFY_CLIENT_SECRET}).encode()
    req = urllib.request.Request(f"https://{SHOPIFY_STORE}/admin/oauth/access_token",
        data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[shopify] token grant failed {e.code}: {e.read().decode('utf-8','replace')[:300]}")
        return None
    tok = d.get("access_token")
    if tok:
        SHOPIFY_TOKEN_CACHE.write_text(json.dumps(
            {"accessToken": tok, "expires": time.time() + d.get("expires_in", 86399)}))
    return tok

def _shopify(method, path, body=None):
    """Shopify Admin REST call. Returns (status_code, json). Reads error bodies too."""
    tok = _shopify_token()
    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "X-Shopify-Access-Token": tok or "", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", "replace") or "{}")

def publish(listing, pick):
    """Create the product as a Shopify draft with image, price, tags, SEO meta."""
    if not _shopify_ready():
        print(f"[shopify] would publish: {listing['title']}")        # dry-run
        return {"shopify_product_id": "draft-" + pick["id"], "handle": None}
    product = {"product": {
        "title": listing["title"],
        "body_html": listing["description_html"],
        "vendor": "PinFlow",
        "tags": ", ".join(listing.get("keywords", [])),
        "status": "draft",                                            # review before going live
        "variants": [{"price": f"{retail_price(pick.get('cost', 0)):.2f}",
                      "sku": pick.get("pid", "")}],
        "metafields_global_title_tag": listing.get("meta_title", ""),
        "metafields_global_description_tag": listing.get("meta_description", ""),
    }}
    imgs = pick.get("images") or ([pick["image"]] if pick.get("image") else [])
    if imgs:
        product["product"]["images"] = [{"src": u, "alt": listing.get("alt_text", "")}
                                        for u in imgs]
    status, resp = _shopify("POST", "products.json", product)
    if status not in (200, 201):
        print(f"[shopify] product create failed {status}: {resp}")
        return {"shopify_product_id": None, "handle": None, "error": resp}
    p = resp["product"]
    print(f"[shopify] created draft product {p['id']}")
    return {"shopify_product_id": p["id"], "handle": p.get("handle")}

def publish_blog(listing, blog_html):
    """Publish the SEO post to the store's first blog (creates one if none exists)."""
    if not _shopify_ready():
        print(f"[shopify] would publish blog ({len(blog_html.split())} words)")
        return None
    _, blogs = _shopify("GET", "blogs.json")
    blist = blogs.get("blogs") or []
    blog_id = blist[0]["id"] if blist else \
        (_shopify("POST", "blogs.json", {"blog": {"title": "Guides"}})[1]
         .get("blog", {}).get("id"))
    if not blog_id:
        print("[shopify] no blog available"); return None
    article = {"article": {"title": _no_dashes(f"Buyer's Guide: {listing['title']}"),
               "body_html": blog_html, "tags": ", ".join(listing.get("keywords", [])),
               "published": True}}
    status, resp = _shopify("POST", f"blogs/{blog_id}/articles.json", article)
    if status not in (200, 201):
        print(f"[shopify] blog publish failed {status}: {resp}"); return None
    aid = resp["article"]["id"]
    print(f"[shopify] published blog article {aid}")
    return aid

def write_blog(listing):
    return claude_text(
        f"Write a 900-word buyer's guide blog post in English about '{listing['title']}', "
        f"targeting the keyword '{listing['keywords'][0]}'. "
        f"Return clean semantic HTML only: <h2>/<h3> subheadings, <p> paragraphs, "
        f"<ul><li> bullets, <strong> emphasis. No markdown, no ``` fences.")

# ---------------------------------------------------------------- MAIN
def main():
    try:
        cands = screen(research())
        picks = score(cands)
        def _ship(cid):
            s = next((c.get("ships") for c in cands if c["id"] == cid), "global")
            return "🇬🇧 UK/EU stock, fast" if s == "local" else "🌏 China stock, ~2 wk"
        digest = "\n\n".join(
            f"[{p['id']}] {next(c['title'] for c in cands if c['id']==p['id'])} "
            f"score {p['score']}, ${p['suggested_price']}  [{_ship(p['id'])}]\n"
            f"  + {', '.join(p['pros'][:2])}\n  - {', '.join(p['cons'][:2])}"
            + (f"\n  ⚠ {', '.join(p['risk_flags'])}" if p.get('risk_flags') else "")
            for p in picks)
        decision = ask_and_wait(_no_dashes("🛒 PinFlow picks:\n\n" + digest),
                                [p["id"] for p in picks])

        if decision["decision"] != "approve":
            alert(f"Run ended: {decision['decision']}"); return
        pick = next(p for p in picks if p["id"] == decision["id"])
        src = next(c for c in cands if c["id"] == pick["id"])          # carry supplier fields
        pick.update({"title": src["title"], "image": src.get("image", ""),
                     "pid": src.get("pid", ""), "cost": src.get("cost", 0)})
        pick["images"] = cj_images(pick["pid"], _cj_token()) if pick.get("pid") else []
        if not pick["images"] and pick.get("image"):
            pick["images"] = [pick["image"]]
        listing = make_listing(pick)
        result = publish(listing, pick)
        blog = write_blog(listing).strip()
        if blog.startswith("```"):                          # strip stray code fences
            blog = blog.strip("`")
            blog = blog[4:] if blog[:4].lower() == "html" else blog
        blog_html = blog
        if result.get("handle") and SHOPIFY_STORE:          # internal link for SEO
            blog_html += (f'<p>Shop it here: <a href="https://{SHOPIFY_STORE}'
                          f'/products/{result["handle"]}">{listing["title"]}</a></p>')
        blog_id = publish_blog(listing, blog_html)
        alert(_no_dashes(f"✅ Published '{listing['title']}' "
              f"(product {result.get('shopify_product_id')}, blog {blog_id}, "
              f"{len(blog.split())} words)"))
    except AuthExpired:
        alert("⚠️ PinFlow: Claude auth expired. Run claude setup-token on the host.")
        sys.exit("AUTH_EXPIRED")

if __name__ == "__main__":
    main()
