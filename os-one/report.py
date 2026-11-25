import argparse
import json
from match import report

def main():
    parser=argparse.ArgumentParser(description="OS ONE MATCH local candidate comparison")
    parser.add_argument("request")
    parser.add_argument("offers")
    args=parser.parse_args()
    with open(args.request,encoding="utf-8") as f:
        request=json.load(f)
    with open(args.offers,encoding="utf-8") as f:
        offers=json.load(f)
    print(json.dumps(report(request,offers),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
