import json, sys, rich
from importlib.metadata import version
print(json.dumps({"program": "python-venv", "prefix": sys.prefix, "executable": sys.executable, "rich": version("rich")}))
