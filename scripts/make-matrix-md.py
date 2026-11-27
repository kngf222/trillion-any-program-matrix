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
with open(ROOT + "/MATRIX.md", "w") as handle:
    handle.write("\n".join(out) + "\n")
print("MATRIX.md written with", len(names), "cases")
