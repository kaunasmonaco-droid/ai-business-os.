# AI BUSINESS OS – Company Website Research Agent (v0.1)

**A working, deterministic research agent; not an LLM and not a marketplace product yet.**

## Mission
Given **1–10 company website URLs**, fetch only public HTTPS homepages and produce JSON records with title, description, short evidence excerpt, explicitly matched keywords and generic business email addresses (e.g. info@, sales@, export@). Every result includes its source URL and timestamps. Buyer intent, demand and order availability are **not** inferred or guaranteed.

## 0 € local test
Requires only Python 3.10+. No API keys, pip dependencies or subscription needed.

```bash
cd actor
python main.py --input example_input.json --output results.json
python -m unittest discover -s tests -v
```

## Free Apify trial
1. Create a **Free** Apify account; do not add a credit card or subscribe to a paid plan.
2. Apify Console → Actors → Create Actor → Git repository source.
3. Repository URL: `https://github.com/kaunasmonaco-droid/ai-business-os.`
4. Branch + directory: `#main:actor` (the repository name ends with a dot).
5. Build, then run with the example input. Keep usage within the free credits. Inspect charges before executing; **never enable automatic paid usage**.
6. Output is written to the Actor's default dataset, as JSON exportable to CSV by Apify. The same JSON is printed in the logs.

## Safety and honesty
- This is **not** a lead generation service by itself: it only profiles URL candidates supplied by the user.
- Respect website terms, robots policies and rate limits; this prototype fetches one page per URL and limits input to 10 sites.
- Rejects most private/local hostnames, direct IP URLs and validates DNS. It is a prototype, not an audited multi-tenant SSRF isolation service.
- No personal email scraping (only common role-based business addresses in HTML).
- No email, CRM edits, payments, paid ads or subscriptions.
- Does not discover sites using search; no paid API calls.
- Failures are recorded transparently rather than fabricated.
- Source code public under the existing GitHub repository. Do not add private client data.

## Next milestone
Run a **real live website test**, review the extraction results, connect the Actor through the user's own Apify account, and only then evaluate store eligibility and pricing.
