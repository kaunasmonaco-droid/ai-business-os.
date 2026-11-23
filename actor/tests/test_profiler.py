import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import run, profile_one, validate_public_url

HTML = """<html><head><title>ACME Metal Works</title><meta name="description" content="Steel fabrication and OEM supplies"></head>
<body><h1>Company manufacturing OEM steel components</h1><p>Contact: info@acme.example and person@acme.example</p><script>SECRET</script></body></html>"""

def fake_fetch(url):
    return url, HTML

class ProfilingTests(unittest.TestCase):
    def test_match_source(self):
        r = profile_one("https://acme.example/", ["OEM", "metal", "manufacturing"], fake_fetch)
        self.assertEqual(r["title"], "ACME Metal Works")
        self.assertEqual(r["keyword_match_count"], 2)
        self.assertEqual(r["generic_contact_emails"], ["info@acme.example"])
        self.assertFalse(r["verified_buyer_interest"])
        self.assertNotIn("SECRET", r["public_evidence_excerpt"])

    def test_reject_private(self):
        for url in ["http://example.com", "https://localhost", "https://127.0.0.1", "https://user:pass@example.com", "https://internal.local/path"]:
            with self.assertRaises(ValueError):
                validate_public_url(url)

    def test_input_cap_and_duplicates(self):
        with self.assertRaises(ValueError):
            run({"urls": []}, fake_fetch)
        with self.assertRaises(ValueError):
            run({"urls": ["https://example.com"] * 11}, fake_fetch)
        self.assertEqual(len(run({"urls": ["https://acme.example", "https://acme.example"]}, fake_fetch)), 1)

    def test_error_per_site(self):
        def fail(url):
            raise ValueError("Website unavailable")
        result = run({"urls":["https://acme.example"]}, fail)
        self.assertEqual(result[0]["status"], "error")

if __name__ == "__main__":
    unittest.main()
