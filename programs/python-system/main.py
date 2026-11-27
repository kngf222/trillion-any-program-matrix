import json, sys
print(json.dumps({"program": "python-system", "version": sys.version.split()[0], "executable": sys.executable, "prefix": sys.prefix}))
