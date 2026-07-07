#!/usr/bin/env python3
import sys, json
inp = json.loads(sys.stdin.read())
print(json.dumps({"echoed": inp.get("args", "")}))