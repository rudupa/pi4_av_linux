from __future__ import annotations
import argparse
import subprocess
import signal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dev", "prod"], default="dev")
    ap.add_argument("--config", default="pc/config/default.yaml")
    args = ap.parse_args()

    cmd = ["python3", "-m", "pc.src.playback_service", "--config", args.config]
    if args.mode == "prod":
        cmd = ["bash", "-lc", "while true; do " + " ".join(cmd) + "; sleep 1; done"]

    p = subprocess.Popen(cmd)
    signal.signal(signal.SIGTERM, lambda *_: p.terminate())
    p.wait()

if __name__ == "__main__":
    main()
