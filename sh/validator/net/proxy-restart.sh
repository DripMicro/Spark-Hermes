#!/bin/sh
# (Re)start the inference proxy on the sh-ep gateway. Env: SH_PROXY_PORT, SH_UPSTREAM, SH_STATE (tokens + usage + log), SH_PKG.
set -eu
PORT=${SH_PROXY_PORT:-8090}; UP=${SH_UPSTREAM:-http://127.0.0.1:8080}; ST=${SH_STATE:-/var/lib/sh}
PKG=${SH_PKG:-$(cd "$(dirname "$0")/../../.." && pwd)}
mkdir -p "$ST/usage"
[ -f "$ST/proxy.pid" ] && kill "$(cat "$ST/proxy.pid")" 2>/dev/null || true
sleep 0.5
cd "$PKG" && nohup python3 -m sh.validator.proxy --listen 172.30.0.1:$PORT --upstream "$UP" --tokens "$ST/tokens" --usage-dir "$ST/usage" > "$ST/proxy.log" 2>&1 &
echo $! > "$ST/proxy.pid"; sleep 1; cat "$ST/proxy.log"
