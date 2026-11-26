import os
import urllib.request
import urllib.error
import json

def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("APIFY_CHECK missing_token", flush=True)
        return
    req = urllib.request.Request("https://api.apify.com/v2/acts/aibusinessos~ai-business-agent", headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.load(response).get("data", {})
            print("APIFY_CHECK read_ok" if data.get("id") else "APIFY_CHECK unexpected_response", flush=True)
    except urllib.error.HTTPError as exc:
        print("APIFY_CHECK http_status=" + str(exc.code), flush=True)
    except Exception as exc:
        print("APIFY_CHECK error=" + type(exc).__name__, flush=True)

if __name__ == "__main__":
    main()
