#!/usr/bin/python3 -I
"""Writes tools/<name>/tool-rows.json: for each program, the card and a second card `-contained` with no capabilities."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAMS = ROOT + "/programs"
LUX = "/Users/brianakhtar/dev/LuxTTS/.venv/bin/python"
NO_INPUT = {"type": "object", "additionalProperties": False, "properties": {}}


def fill(field):
    return {"fill": {"from": "input", "field": field}}


def schema(**props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": {k: {"type": "string"} for k in props}}


# name: (label, job, input_schema, argv, extras, workdir override)
CARDS = {
    "node-npm": ("Node with an npm package", "Run a Node program that uses dayjs from its own node_modules", NO_INPUT, ["node", "main.mjs"], {}),
    "node-nvm": ("Node from nvm", "Run a Node program; print which node ran", NO_INPUT, ["node", "main.mjs"], {}),
    "bun-run": ("Bun", "Run a TypeScript program with Bun", NO_INPUT, ["bun", "main.ts"], {}),
    "deno-run": ("Deno", "Run a TypeScript program with Deno", NO_INPUT, ["deno", "run", "main.ts"], {}),
    "python-system": ("System Python", "Run a Python program with the system python (/usr/bin/python3)", NO_INPUT, ["/usr/bin/python3", "main.py"], {}),
    "python-venv": ("Python in a .venv", "Run a Python program with its own .venv and a package", NO_INPUT, [".venv/bin/python", "main.py"], {}),
    "conda-python": ("Conda Python", "Run a Python program with the Anaconda python", NO_INPUT, ["/opt/homebrew/anaconda3/bin/python", "main.py"], {}),
    "uv-project": ("uv project", "Run a Python program with uv and a dependency in pyproject.toml", NO_INPUT, ["uv", "run", "main.py"], {}),
    "luxtts-voice": ("LuxTTS voice (big local model)", "Say words in a voice with LuxTTS through the existing wrapper script", schema(text="", voice_file="", out_file=""),
                     [LUX, "/Users/brianakhtar/dev/trillion-wrap-luxtts/tools/say-words-in-a-voice/say.py"], {"stdin": {"fill": {"from": "input"}}},
                     "/Users/brianakhtar/dev/LuxTTS"),
    "rust-bin": ("Compiled Rust binary", "Run a binary built with cargo build --release", NO_INPUT, ["./target/release/rust-bin"], {}),
    "go-bin": ("Compiled Go binary", "Run a binary built with go build", NO_INPUT, ["./go-bin"], {}),
    "shell-script": ("Shell script", "Run a zsh script with a shebang", NO_INPUT, ["./run.sh"], {}),
    "reads-everything": ("Reads stdin, args, a file and its own env", "Echo what the program got on stdin, in args, in a file and in an environment variable it sets", schema(first="", second=""),
                         ["/usr/bin/python3", "main.py", fill("first"), fill("second")], {"stdin": {"fill": {"from": "input"}}}),
    "writes-binary": ("Writes a PNG", "Write a PNG to the path the input names; print its size and hash", schema(out_file=""), ["/usr/bin/python3", "main.py", fill("out_file")], {}),
    "http-server": ("HTTP server", "Start a small HTTP server and keep it open", schema(port=""), ["node", "main.mjs", fill("port")], {"session": {"keep_open": True}}),
    "vault-tidycal": ("TidyCal booking types (vault key)", "Count TidyCal booking types with the key mounted from the vault", NO_INPUT, ["node", "list.mjs"],
                      {"internet": True, "credential_mounts": [{"secret_name": "tidycal-api-token", "env": "TIDYCAL_API_TOKEN"}]},
                      "/Users/brianakhtar/dev/try-a-plain-tool-with-a-key/tools/list-my-booking-types"),
    "network-example": ("Fetch example.com", "Fetch https://example.com and print status and byte count", NO_INPUT, ["node", "main.mjs"], {"internet": True}),
    "pure-compute": ("Pure computation", "Print the nth Fibonacci number", schema(n=""), ["/usr/bin/python3", "main.py", fill("n")], {}),
    "mac-only": ("Mac-only tools", "Run sw_vers, mdls and osascript", NO_INPUT, ["./run.sh"], {}),
    "docker-alpine": ("Docker image", "Run an alpine container with docker", NO_INPUT, ["./run.sh"], {}),
    # stdin is built from two input fields, so the whole request stays under the command line's own 1 MiB input-file limit
    # while the stdin the program gets can pass the engine's max_stdin_bytes.
    "limit-stdin": ("Limit probe: stdin size", "Count the bytes on stdin", schema(pad="", rest=""),
                    ["/usr/bin/python3", "main.py"], {"stdin": {"a": fill("pad"), "b": fill("rest")}}),
    "limit-stdout": ("Limit probe: stdout size", "Print about N bytes on stdout", schema(bytes=""), ["/usr/bin/python3", "main.py", fill("bytes")], {}),
    "limit-duration": ("Limit probe: run time", "Sleep N seconds, no max_run_ms", schema(seconds=""), ["/usr/bin/python3", "main.py", fill("seconds")], {}),
}
for n in (8, 9):
    dirs = [PROGRAMS + "/limit-read-dirs/d%d" % i for i in range(1, n + 1)]
    CARDS["limit-read-dirs-%d" % n] = (
        "Limit probe: %d runtime_read_dirs" % n, "A declared program with %d runtime_read_dirs" % n, NO_INPUT, ["conda-py", "main.py"],
        {"programs": {"conda-py": {"search": "python", "search_path": ["/opt/homebrew/anaconda3/bin"], "runtime_read_dirs": dirs}}},
        PROGRAMS + "/limit-read-dirs")


def card(tool_id, label, job, input_schema, argv, extras, workdir, capabilities):
    invoke = {"kind": "computer", "capabilities": capabilities, "workdir": workdir, "argv": argv, "stdout": "json"}
    invoke.update(extras)
    return {"payload": {"kind": "ai-tool-descriptor", "id": tool_id, "label": label, "job": job, "status": "active",
                        "input_schema": input_schema, "invoke": invoke,
                        "needs": {"expected_seconds": 10, "network_egress": bool(extras.get("internet"))},
                        "placements": ["placement:your-computer"]}}


for name, spec in CARDS.items():
    label, job, input_schema, argv, extras = spec[:5]
    workdir = spec[5] if len(spec) > 5 else PROGRAMS + "/" + name
    records = [card("tool:" + name, label, job, input_schema, argv, extras, workdir, ["use-this-computer-as-you"]),
               card("tool:%s-contained" % name, label + " (contained)", job, input_schema, argv, extras, workdir, [])]
    os.makedirs(ROOT + "/tools/" + name, exist_ok=True)
    with open(ROOT + "/tools/%s/tool-rows.json" % name, "w") as f:
        json.dump({"records": records}, f, indent=2)
        f.write("\n")
print(len(CARDS), "programs")
