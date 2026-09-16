#!/bin/sh
# B2 — the episode network (spec §12.1). Idempotent; run as root on the validator host after every boot.
#
#   sh-ep       172.30.0.0/24, gateway 172.30.0.1, no inter-container traffic, no masquerade
#   SH_EP_IN    (from INPUT)       containers reach ONLY the proxy at 172.30.0.1:${SH_PROXY_PORT:-8090}
#   SH_EP_FWD   (from DOCKER-USER) nothing leaves sh-ep — DOCKER-USER runs before Docker's own accept rules
#   SH_EP_DROP  final drop; the episode driver inserts one count-only rule per container IP at its top and reads the
#               counter back as the episode's `dropped_packets` (kernel LOG lines are not readable on every host;
#               packet counters are)
#
# Episodes run with `--network sh-ep --dns 172.30.0.1 --add-host inference:172.30.0.1` and use http://inference:8090/v1.
set -eu
NET=sh-ep; SUBNET=172.30.0.0/24; GW=172.30.0.1; PORT=${SH_PROXY_PORT:-8090}

docker network inspect "$NET" >/dev/null 2>&1 || docker network create \
  --driver bridge --subnet "$SUBNET" --gateway "$GW" \
  -o com.docker.network.bridge.name="$NET" \
  -o com.docker.network.bridge.enable_icc=false \
  -o com.docker.network.bridge.enable_ip_masquerade=false \
  "$NET"

chain() { iptables -N "$1" 2>/dev/null || true; }
chain SH_EP_DROP; iptables -C SH_EP_DROP -j DROP 2>/dev/null || iptables -A SH_EP_DROP -j DROP   # never flushed: live accounting rules
for r in "-p udp --dport 53" "-p tcp --dport 443" "-p tcp --dport 80" "-p tcp --dport 22"; do        # what escapes are aimed at (diagnostic)
  # shellcheck disable=SC2086
  iptables -C SH_EP_DROP $r 2>/dev/null || iptables -I SH_EP_DROP 1 $r
done
chain SH_EP_IN;  iptables -F SH_EP_IN
iptables -A SH_EP_IN -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A SH_EP_IN -p tcp -d "$GW" --dport "$PORT" -j ACCEPT
# the container's resolver points at the gateway, where nothing listens: answer at once instead of letting lookups
# time out, and do not count them as escape attempts (the agent did not choose them)
iptables -A SH_EP_IN -p udp -d "$GW" --dport 53 -j REJECT --reject-with icmp-port-unreachable
iptables -A SH_EP_IN -p tcp -d "$GW" --dport 53 -j REJECT --reject-with tcp-reset
iptables -A SH_EP_IN -m limit --limit 20/min -j LOG --log-prefix "sh-ep-drop-in: " --log-level 4
iptables -A SH_EP_IN -j SH_EP_DROP
chain SH_EP_FWD; iptables -F SH_EP_FWD
iptables -A SH_EP_FWD -m limit --limit 20/min -j LOG --log-prefix "sh-ep-drop-fwd: " --log-level 4
iptables -A SH_EP_FWD -j SH_EP_DROP
iptables -C INPUT -i "$NET" -j SH_EP_IN 2>/dev/null        || iptables -I INPUT 1 -i "$NET" -j SH_EP_IN
iptables -C DOCKER-USER -i "$NET" -j SH_EP_FWD 2>/dev/null || iptables -I DOCKER-USER 1 -i "$NET" -j SH_EP_FWD
# any other rule matching the interface directly (flat rules from earlier revisions) is removed
for ch in INPUT DOCKER-USER; do
  iptables -S "$ch" | grep -- "-i $NET " | grep -v -E -- "-j SH_EP_(IN|FWD)$" | sed "s/^-A $ch //" | while read -r r; do
    # shellcheck disable=SC2086
    eval iptables -D "$ch" $r
  done
done
echo "sh-ep up: $SUBNET gw $GW proxy :$PORT"
