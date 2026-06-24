#!/usr/bin/env sh
./.venv/bin/pytest --ignore=test/webhost --color=yes |tee a.ans;tail -n +"$(grep -n "game='MathQuest'" a.ans | head -n 2 | tail -n 1 | cut -d: -f1)" a.ans>as.ans&&mv as.ans a.ans