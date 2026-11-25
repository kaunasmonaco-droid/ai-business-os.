"""Local matching core. No scraping, messaging or payments."""
from datetime import date
from urllib.parse import urlparse

def match(request, offers, today=None):
    today = today or date.today()
    results = []
    seen = set()
    for offer in offers:
        url = offer.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or url in seen:
            continue
        if offer.get("category") != request.get("category"):
            continue
        if request.get("country") and offer.get("country") != request["country"]:
            continue
        try:
            if date.fromisoformat(offer["expires"]) < today:
                continue
        except (KeyError, ValueError, TypeError):
            continue
        budget = request.get("max_price")
        price = offer.get("price")
        if budget is not None and (not isinstance(price, (int, float)) or price < 0 or price > budget or offer.get("currency") != request.get("currency")):
            continue
        required = set(request.get("required", []))
        features = set(offer.get("features", []))
        if not required.issubset(features):
            continue
        seen.add(url)
        results.append({**offer, "status": "candidate_requires_source_verification", "score": len(set(request.get("preferred", [])) & features)})
    return sorted(results, key=lambda x: -x["score"])

def report(request, offers):
    return {"category": request.get("category"), "matches": match(request, offers), "notice": "Candidate matches only. Confirm availability, terms and source before delivery. No unsolicited messaging."}
