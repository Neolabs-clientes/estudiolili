#!/usr/bin/env python3
"""Deploy demo Lili a la org de clientes. Uso: _deploy.py <create|pages|verify>"""
import json, os, re, sys, urllib.request, urllib.error

HOME = os.path.expanduser("~")
ORG = "Neolabs-clientes"
REPO = "estudiolili"
BRANCH = "main"
URL = "https://neolabs-clientes.github.io/%s/" % REPO

def token():
    env = os.path.join(HOME, ".hermes/.env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8", errors="ignore"):
            m = re.match(r"\s*(?:GITHUB_TOKEN|GH_TOKEN|GITHUB_PAT)\s*=\s*['\"]?([A-Za-z0-9_\-]+)", line)
            if m:
                return m.group(1).strip()
    creds = os.path.join(HOME, ".git-credentials")
    if os.path.exists(creds):
        m = re.search(r"https://([^:@/]+):([^@]+)@github\.com", open(creds, encoding="utf-8", errors="ignore").read())
        if m:
            return m.group(2).strip()
    return os.environ.get("GITHUB_TOKEN", "")

TOKEN = token()

def api(method, path, payload=None):
    req = urllib.request.Request("https://api.github.com" + path,
                                data=json.dumps(payload).encode() if payload is not None else None,
                                method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "neo-deploy")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"error": "http %d" % e.code}
    except Exception as e:
        return 0, {"error": str(e)[:200]}

action = sys.argv[1] if len(sys.argv) > 1 else "create"

if action == "create":
    st, r = api("GET", "/repos/%s/%s" % (ORG, REPO))
    if st == 200:
        print("repo ya existe:", r.get("full_name"))
    else:
        st, r = api("POST", "/orgs/%s/repos" % ORG, {
            "name": REPO,
            "description": "Demo premium para Estudio de unas Lili (Madrid) - manicura rusa y unas de gel",
            "private": False, "has_issues": False, "has_wiki": False, "auto_init": False
        })
        print("crear repo:", st, r.get("full_name") or str(r)[:200])

elif action == "pages":
    st, r = api("POST", "/repos/%s/%s/pages" % (ORG, REPO),
                {"source": {"branch": BRANCH, "path": "/"}})
    print("activar pages:", st, (r.get("html_url") or r.get("message") or str(r)[:200]))
    st2, r2 = api("PUT", "/repos/%s/%s/pages" % (ORG, REPO),
                  {"source": {"branch": BRANCH, "path": "/"}, "build_type": "legacy"})
    print("forzar source:", st2, (r2.get("html_url") or r2.get("message") or "")[:160])

elif action == "verify":
    st, r = api("GET", "/repos/%s/%s/pages" % (ORG, REPO))
    print("pages:", st, r.get("status"), r.get("html_url"), "| branch:", (r.get("source") or {}).get("branch"))
    st2, r2 = api("GET", "/repos/%s/%s" % (ORG, REPO))
    print("repo:", st2, r2.get("full_name"), "| default_branch:", r2.get("default_branch"), "| private:", r2.get("private"))
