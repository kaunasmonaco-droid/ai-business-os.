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
    token = token.strip()
    actor = "Sd25i6Ior4ut8EwDa"
    data = get("acts/" + urllib.parse.quote(actor, safe="~"), token, "actor")
    if data.get("id"):
        print("APIFY_CHECK read_ok", flush=True)
        recent = get("acts/" + actor + "/runs?limit=10&desc=true", token, "actor_runs")
        print("APIFY_CHECK recent_runs=" + json.dumps([{k:x.get(k) for k in ("id","status","buildNumber","startedAt")} for x in recent.get("items",[])]), flush=True)
        builds = get("acts/" + actor + "/builds?limit=5&desc=true", token, "actor_builds")
        print("APIFY_CHECK builds=" + json.dumps([{k:b.get(k) for k in ("id","status","buildNumber","startedAt","finishedAt")} for b in builds.get("items",[])]), flush=True)
        contract = get("actor-runs/4ytBKgyvlcNLnNbO4", token, "contract_result")
        print("APIFY_CHECK contract_status="+str(contract.get("status")),flush=True)
        if contract.get("defaultKeyValueStoreId"):
            try:
                req=urllib.request.Request("https://api.apify.com/v2/key-value-stores/"+contract["defaultKeyValueStoreId"]+"/records/PROPOSAL_DRAFTS",headers={"Authorization":"Bearer "+token})
                with urllib.request.urlopen(req,timeout=12) as response:
                    value=json.load(response)
                    print("APIFY_CHECK contract_empty_array="+str(value == [])+" http="+str(response.status),flush=True)
            except urllib.error.HTTPError as exc:
                print("APIFY_CHECK contract_record_http="+str(exc.code),flush=True)
            except Exception as exc:
                print("APIFY_CHECK contract_error="+type(exc).__name__,flush=True)
        test = get("actor-runs/kpxl6LiDaBZ7U3kFK", token, "enrichment_result")
        print("APIFY_CHECK enrichment_status="+str(test.get("status")),flush=True)
        print("APIFY_CHECK enrichment_cost="+str(test.get("usageTotalUsd")),flush=True)
        for path,label in [(("datasets/"+test["defaultDatasetId"]+"/items?limit=10") if test.get("defaultDatasetId") else None,"enrichment_items"),(("key-value-stores/"+test["defaultKeyValueStoreId"]+"/records/PROPOSAL_DRAFTS") if test.get("defaultKeyValueStoreId") else None,"proposal_drafts")]:
            if not path:
                continue
            try:
                req=urllib.request.Request("https://api.apify.com/v2/"+path,headers={"Authorization":"Bearer "+token})
                with urllib.request.urlopen(req,timeout=12) as response:
                    items=json.load(response)
                    print("APIFY_CHECK "+label+"="+json.dumps([{k:x.get(k) for k in ("status","source_url","lead_priority","qualification_stage","dedup_key","requires_human_approval")} | {"enrichment_count":len(x.get("enrichment_sources",[]))} for x in items if isinstance(x,dict)]),flush=True)
            except Exception as exc:
                print("APIFY_CHECK "+label+"_error="+type(exc).__name__,flush=True)
        discovery = get("actor-runs/UJjwP1hXeVhtwwl37", token, "discovery_result")
        print("APIFY_CHECK discovery_status="+str(discovery.get("status")),flush=True)
        print("APIFY_CHECK discovery_cost="+str(discovery.get("usageTotalUsd")),flush=True)
        if discovery.get("defaultDatasetId"):
            req = urllib.request.Request("https://api.apify.com/v2/datasets/"+discovery["defaultDatasetId"]+"/items?limit=5",headers={"Authorization":"Bearer "+token})
            try:
                with urllib.request.urlopen(req,timeout=12) as response:
                    items=json.load(response)
                    print("APIFY_CHECK discovery_items="+json.dumps([{k:x.get(k) for k in ("status","source_url","title","lead_priority","error")} for x in items if isinstance(x,dict)]),flush=True)
            except Exception as exc:
                print("APIFY_CHECK discovery_read_error="+type(exc).__name__,flush=True)
        validation = get("actor-runs/ZDFBEUzKzlWp3DiJE", token, "validation_result")
        print("APIFY_CHECK validation_status=" + str(validation.get("status")), flush=True)
        print("APIFY_CHECK validation_cost=" + str(validation.get("usageTotalUsd")), flush=True)
        if validation.get("defaultDatasetId"):
            ds = get("datasets/" + validation["defaultDatasetId"], token, "validation_dataset")
            print("APIFY_CHECK validation_count=" + str(ds.get("itemCount")), flush=True)
        for b in builds.get("items",[])[:2]:
            if b.get("status") == "FAILED":
                detail = get("actor-builds/" + b["id"], token, "failed_build")
                req = urllib.request.Request("https://api.apify.com/v2/logs/" + b["id"], headers={"Authorization":"Bearer " + token})
                try:
                    with urllib.request.urlopen(req, timeout=12) as response:
                        lines = response.read(65536).decode("utf-8", "replace").splitlines()
                        for line in lines:
                            if any(w in line.lower() for w in ("schema", "error", "invalid", "failed")) and not any(w in line.lower() for w in ("token", "secret", "password", "authorization", "credential", "https://")):
                                print("APIFY_CHECK build_log=" + line[:350], flush=True)
                except Exception as exc:
                    print("APIFY_CHECK build_log_error=" + type(exc).__name__, flush=True)
                print("APIFY_CHECK build_error=" + json.dumps({k:detail.get(k) for k in ("statusMessage","exitCode")}), flush=True)
        run = get("actor-runs/Pd0hJbpIvLsYGXOVx", token, "smoke_result")
        print("APIFY_CHECK smoke_status=" + str(run.get("status")), flush=True)
        if run.get("defaultDatasetId"):
            dataset = get("datasets/" + run["defaultDatasetId"], token, "smoke_dataset")
            print("APIFY_CHECK dataset_item_count=" + str(dataset.get("itemCount")), flush=True)
            req = urllib.request.Request("https://api.apify.com/v2/datasets/" + run["defaultDatasetId"] + "/items?limit=5", headers={"Authorization":"Bearer " + token})
            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    items = json.load(response)
                    print("APIFY_CHECK result_summary=" + json.dumps([{"status":x.get("status"),"keys":sorted(x.keys())} for x in items if isinstance(x,dict)]), flush=True)
            except Exception as exc:
                print("APIFY_CHECK dataset_items_error=" + type(exc).__name__, flush=True)
        return
    for index, candidate in enumerate(["Sd25i6Ior4ut8EwDa", "Sd25i6lor4ut8EwDa", "Sd25i6ior4ut8EwDa", "aibusinessos~ai-business-agent"]):
        if candidate == actor:
            continue
        found = get("acts/" + urllib.parse.quote(candidate, safe="~"), token, "candidate_" + str(index))
        if found.get("id"):
            print("APIFY_CHECK resolved_read_ok actor_id=" + found["id"], flush=True)
            return
    get("acts/" + urllib.parse.quote(actor, safe="~") + "/runs?limit=1", token, "actor_runs")
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
