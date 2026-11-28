"""A secret provider for the key-source proof: the value lives in a file beside this program (values/<path>), never in
the Trillion vault. It prints {"value": ...}, which the provider row reads at /value. The value it holds is a made-up
test string, not a key."""
import json, os, sys

here = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else ""
full = os.path.normpath(os.path.join(here, "values", path))
if not full.startswith(os.path.join(here, "values") + os.sep):
    print(json.dumps({"error": "path_outside_values"})); sys.exit(1)
with open(full, encoding="utf-8") as f:
    print(json.dumps({"value": f.read().strip()}))
