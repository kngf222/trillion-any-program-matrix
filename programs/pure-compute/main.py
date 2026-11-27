import json, sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
a, b = 0, 1
for _ in range(n): a, b = b, a + b
print(json.dumps({"program": "pure-compute", "n": n, "fib": a}))
