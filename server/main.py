#!/usr/bin/env python3
"""
GemStone IV supervisor entry point.

Starts the world authority under one visible server app/window while leaving
room for child services under the same root.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("GEMSTONE_ROOT", PROJECT_ROOT)


def main():
    print(r"""
   ____                ____  _                     _______     __
  / ___| ___ _ __ ___ / ___|| |_ ___  _ __   ___  |_ _\ \   / /
 | |  _ / _ \ '_ ` _ \\___ \| __/ _ \| '_ \ / _ \  | | \ \ / /
 | |_| |  __/ | | | | |___) | || (_) | | | |  __/  | |  \ V /
  \____|\___|_| |_| |_|____/ \__\___/|_| |_|\___| |___|  \_/

                Supervisor + World Authority
    """)
    env = os.environ.copy()
    env.setdefault("GEMSTONE_ROOT", PROJECT_ROOT)
    env["GEMSTONE_ROLE"] = "world"
    world_main = os.path.join(PROJECT_ROOT, "server", "world_main.py")
    proc = subprocess.Popen([sys.executable, world_main], cwd=PROJECT_ROOT, env=env)

    def _forward_signal(signum, frame):
        try:
            proc.send_signal(signum)
        except Exception:
            pass

    signal.signal(signal.SIGINT, _forward_signal)
    signal.signal(signal.SIGTERM, _forward_signal)

    try:
        return proc.wait()
    except KeyboardInterrupt:
        _forward_signal(signal.SIGINT, None)
        return proc.wait()


if __name__ == "__main__":
    sys.exit(main())
