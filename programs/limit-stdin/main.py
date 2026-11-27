import json, sys
data = sys.stdin.buffer.read()
print(json.dumps({"program": "limit-stdin", "stdin_bytes": len(data)}))
