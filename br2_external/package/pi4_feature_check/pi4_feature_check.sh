#!/bin/sh
set -u

REPORT_FILE="/var/log/pi4_feature_report.md"
BOOT_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
HOSTNAME="$(hostname 2>/dev/null || echo unknown)"

check_ok() {
    desc="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "- [x] ${desc}"
    else
        echo "- [ ] ${desc}"
    fi
}

check_cmd() {
    desc="$1"
    cmd="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "- [x] ${desc}"
    else
        echo "- [ ] ${desc}"
    fi
}

service_active() {
    svc="$1"
    systemctl is-active --quiet "$svc"
}

service_enabled() {
    svc="$1"
    systemctl is-enabled --quiet "$svc"
}

mkdir -p /var/log

{
    echo "# Pi4 Feature Verification Report"
    echo
    echo "- Generated (UTC): ${BOOT_TS}"
    echo "- Hostname: ${HOSTNAME}"
    echo

    echo "## Boot and OS"
    check_ok "systemd is PID 1" sh -c '[ "$(ps -p 1 -o comm= 2>/dev/null)" = "systemd" ]'
    check_ok "Architecture is aarch64" sh -c '[ "$(uname -m 2>/dev/null)" = "aarch64" ]'
    check_ok "Root filesystem mounted" sh -c 'mount | grep -q " on / "'
    echo

    echo "## Core systemd services"
    check_ok "systemd-networkd active" service_active systemd-networkd
    check_ok "systemd-resolved active" service_active systemd-resolved
    check_ok "systemd-timesyncd active" service_active systemd-timesyncd
    check_ok "sshd active" service_active sshd
    check_ok "sshd enabled" service_enabled sshd
    echo

    echo "## AV services"
    check_ok "av-core.target active" service_active av-core.target
    check_ok "av-core-orchestrator active" service_active av-core-orchestrator
    check_ok "av-core-gateway active" service_active av-core-gateway
    check_ok "av-core-health active" service_active av-core-health
    check_ok "av-core-logger active" service_active av-core-logger
    echo

    echo "## AV binaries and config"
    check_ok "av-core-orchestrator present" test -x /usr/local/bin/av-core-orchestrator
    check_ok "av-core-gateway present" test -x /usr/local/bin/av-core-gateway
    check_ok "av-core-health present" test -x /usr/local/bin/av-core-health
    check_ok "av-core-logger present" test -x /usr/local/bin/av-core-logger
    check_ok "av-core-ota present" test -x /usr/local/bin/av-core-ota
    check_ok "/etc/av-core exists" test -d /etc/av-core
    check_ok "/var/lib/av-core/ota exists" test -d /var/lib/av-core/ota
    check_ok "/var/log/av-core exists" test -d /var/log/av-core
    echo

    echo "## Tools"
    check_cmd "journalctl available" journalctl
    check_cmd "htop available" htop
    check_cmd "strace available" strace
    check_cmd "lshw available" lshw
    check_cmd "man available" man
    check_cmd "lscpu available" lscpu
    check_cmd "lspci available" lspci
    check_cmd "lsusb available" lsusb
    check_cmd "screen available" screen
    check_cmd "python3 available" python3
    echo

    echo "## Notes"
    echo "- Some checks may fail if dependent hardware/peripherals are absent."
    echo "- For detailed logs: journalctl -u pi4-feature-check -b"
} > "$REPORT_FILE"

chmod 0644 "$REPORT_FILE"

echo "Pi4 feature report written to $REPORT_FILE"
exit 0
