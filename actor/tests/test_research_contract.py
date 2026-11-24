import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "main.py"
spec = importlib.util.spec_from_file_location("research_agent", path)
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)

class ResearchContractTests(unittest.TestCase):
    def test_public_https_required(self):
        for url in ("http://example.com", "https://localhost", "https://127.0.0.1", "https://user:pass@example.com", "https://example.com:8443"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                agent.validate_public_url(url)

    def test_evidence_and_no_fabricated_intent(self):
        def fetcher(url):
            return url, '<html><head><title>Metal Works</title><meta name="description" content="Industrial metal"></head><body>Manufacturing export contact info@example.com</body></html>'
        result = agent.profile_one("https://example.com", ["manufacturing", "export"], fetcher)
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["verified_buyer_interest"])
        self.assertEqual(result["keyword_match_count"], 2)
        self.assertIn("info@example.com", result["generic_contact_emails"])
        self.assertTrue(result["checked_at_utc"])

    def test_duplicate_urls_not_processed_twice(self):
        calls = []
        def fetcher(url):
            calls.append(url)
            return url, "<html><body>Metal</body></html>"
        result = agent.run({"urls":["https://example.com","https://example.com"],"keywords":["metal"]}, fetcher)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(calls), 1)

    def test_failures_are_not_marked_success(self):
        def fetcher(url):
            raise TimeoutError("offline")
        result = agent.run({"urls":["https://example.com"]}, fetcher)
        self.assertEqual(result[0]["status"], "error")
        self.assertFalse(result[0]["verified_buyer_interest"])

if __name__ == "__main__":
    unittest.main()
