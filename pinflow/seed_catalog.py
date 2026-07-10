"""
Seed the catalog with N draft products, no human approval, for reviewing the store.
Reuses orchestrator's research/listing/publish. Products land as DRAFT (safe, reviewable).
Deduped against existing store products, relevance-filtered to the seed niches.

Usage:  python seed_catalog.py [count]   (default 15)
"""
import sys, json
import orchestrator as o

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 15

def existing_titles_skus():
    titles, skus = set(), set()
    _, r = o._shopify("GET", "products.json?limit=250&fields=title,variants")
    for p in r.get("products", []):
        titles.add(p["title"].lower())
        for v in p.get("variants", []):
            if v.get("sku"):
                skus.add(v["sku"])
    return titles, skus

def build_pool(token, per_term=4):
    terms = list(o.SEED_NICHES)
    try:
        terms += list(json.loads(o.KEYWORDS_STORE.read_text()).keys())
    except Exception:
        pass
    pool = {}
    for k in terms:
        local = o.cj_search(k, token, limit=per_term, country=o.WAREHOUSE_COUNTRIES) \
                if o.PREFER_LOCAL_WAREHOUSE else []
        fill = o.cj_search(k, token, limit=per_term)
        for p in local + fill:
            pool.setdefault(p["title"].lower(), p)
    return list(pool.values())

def main():
    if not o._shopify_ready():
        sys.exit("Shopify not configured (env vars).")
    token = o._cj_token()
    titles, skus = existing_titles_skus()
    seed_words = {w for s in o.SEED_NICHES for w in s.split() if len(w) > 3}

    pool = build_pool(token)
    pool = [p for p in pool
            if 0 < p["cost"] < 8                                   # affordable, protects margin
            and p["title"].lower() not in titles                   # not already listed
            and p.get("pid") not in skus
            and any(w in p["title"].lower() for w in seed_words)]   # on-niche relevance guard
    pool.sort(key=lambda p: p.get("listed") or 0, reverse=True)    # proven sellers first
    print(f"pool: {len(pool)} eligible products, publishing up to {TARGET}")

    done = 0
    for p in pool:
        if done >= TARGET:
            break
        pick = {"id": str(done + 1), "angle": "practical everyday value for UK homes and gardens",
                "title": p["title"], "image": p.get("image", ""), "pid": p.get("pid", ""),
                "cost": p["cost"]}
        pick["images"] = o.cj_images(pick["pid"], token) or \
                         ([pick["image"]] if pick["image"] else [])
        try:
            listing = o.make_listing(pick)
            res = o.publish(listing, pick)
            if not res.get("shopify_product_id"):
                print(f"  skip (publish failed): {p['title'][:45]}"); continue
            done += 1
            print(f"[{done}/{TARGET}] £{o.retail_price(pick['cost']):.2f}  "
                  f"imgs {len(pick['images'])}  {listing['title'][:55]}")
        except o.AuthExpired:
            o.alert("PinFlow seed: Claude auth expired."); sys.exit("AUTH_EXPIRED")
        except Exception as e:
            print(f"  skip ({type(e).__name__}): {p['title'][:45]}")
    print(f"done: {done} draft products created")

if __name__ == "__main__":
    main()
