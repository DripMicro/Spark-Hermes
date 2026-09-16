#!/bin/sh
# B2 exit test: a container on sh-ep reaches ONLY the proxy; every other destination is dropped and the drop is logged.
set -u
GW=172.30.0.1; PORT=${SH_PROXY_PORT:-8090}
probe() {  # probe NAME URL EXPECT(ok|blocked)
  out=$(docker run --rm --network sh-ep --add-host inference:$GW curlimages/curl:8.10.1 -s -o /dev/null -m 4 -w '%{http_code}' "$2" 2>&1); rc=$?
  if [ "$3" = ok ]; then [ "$rc" = 0 ] && r=PASS || r=FAIL; else [ "$rc" != 0 ] && r=PASS || r=FAIL; fi
  echo "$r $1 rc=$rc http=$out"
}
probe proxy            http://inference:$PORT/v1/models ok
probe host-loopback    http://$GW:8080/v1/models      blocked
probe internet         http://1.1.1.1/                blocked
probe dns              http://example.com/            blocked
docker run --rm --network sh-ep alpine:3.20 sh -c 'nc -z -w2 172.30.0.1 22 && echo "FAIL ssh reachable" || echo "PASS ssh blocked"'
echo "--- recent drops (kernel log) ---"; dmesg 2>/dev/null | grep -E 'sh-ep-drop' | tail -3 || journalctl -k --no-pager | grep -E 'sh-ep-drop' | tail -3
