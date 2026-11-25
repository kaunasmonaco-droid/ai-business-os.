import unittest
from datetime import date
from match import match

class MatchTests(unittest.TestCase):
    def test_filters(self):
        req={"category":"rental","country":"ES","max_price":100,"currency":"EUR","required":["automatic"]}
        good={"category":"rental","country":"ES","price":80,"currency":"EUR","features":["automatic"],"url":"https://example.com/demo","expires":"2027-01-01"}
        offers=[good,good,{**good,"url":"https://example.com/expired","expires":"2025-01-01"},{**good,"url":"https://example.com/expensive","price":101},{**good,"url":"https://example.com/manual","features":[]},{**good,"url":"https://example.com/wrong","country":"FR"}]
        self.assertEqual(len(match(req,offers,date(2026,11,25))),1)
    def test_empty(self):
        self.assertEqual(match({"category":"job"},[]),[])
if __name__=="__main__":
    unittest.main()
