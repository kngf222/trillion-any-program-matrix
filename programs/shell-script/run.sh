#!/bin/zsh
print -r -- "{\"program\":\"shell-script\",\"shell\":\"$ZSH_VERSION\",\"cwd\":\"$PWD\",\"uname\":\"$(uname -sm)\"}"
