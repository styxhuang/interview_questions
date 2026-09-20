#!/bin/sh
set -eu

printf '{"ok":true,"marker":"bohrium-agent-interview-real-smoke"}\n' > result.json
uname -a > environment.txt
printf 'real Bohrium smoke job completed\n'
