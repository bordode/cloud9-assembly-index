#!/usr/bin/env python3
"""
c9_interrupt_controller.py
Distributed Interrupt Layer for Cloud-9 Ecosystem v1.0

Purpose:
  Any module can emit a bus command like:
    {"target_module": "c9_hypothesis_debate", "action": "interrupt", "level": 1}

  This controller reads the command and delivers the appropriate Unix signal
to the target process. This decouples "who decides to stop" from "who actually stops."

Signal Mapping:
  level 1 (PAUSE)  â SIGINT  â target finishes current turn, checkpoints, pauses
  level 2 (ABORT)  â SIGTERM â target checkpoints immediately and exits
  level 3 (KILL)   â SIGKILL â immediate termination (no checkpoint)

Integration:
  - Run alongside c9_unified_launcher.py
  - Reads same c9_bus.jsonl
  - Requires target modules to register their PID on boot
"""

import os
import sys
import json
import time
import signal
import argparse
from datetime import datetime

DEFAULT_BUS = os.path.expanduser("~/c9_bus.jsonl")
DEFAULT_MODULE = "c9_interrupt_controller"

class InterruptController:
    def __init__(self, bus_file: str):
        self.bus_file = bus_file
        self._last_size = 0
        self.pid_registry = {}  # module_name -> pid

    def emit(self, event_type: str, payload: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": DEFAULT_MODULE,
            "event": event_type,
            "payload": payload,
        }
        with open(self.bus_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def read_new(self):
        if not os.path.exists(self.bus_file):
            return []
        current_size = os.path.getsize(self.bus_file)
        if current_size <= self._last_size:
            return []
        entries = []
        with open(self.bus_file, "r") as f:
            f.seek(self._last_size)
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        self._last_size = current_size
        return entries

    def _update_registry(self, entry: dict):
        """Auto-learn PIDs from module_boot events."""
        event = entry.get("event", "")
        payload = entry.get("payload", {})
        module = entry.get("module", "")
        if event == "module_boot" and module and module != DEFAULT_MODULE:
            pid = payload.get("pid")
            if pid:
                self.pid_registry[module] = pid
                print(f"[REGISTRY] {module} â PID {pid}")

    def _handle_interrupt_command(self, entry: dict):
        payload = entry.get("payload", {})
        if payload.get("action") not in ("interrupt", "pause", "abort", "kill"):
            return

        target = payload.get("target_module", "")
        level = payload.get("level", 1)

        # Resolve PID
        pid = self.pid_registry.get(target)
        if not pid:
            # Try to find from recent bus entries
            pid = payload.get("target_pid")

        if not pid:
            self.emit("interrupt_error", {"error": f"Unknown PID for {target}"})
            return

        # Map action to signal
        sig_map = {
            "pause": (signal.SIGINT, "SIGINT"),
            "interrupt": (signal.SIGINT, "SIGINT"),
            "abort": (signal.SIGTERM, "SIGTERM"),
            "kill": (signal.SIGKILL, "SIGKILL"),
        }
        sig, sig_name = sig_map.get(payload["action"], (signal.SIGINT, "SIGINT"))

        try:
            os.kill(pid, sig)
            self.emit("interrupt_delivered", {
                "target_module": target,
                "target_pid": pid,
                "signal": sig_name,
                "level": level,
                "source": entry.get("module", "unknown"),
            })
            print(f"[INTERRUPT] Sent {sig_name} to {target} (PID {pid})")
        except ProcessLookupError:
            self.emit("interrupt_error", {"error": f"PID {pid} not found for {target}"})
            del self.pid_registry[target]
        except PermissionError:
            self.emit("interrupt_error", {"error": f"Permission denied for PID {pid}"})

    def run(self):
        print(f"[INT-CTRL] Online. Polling {self.bus_file}...")
        self.emit("module_boot", {"status": "ready", "pid": os.getpid()})

        while True:
            entries = self.read_new()
            for entry in entries:
                self._update_registry(entry)
                self._handle_interrupt_command(entry)
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus-file", default=DEFAULT_BUS)
    args = parser.parse_args()
    ctrl = InterruptController(args.bus_file)
    ctrl.run()

if __name__ == "__main__":
    main()
