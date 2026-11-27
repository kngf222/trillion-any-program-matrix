import json, os, sys
os.environ["SET_BY_ME"] = "yes"
stdin_text = sys.stdin.read()
print(json.dumps({"program": "reads-everything", "args": sys.argv[1:], "stdin": stdin_text, "file": open("data.txt").read(),
                  "own_env": os.environ["SET_BY_ME"], "cwd": os.getcwd(), "home": os.environ.get("HOME")}))
