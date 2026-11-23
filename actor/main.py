"""AI BUSINESS OS – Source-verified company website profiler. No paid APIs."""
import argparse
import csv
import io
import ipaddress
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

MAX_SITES = 10
MAX_BYTES = 400_000
USER_AGENT = "AIBusinessOS-CompanyResearch/0.1 (+public-source-verification)"
GENERIC_PREFIXES = ("info", "hello", "contact", "sales", "export", "office", "enquiries", "inquiries", "support")

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self._in_title = False
        self._ignored = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            self._ignored += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key in ("description", "og:description") and not self.description:
                self.description = attrs.get("content", "")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self._ignored = max(0, self._ignored - 1)
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._ignored:
            return
        s = re.sub(r"\s+", " ", data).strip()
        if s:
            if self._in_title:
                self.title += (" " if self.title else "") + s
            else:
                self.parts.append(s)

def validate_public_url(value):
    """Limit to HTTPS public hostnames; reject direct IP and local/reserved DNS."""
    if not isinstance(value, str):
        raise ValueError("URL must be a string")
    p = urllib.parse.urlsplit(value.strip())
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise ValueError("Only HTTPS public hostname URLs are allowed")
    host = p.hostname.lower().rstrip(".")
    if (host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".test"))
            or "." not in host):
        raise ValueError("Local hostname rejected")
    try:
        ipaddress.ip_address(host)
        raise ValueError("Direct IP URLs are not supported")
    except ValueError as exc:
        if str(exc) == "Direct IP URLs are not supported":
            raise
    return p.geturl()

def public_dns(host):
    """Reject private, reserved or local destinations after DNS resolution."""
    records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    ips = {record[4][0] for record in records}
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Target resolved to a non-public address")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def download_page(url):
    opener = urllib.request.build_opener(NoRedirect)
    for _ in range(3):
        url = validate_public_url(url)
        public_dns(urllib.parse.urlsplit(url).hostname)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            with opener.open(req, timeout=9) as res:
                content_type = (res.headers.get("Content-Type") or "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    raise ValueError("Not an HTML page")
                data = res.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError("Page too large")
                return url, data.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                url = urllib.parse.urljoin(url, e.headers["Location"])
                continue
            raise
    raise ValueError("Too many redirects")

def profile_one(url, keywords=None, fetcher=download_page):
    validated_url = validate_public_url(url)
    final_url, html = fetcher(validated_url)
    parser = TextParser()
    parser.feed(html)
    body = re.sub(r"\s+", " ", " ".join(parser.parts))[:7000]
    words = [str(x).strip().lower() for x in (keywords or []) if str(x).strip()][:10]
    matches = [word for word in words if word in body.lower()]
    emails = re.findall(r"(?i)(?<![\w.+-])([\w.+-]+@[\w.-]+\.[a-z]{2,})(?![\w.-])", html)
    generic = sorted({e.lower() for e in emails if e.split("@")[0].lower() in GENERIC_PREFIXES})[:5]
    return {
        "source_url": final_url,
        "title": parser.title[:180] or None,
        "description": parser.description[:500] or None,
        "public_evidence_excerpt": body[:550] or None,
        "keyword_matches": matches,
        "keyword_match_count": len(matches),
        "generic_contact_emails": generic,
        "verified_buyer_interest": False,
        "verification_note": "Public website data only. No verification of purchasing intent or order availability.",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }

def run(payload, fetcher=download_page):
    urls = payload.get("urls", []) if isinstance(payload, dict) else []
    if not isinstance(urls, list) or not (1 <= len(urls) <= MAX_SITES):
        raise ValueError("Provide 1–10 source website URLs")
    keywords = payload.get("keywords", [])
    if not isinstance(keywords, list):
        raise ValueError("keywords must be an array")
    output = []
    seen = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        try:
            output.append(profile_one(url, keywords, fetcher=fetcher))
        except Exception as e:
            output.append({"source_url": str(url), "status": "error",
                           "error": str(e)[:220], "verified_buyer_interest": False})
    return output

def apify_get_input():
    store = os.getenv("APIFY_DEFAULT_KEY_VALUE_STORE_ID")
    token = os.getenv("APIFY_TOKEN")
    if not store or not token:
        return None
    key = os.getenv("ACTOR_INPUT_KEY", "INPUT")
    base = os.getenv("APIFY_API_BASE_URL", "https://api.apify.com").rstrip("/")
    url = f"{base}/v2/key-value-stores/{urllib.parse.quote(store)}/records/{urllib.parse.quote(key)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read(1_000_000).decode())

def apify_push(records):
    dataset = os.getenv("APIFY_DEFAULT_DATASET_ID")
    token = os.getenv("APIFY_TOKEN")
    if not dataset or not token:
        return False
    base = os.getenv("APIFY_API_BASE_URL", "https://api.apify.com").rstrip("/")
    endpoint = f"{base}/v2/datasets/{urllib.parse.quote(dataset)}/items"
    data = json.dumps(records, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status not in (200, 201, 204):
            raise ValueError(f"Apify dataset write failed: {res.status}")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Local JSON input path, no API token required")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as stream:
            payload = json.load(stream)
    else:
        payload = apify_get_input()
        if payload is None:
            raise SystemExit("Missing input: use --input example_input.json, or Apify runtime")
    result = run(payload)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    print(output)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(output + "\n")
    if not args.input:
        apify_push(result)

if __name__ == "__main__":
    main()
