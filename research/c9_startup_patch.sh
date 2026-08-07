#!/bin/bash
# C9 Startup Safety Patch
# Run this BEFORE c9_complete_startup_v4.sh to prevent log-file crashes
# Safe to run multiple times - idempotent

echo "[C9-PATCH] Pre-creating log files..."

LOGS=(
    "$HOME/birth_proxy.log"
    "$HOME/c9_bridge.log"
    "$HOME/c9_launcher.log"
    "$HOME/c9_omni.log"
    "$HOME/autobaby.log"
    "$HOME/kimi_bridge.log"
    "$HOME/llama_server.log"
    "$HOME/c9_quantum_module.log"
    "$HOME/c9_health.log"
)

for log in "${LOGS[@]}"; do
    touch "$log" 2>/dev/null && echo "  â $log" || echo "  â $log (permission denied)"
done

echo "[C9-PATCH] Log files ready. You can now run:"
echo "  bash ~/c9_complete_startup_v4.sh"
