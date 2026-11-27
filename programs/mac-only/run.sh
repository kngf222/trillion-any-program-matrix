#!/bin/sh
echo "{\"program\":\"mac-only\",\"product\":\"$(sw_vers -productName)\",\"version\":\"$(sw_vers -productVersion)\",\"kind\":\"$(mdls -raw -name kMDItemKind note.txt)\",\"osascript\":\"$(osascript -e 'return (system version of (system info))')\"}"
