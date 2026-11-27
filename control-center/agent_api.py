import os,json,hmac,re,urllib.request,urllib.error,threading,time
LOCK=threading.Lock()
LAST_RUN=0
RUN_COUNT=0
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ACTOR="Sd25i6Ior4ut8EwDa"
def api(path,payload=None):
    token=os.environ["APIFY_TOKEN"]
    req=urllib.request.Request("https://api.apify.com/v2/"+path,data=None if payload is None else json.dumps(payload).encode(),headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as response:
        return json.load(response)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def reply(self,status,value):
        body=json.dumps(value,ensure_ascii=False).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def authorized(self):
        secret=os.environ.get("CONTROL_TOKEN","")
        return len(secret)>=32 and hmac.compare_digest(self.headers.get("Authorization","").encode(),("Bearer "+secret).encode())
    def do_GET(self):
        if self.path=="/":
            body=Path(__file__).with_name("index.html").read_bytes()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body);return
        if not self.authorized(): return self.reply(401,{"error":"Unauthorized"})
        try:
            if self.path=="/api/runs":
                data=api("acts/"+ACTOR+"/runs?limit=10&desc=true")["data"]["items"]
                return self.reply(200,[{k:x.get(k) for k in ("id","status","startedAt","finishedAt","usageTotalUsd")} for x in data])
            return self.reply(404,{"error":"Not found"})
        except Exception: return self.reply(502,{"error":"Agent API unavailable"})
    def do_POST(self):
        if not self.authorized(): return self.reply(401,{"error":"Unauthorized"})
        if self.path!="/api/run": return self.reply(404,{"error":"Not found"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if not 0<n<=8192: return self.reply(400,{"error":"Invalid size"})
            x=json.loads(self.rfile.read(n))
            country=x.get("country","");keywords=x.get("keywords",[])
            if not isinstance(country,str) or not re.fullmatch("[A-Z]{2}",country) or not isinstance(keywords,list) or not 1<=len(keywords)<=8 or not all(isinstance(k,str) and 1<=len(k)<=100 for k in keywords): return self.reply(400,{"error":"Invalid task"})
            payload={"discovery_country":country,"keywords":keywords,"result_limit":5,"sales_pipeline":False,"sync_hubspot":False}
            global LAST_RUN,RUN_COUNT
            with LOCK:
                if RUN_COUNT>=10 or time.monotonic()-LAST_RUN<120 and LAST_RUN!=0: return self.reply(429,{"error":"Test limit or cooldown reached"})
                LAST_RUN=time.monotonic()
                RUN_COUNT+=1
                data=api("acts/"+ACTOR+"/runs?build=0.0.46&timeout=120&maxTotalChargeUsd=0.01",payload)["data"]
            return self.reply(202,{"id":data["id"],"status":data["status"]})
        except Exception: return self.reply(502,{"error":"Request failed; verify run history before retrying"})
if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","8080"))),Handler).serve_forever()
