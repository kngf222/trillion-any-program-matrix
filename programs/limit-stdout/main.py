import json, sys
n = int(sys.argv[1])
w = sys.stdout.write
chunk = "x" * 1023 + "\n"
total = 0
while total + 1024 <= n - 80:
    w(chunk); total += 1024
w(json.dumps({"program": "limit-stdout", "filler_bytes": total}) + "\n")
