"""Writes MATRIX.md from runs/<case>-<label>.json for the labels given: python3 -I scripts/make-matrix-md.py before [after]"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
labels = sys.argv[1:] or ["before"]

BEYOND = {
    "vault-tidycal": "none beyond the card; direct run reads the key through a pipe only",
    "luxtts-voice": "none beyond the card; voice.wav is a local reference voice kept out of git",
    "docker-alpine": "none beyond the card; needs OrbStack running",
    "http-server": "card adds session.keep_open",
}


def cell(section):
    if section is None:
        return "not run"
    state = "worked" if section.get("worked") else "REFUSED/FAILED"
    text = "%s, %ss" % (state, section["seconds"])
    if section.get("worked"):
        answer = section.get("last_json_line")
        if answer is None:
            text += " (stdout: %s)" % " ".join(section.get("stdout_tail", "").split())[:150]
        else:
            text += " `%s`" % json.dumps(answer)[:200]
    else:
        said = section.get("stderr") or section.get("stderr_tail") or ""
        text += ": " + " ".join(said.split()).replace("|", "/")
    return text


def load(label):
    rows = {}
    for path in sorted(glob.glob("%s/runs/*-%s.json" % (ROOT, label))):
        if os.path.basename(path).startswith("summary-"):
            continue
        record = json.load(open(path))
        rows[record["case"]] = record
    return rows


data = {label: load(label) for label in labels}
names = list(data[labels[0]].keys())
out = ["# Matrix of real programs, run directly and through Trillion", "",
       "Repo: https://github.com/kngf222/trillion-any-program-matrix. Raw output: `runs/<case>-<label>.json`. "
       "Each case is run three ways: directly as its author runs it; through its card (`tool:<name>`, capability `use-this-computer-as-you`); "
       "through the same card with no capabilities (`tool:<name>-contained`). Refusals are quoted word for word with their Reference and the "
       "`--verbose` source line.", ""]
for label in labels:
    out += ["## Label: %s" % label, "",
            "| program (case) | how the author runs it | direct | through Trillion: card | through Trillion: contained card | file or step beyond the card |",
            "|---|---|---|---|---|---|"]
    for name in names:
        r = data[label].get(name)
        if r is None:
            continue
        argv = r["direct"].get("argv") or []
        how = "`cd %s && %s`" % (os.path.relpath(r["direct"]["cwd"], "/Users/brianakhtar/dev"), " ".join(argv)) if argv else ""
        out.append("| %s | %s | %s | %s | %s | %s |" % (name, how.replace("|", "/"), cell(r["direct"]), cell(r["through_trillion"]),
                                                          cell(r["contained"]), BEYOND.get(name, "none beyond the card")))
    out.append("")
out += ["## Notes", "",
        "- Install and list needed no step beyond the card: no package-files.json and no pinned-files.json were added. "
        "`tools:update` accepted the pin (58 files first, 91 after the runs were added) and `tools:list` showed both cards of every program.",
        "- Card refusal (before the new capability): every card is refused at `src/tool_runs/tools/computer.rs:197:28` with `capability_not_reported`, "
        "naming `use-this-computer-as-you`. No program started.",
        "- Contained card (capabilities `[]`): every one is refused at `src/tool_runs/tools/container.rs:692:28` with `Failure::NotRunnableHere`: "
        "a contained run starts only programs it declares, inside its own folder, and the cards name a workdir and programs on this Mac outside it.",
        "- The command line (`trillion op ... @FILE`) refuses an input file over 1048576 bytes before any engine sees it "
        "(`The input file ... is 1048617 bytes; an input is at most 1048576.`). The stdin probe therefore builds the program's stdin from "
        "the `pad` field twice plus `rest`, so the request file is about 524 KB and the stdin is exactly 1048576 (under) or 1048577 (over) bytes.",
        "- Direct times are wall time on a Mac with a load average near 9 (other lanes were working); LuxTTS direct took 29 s to 51 s here "
        "(its own report: load 3.7 s to 4.0 s, speak 10.4 s to 28.5 s), not the 7 s to 9 s measured on a quiet Mac. Its wav says "
        "\"Trillion runs any program you already have.\" when read by mlx_whisper (whisper-base).",
        "- The vault row's direct run sends the key only through a pipe. Through Trillion it is mounted from the vault by `credential_mounts`.",
        "- Deno was not installed; `brew install deno` succeeded (deno 2.9.8, /opt/homebrew/bin/deno).",
        "- `python-system` uses `/usr/bin/python3`, which on this Mac is Apple's Xcode python 3.9.6 (the author's plain `python3` is Anaconda's 3.10.9, covered by `conda-python`).",
        ""]
with open(ROOT + "/MATRIX.md", "w") as handle:
    handle.write("\n".join(out) + "\n")
print("MATRIX.md written with", len(names), "cases")
