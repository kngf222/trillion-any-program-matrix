import json, sys, tabulate
print(json.dumps({"program": "uv-project", "prefix": sys.prefix, "executable": sys.executable, "tabulate": tabulate.__version__}))
