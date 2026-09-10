#!/usr/bin/env python3
import json, urllib.request

raw = open("/home/davidos/.git-credentials").read().strip()
tok = raw.split(":")[2].split("@")[0]
API = "https://api.github.com/repos/Neolabs-clien...[truncated]