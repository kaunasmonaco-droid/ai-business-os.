"""Single-contact CRM pilot. No paid API, no email sending."""
import argparse, json, os, re, urllib.request, urllib.error
from pathlib import Path

def api(method, path, data=None):
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Missing HUBSPOT_ACCESS_TOKEN")
    req = urllib.request.Request("https://api.hubapi.com"+path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},method=method)
    with urllib.request.urlopen(req,timeout=20) as response:
        return json.load(response)

def pilot(profile, email, company, offer, apply=False):
    email=email.strip().lower()
    if profile.get("status")!="ok" or email not in profile.get("generic_contact_emails",[]):
        raise ValueError("Contact must appear in successful source profile")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email):
        raise ValueError("Invalid email")
    if not company.strip() or not offer.strip():
        raise ValueError("Company and reviewed individual offer required")
    result={"company":company,"email":email,"source":profile["source_url"],
            "proposal":offer,"buyer_interest_verified":False,"sent":False,"crm_id":None}
    if not apply:
        return result
    search=api("POST","/crm/v3/objects/contacts/search",{"filterGroups":[{"filters":[{"propertyName":"email","operator":"EQ","value":email}]}],"limit":2})
    matches=search.get("results",[])
    if len(matches)>1:
        raise RuntimeError("Duplicate contacts require review")
    if matches:
        result.update(crm_id=matches[0]["id"],crm_status="existing")
    else:
        try:
            created=api("POST","/crm/v3/objects/contacts",{"properties":{"email":email,"company":company,"website":profile["source_url"]}})
            result.update(crm_id=created["id"],crm_status="created")
        except urllib.error.HTTPError as exc:
            if exc.code!=409:
                raise
            raise RuntimeError("Concurrent duplicate; rerun search") from None
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--profile",required=True)
    p.add_argument("--email",required=True)
    p.add_argument("--company",required=True)
    p.add_argument("--offer-file",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    profiles=json.loads(Path(a.profile).read_text())
    matches=[x for x in profiles if a.email.lower() in x.get("generic_contact_emails",[])]
    if len(matches)!=1:
        raise SystemExit("Expected exactly one source profile")
    result=pilot(matches[0],a.email,a.company,Path(a.offer_file).read_text(),a.apply)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
