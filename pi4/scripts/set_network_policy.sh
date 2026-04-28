#!/usr/bin/env bash
set -euo pipefail
POLICY="${1:-static}"
case "$POLICY" in
  static|dhcp) ;;
  *) echo "usage: $0 [static|dhcp]"; exit 1;;
esac
echo "network_policy=$POLICY" > /etc/av-network-policy
