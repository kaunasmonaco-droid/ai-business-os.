import os
import urllib.parse
import urllib.request
import urllib.error
import json

def get(path, token, label):
    req = urllib.request.Request("https://api.apify.com/v2/" + path, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.load(response).get("data", {})
            print("APIFY_CHECK " + label + " http=200", flush=True)
            return data
    except urllib.error.HTTPError as exc:
        print("APIFY_CHECK " + label + " http=" + str(exc.code), flush=True)
    except Exception as exc:
        print("APIFY_CHECK " + label + " error=" + type(exc).__name__, flush=True)
    return {}

def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("APIFY_CHECK missing_token", flush=True)
        return
    actor = os.environ.get("APIFY_ACTOR_ID", "Sd25i6lor4ut8EwDa")
    data = get("acts/" + urllib.parse.quote(actor, safe="~"), token, "actor")
    if data.get("id"):
        print("APIFY_CHECK read_ok", flush=True)
        return
    for index, candidate in enumerate(["Sd25i6Ior4ut8EwDa", "Sd25i6lor4ut8EwDa", "Sd25i6ior4ut8EwDa", "aibusinessos~ai-business-agent"]):
        if candidate == actor:
            continue
        found = get("acts/" + urllib.parse.quote(candidate, safe="~"), token, "candidate_" + str(index))
        if found.get("id"):
            print("APIFY_CHECK resolved_read_ok actor_id=" + found["id"], flush=True)
            return
    get("users/me", token, "identity")
    listing = get("acts?limit=100", token, "actor_list")
    for item in listing.get("items", []):
        if item.get("name") == "ai-business-agent" and item.get("id"):
            found = get("acts/" + urllib.parse.quote(item["id"], safe=""), token, "resolved_actor")
            if found.get("id"):
                print("APIFY_CHECK resolved_read_ok", flush=True)
                return
    print("APIFY_CHECK actor_not_resolved", flush=True)

if __name__ == "__main__":
    main()
