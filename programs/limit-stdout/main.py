import json, sys
n = int(sys.argv[1])
line = json.dumps({"program": "limit-stdout", "total_bytes": n}) + "\n"
filler = n - len(line)
out = sys.stdout
chunk = "x" * 1023 + "\n"
while filler >= 1024:
    out.write(chunk)
    filler -= 1024
if filler > 0:
    out.write("y" * (filler - 1) + "\n")
out.write(line)
