"""Runs every case of the matrix directly and through Trillion; see ../run-matrix.sh.

For each case it writes runs/<case>-<label>.json:
  direct     how the author runs it: argv, cwd, exit code, seconds, last lines of stdout and stderr
  card       the card's run through `trillion op tools:run ... --pin PIN --verbose`: exit code, seconds, full output
  contained  the same card with no capabilities (tool:<name>-contained)
and runs/summary-<label>.md and runs/summary-<label>.json for the whole matrix.
The vault key of the TidyCal case goes only through a pipe, in memory of the shells; it is never an argument, a file or output.
"""
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAMS = ROOT + "/programs"
RUNS = ROOT + "/runs"
SCRATCH = os.environ.get("MATRIX_SCRATCH", "/Users/brianakhtar/dev/trillion-workshop/.git/scratch/matrix")
PIN = os.environ.get("MATRIX_PIN", "f596fa0076f6c620")
TRILLION = os.environ.get("TRILLION", "/Users/brianakhtar/.local/bin/trillion")
# The shell the author works in: this Mac's PATH starts with the nvm node.
AUTHOR_PATH = ("/Users/brianakhtar/.nvm/versions/node/v25.3.0/bin:/Users/brianakhtar/.bun/bin:/Users/brianakhtar/.local/bin:"
               "/Users/brianakhtar/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin")
LUX = "/Users/brianakhtar/dev/LuxTTS/.venv/bin/python"
WRAP = "/Users/brianakhtar/dev/trillion-wrap-luxtts/tools/say-words-in-a-voice/say.py"
TIDY = "/Users/brianakhtar/dev/try-a-plain-tool-with-a-key/tools/list-my-booking-types"
HELD = "/Users/brianakhtar/dev/trillion-apps/scripts/read-a-held-value.sh"
MIB = 1048576
MAX_OUT = 33554432


def pad_input(total):
    """The input {"pad", "rest"}; the card's stdin {"a": pad, "b": pad, "c": rest} is exactly `total` bytes long."""
    base = len(json.dumps({"a": "", "b": "", "c": ""}, separators=(",", ":")))
    half = (total - base) // 2
    return {"pad": "a" * half, "rest": "c" * (total - base - 2 * half)}


def pad_stdin(total):
    made = pad_input(total)
    return json.dumps({"a": made["pad"], "b": made["pad"], "c": made["rest"]}, separators=(",", ":"))


# case: card name, input, direct (argv, cwd, stdin text or None); a case may name `special`
def cases(label):
    vp = PROGRAMS + "/luxtts-voice/voice.wav"
    p = lambda n: PROGRAMS + "/" + n
    stdin_ro = {"first": "a", "second": "b"}
    ro = json.dumps(stdin_ro, separators=(",", ":"))
    return [
        dict(name="node-npm", card="node-npm", input={}, argv=["node", "main.mjs"], cwd=p("node-npm")),
        dict(name="node-nvm", card="node-nvm", input={}, argv=["node", "main.mjs"], cwd=p("node-nvm")),
        dict(name="bun-run", card="bun-run", input={}, argv=["bun", "main.ts"], cwd=p("bun-run")),
        dict(name="deno-run", card="deno-run", input={}, argv=["deno", "run", "main.ts"], cwd=p("deno-run")),
        dict(name="python-system", card="python-system", input={}, argv=["/usr/bin/python3", "main.py"], cwd=p("python-system")),
        dict(name="python-venv", card="python-venv", input={}, argv=[".venv/bin/python", "main.py"], cwd=p("python-venv")),
        dict(name="conda-python", card="conda-python", input={}, argv=["/opt/homebrew/anaconda3/bin/python", "main.py"], cwd=p("conda-python")),
        dict(name="uv-project", card="uv-project", input={}, argv=["uv", "run", "main.py"], cwd=p("uv-project")),
        dict(name="luxtts-voice", card="luxtts-voice", input={"text": "Trillion runs any program you already have.", "voice_file": vp,
                                                              "out_file": "%s/lux-%s.wav" % (SCRATCH, label)},
             argv=[LUX, WRAP], cwd="/Users/brianakhtar/dev/LuxTTS",
             stdin=json.dumps({"text": "Trillion runs any program you already have.", "voice_file": vp, "out_file": "%s/lux-direct-%s.wav" % (SCRATCH, label)}),
             special="wav"),
        dict(name="rust-bin", card="rust-bin", input={}, argv=["./target/release/rust-bin"], cwd=p("rust-bin")),
        dict(name="go-bin", card="go-bin", input={}, argv=["./go-bin"], cwd=p("go-bin")),
        dict(name="shell-script", card="shell-script", input={}, argv=["./run.sh"], cwd=p("shell-script")),
        dict(name="reads-everything", card="reads-everything", input=stdin_ro, argv=["/usr/bin/python3", "main.py", "a", "b"],
             cwd=p("reads-everything"), stdin=ro),
        dict(name="writes-binary", card="writes-binary", input={"out_file": "%s/png-%s.png" % (SCRATCH, label)},
             argv=["/usr/bin/python3", "main.py", "%s/png-direct-%s.png" % (SCRATCH, label)], cwd=p("writes-binary")),
        dict(name="http-server", card="http-server", input={"port": "47391"}, argv=["node", "main.mjs", "47392"], cwd=p("http-server"),
             special="server"),
        dict(name="vault-tidycal", card="vault-tidycal", input={}, cwd=TIDY, special="vault"),
        dict(name="network-example", card="network-example", input={}, argv=["node", "main.mjs"], cwd=p("network-example")),
        dict(name="pure-compute", card="pure-compute", input={"n": "30"}, argv=["/usr/bin/python3", "main.py", "30"], cwd=p("pure-compute")),
        dict(name="mac-only", card="mac-only", input={}, argv=["./run.sh"], cwd=p("mac-only")),
        dict(name="docker-alpine", card="docker-alpine", input={}, argv=["./run.sh"], cwd=p("docker-alpine")),
        dict(name="limit-stdin-under", card="limit-stdin", input=pad_input(MIB), argv=["/usr/bin/python3", "main.py"], cwd=p("limit-stdin"),
             stdin=pad_stdin(MIB)),
        dict(name="limit-stdin-over", card="limit-stdin", input=pad_input(MIB + 1), argv=["/usr/bin/python3", "main.py"], cwd=p("limit-stdin"),
             stdin=pad_stdin(MIB + 1)),
        dict(name="limit-stdout-under", card="limit-stdout", input={"bytes": str(MAX_OUT - 1)},
             argv=["/usr/bin/python3", "main.py", str(MAX_OUT - 1)], cwd=p("limit-stdout")),
        dict(name="limit-stdout-over", card="limit-stdout", input={"bytes": str(MAX_OUT + 1)},
             argv=["/usr/bin/python3", "main.py", str(MAX_OUT + 1)], cwd=p("limit-stdout")),
        dict(name="limit-read-dirs-8", card="limit-read-dirs-8", input={}, argv=["/opt/homebrew/anaconda3/bin/python", "main.py"],
             cwd=p("limit-read-dirs")),
        dict(name="limit-read-dirs-9", card="limit-read-dirs-9", input={}, argv=["/opt/homebrew/anaconda3/bin/python", "main.py"],
             cwd=p("limit-read-dirs")),
        dict(name="limit-duration-under", card="limit-duration", input={"seconds": "115"}, argv=["/usr/bin/python3", "main.py", "115"],
             cwd=p("limit-duration"), slow=True),
        dict(name="limit-duration-over", card="limit-duration", input={"seconds": "125"}, argv=["/usr/bin/python3", "main.py", "125"],
             cwd=p("limit-duration"), slow=True),
    ]


def last_json_line(text):
    for line in reversed(text.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def tail(text, n=1500):
    return text if len(text) <= n else "[%d bytes, last %d]\n" % (len(text), n) + text[-n:]


def run(argv=None, cwd=None, stdin=None, shell_cmd=None, timeout=400, env_path=True):
    env = dict(os.environ)
    if env_path:
        env["PATH"] = AUTHOR_PATH
    started = time.monotonic()
    try:
        done = subprocess.run(shell_cmd if shell_cmd else argv, cwd=cwd, input=None if stdin is None else stdin.encode(),
                              capture_output=True, timeout=timeout, env=env, shell=bool(shell_cmd))
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as late:
        code, out, err = "timeout", late.stdout or b"", late.stderr or b""
    seconds = round(time.monotonic() - started, 2)
    return code, seconds, out, err


def direct(case):
    if case.get("special") == "server":
        return direct_server(case)
    if case.get("special") == "vault":
        # the key goes only through the pipe: the held value is read by the vault script, the program gets it in its environment
        cmd = "sh %s read tidycal-api-token | sh -c 'TIDYCAL_API_TOKEN=$(cat) exec node %s/list.mjs'" % (HELD, TIDY)
        code, seconds, out, err = run(shell_cmd=cmd, cwd=TIDY)
        argv = ["sh", HELD, "read", "tidycal-api-token", "|", "sh", "-c", "TIDYCAL_API_TOKEN=$(cat) exec node list.mjs"]
    else:
        argv = case["argv"]
        code, seconds, out, err = run(argv=argv, cwd=case["cwd"], stdin=case.get("stdin"))
    text = out.decode("utf-8", "replace")
    answer = last_json_line(text)
    return {"argv": argv, "cwd": case["cwd"], "exit": code, "seconds": seconds, "worked": code == 0 and answer is not None,
            "stdout_bytes": len(out), "last_json_line": answer, "stdout_tail": tail(text, 600), "stderr_tail": tail(err.decode("utf-8", "replace"))}


def direct_server(case):
    started = time.monotonic()
    proc = subprocess.Popen(case["argv"], cwd=case["cwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=dict(os.environ, PATH=AUTHOR_PATH))
    first = proc.stdout.readline().decode()
    port = case["argv"][-1]
    got = subprocess.run(["/usr/bin/curl", "-s", "http://127.0.0.1:%s/hello" % port], capture_output=True, timeout=20).stdout.decode()
    seconds = round(time.monotonic() - started, 2)
    proc.terminate()  # by its own pid
    proc.wait(timeout=20)
    answer = last_json_line(first)
    return {"argv": case["argv"], "cwd": case["cwd"], "exit": 0, "seconds": seconds, "worked": answer is not None and "hello" in got,
            "last_json_line": answer, "http_reply": got, "stdout_tail": first}


def through_trillion(tool, payload, name, label):
    file = "%s/%s-%s-%s.json" % (SCRATCH, name, tool.replace("tool:", ""), label)
    with open(file, "w") as handle:
        json.dump({"tool": tool, "input": payload}, handle)
    code, seconds, out, err = run(argv=[TRILLION, "op", "tools:run", "@" + file, "--pin", PIN, "--verbose", "--timeout", "300"],
                                  timeout=420, env_path=False)
    text = out.decode("utf-8", "replace")
    error = err.decode("utf-8", "replace")
    reference = re.findall(r"Reference: ([0-9a-f-]{36})", text + error)
    return {"tool": tool, "exit": code, "seconds": seconds, "worked": code == 0, "reference": reference[-1] if reference else None,
            "stdout_bytes": len(out), "stdout_tail": tail(text), "stderr": tail(error, 4000)}


def through_trillion_server(tool, payload, name, label):
    first = through_trillion(tool, payload, name, label)
    if not first["worked"]:
        return first
    answer = None
    try:
        answer = json.loads(first["stdout_tail"])
    except ValueError:
        pass
    key = (answer or {}).get("run")
    first["session_run"] = key
    if not key:
        first["worked"] = False
        first["note"] = "no session run key in the answer"
        return first
    time.sleep(2)
    for method in ("tools:read", "tools:cancel"):
        code, seconds, out, err = run(argv=[TRILLION, "op", method, json.dumps({"run": key}), "--pin", PIN, "--verbose"], env_path=False)
        first[method.split(":")[1]] = {"exit": code, "seconds": seconds, "stdout": tail(out.decode("utf-8", "replace"), 2500),
                                       "stderr": tail(err.decode("utf-8", "replace"), 2000)}
    first["worked"] = first["read"]["exit"] == 0 and first["cancel"]["exit"] == 0
    return first


def wav_check(path):
    """Length of a wav file, and the words in it when mlx_whisper is on this Mac."""
    if not os.path.exists(path):
        return {"file": path, "exists": False}
    info = {"file": path, "exists": True, "bytes": os.path.getsize(path)}
    code, seconds, out, err = run(argv=["/usr/bin/afinfo", path], timeout=30)
    match = re.search(r"estimated duration: ([0-9.]+)", out.decode("utf-8", "replace"))
    info["seconds_of_audio"] = float(match.group(1)) if match else None
    whisper = "/opt/homebrew/anaconda3/bin/mlx_whisper"
    if os.path.exists(whisper):
        folder = os.path.dirname(path)
        code, seconds, out, err = run(argv=[whisper, path, "--model", "mlx-community/whisper-base-mlx", "--output-format", "txt",
                                            "--output-dir", folder, "--language", "en"], timeout=200)
        txt = os.path.splitext(path)[0] + ".txt"
        info["speech_to_text"] = open(txt).read().strip() if os.path.exists(txt) else "mlx_whisper exit %s: %s" % (code, err.decode("utf-8", "replace")[-300:])
    return info


def run_case(case, label):
    name = case["name"]
    record = {"case": name, "label": label, "card": case["card"], "date": time.strftime("%Y-%m-%d %H:%M:%S %Z")}
    record["direct"] = direct(case)
    trillion = through_trillion_server if case.get("special") == "server" else through_trillion
    record["through_trillion"] = trillion("tool:" + case["card"], case["input"], name, label)
    record["contained"] = through_trillion("tool:%s-contained" % case["card"], case["input"], name, label)
    if case.get("special") == "wav":
        record["direct"]["wav"] = wav_check(json.loads(case["stdin"])["out_file"])
        record["through_trillion"]["wav"] = wav_check(case["input"]["out_file"])
    if name == "writes-binary":
        record["through_trillion"]["file_exists"] = os.path.exists(case["input"]["out_file"])
    with open("%s/%s-%s.json" % (RUNS, name, label), "w") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    return record


def word(section):
    return ("ok %ss" if section["worked"] else "FAILED %ss") % section["seconds"]


def refusal(section):
    if section["worked"]:
        return ""
    return " ".join(section["stderr"].split()) if "stderr" in section else " ".join(section.get("stderr_tail", "").split())


def main():
    label = sys.argv[1]
    only = set(sys.argv[2:])
    os.makedirs(SCRATCH, exist_ok=True)
    os.makedirs(RUNS, exist_ok=True)
    chosen = [c for c in cases(label) if not only or c["name"] in only]
    records = [run_case(c, label) for c in chosen if not c.get("slow")]
    with ThreadPoolExecutor(max_workers=4) as pool:  # the 115 s and 125 s runs overlap each other
        records += list(pool.map(lambda c: run_case(c, label), [c for c in chosen if c.get("slow")]))
    records = []
    for case in cases(label):
        path = "%s/%s-%s.json" % (RUNS, case["name"], label)
        if os.path.exists(path):
            records.append(json.load(open(path)))
    summary = ["# Matrix summary, label %s, %s" % (label, time.strftime("%Y-%m-%d %H:%M:%S %Z")), "",
               "| case | direct | through Trillion (card) | contained card |", "|---|---|---|---|"]
    for r in records:
        summary.append("| %s | %s | %s %s | %s %s |" % (r["case"], word(r["direct"]), word(r["through_trillion"]), refusal(r["through_trillion"])[:700],
                                                         word(r["contained"]), refusal(r["contained"])[:700]))
    with open("%s/summary-%s.md" % (RUNS, label), "w") as handle:
        handle.write("\n".join(summary) + "\n")
    with open("%s/summary-%s.json" % (RUNS, label), "w") as handle:
        json.dump([{"case": r["case"], "direct": [r["direct"]["worked"], r["direct"]["seconds"]],
                    "card": [r["through_trillion"]["worked"], r["through_trillion"]["seconds"]],
                    "contained": [r["contained"]["worked"], r["contained"]["seconds"]]} for r in records], handle, indent=1)
    print("\n".join(summary))


main()
