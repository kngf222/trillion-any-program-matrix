import json, sys, time
s = float(sys.argv[1])
time.sleep(s)
print(json.dumps({"program": "limit-duration", "slept_s": s}))
