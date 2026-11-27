import json, sys, numpy
print(json.dumps({"program": "conda-python", "prefix": sys.prefix, "executable": sys.executable, "numpy": numpy.__version__}))
