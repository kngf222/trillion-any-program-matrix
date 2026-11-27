# trillion-any-program-matrix

Real programs, set up the way their authors set them up (npm, nvm, bun, deno, python, .venv, conda, uv, cargo, go, shell, a server,
docker, a vault key, a big local model), each with only a card in `tools/<name>/tool-rows.json` (the card and a `-contained` copy with
no capabilities). `programs/` holds the programs (build output, node_modules and .venv stay on the Mac and are git-ignored),
`MATRIX.md` the result of running each directly and through Trillion, `runs/` the raw output.

    python3 -I scripts/make-cards.py                # writes every card
    sh run-matrix.sh LABEL [CASE ...]               # runs every case directly and through Trillion; writes runs/<case>-LABEL.json
    python3 -I scripts/make-matrix-md.py before after   # writes MATRIX.md

Install the cards with `trillion op tools:update '{"source":"any-program-matrix","address":...,"files_blake3":...}' --pin f596fa0076f6c620`.
