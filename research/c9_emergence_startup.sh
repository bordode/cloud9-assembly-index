#!/data/data/com.termux/files/usr/bin/bash
# C9 Emergence Adapter Startup
# Run: bash c9_emergence_startup.sh

echo "[C9-EMERGENCE] Booting Emergence Adapter..."

# Ensure bus exists
BUS="$HOME/c9_bus.jsonl"
touch "$BUS"

# Start the main adapter
cd "$HOME"
nohup python3 ~/c9_emergence_adapter.py >> ~/c9_emergence_adapter.log 2>&1 &
echo "[C9-EMERGENCE] Adapter PID: $!"

# Start the dashboard
sleep 2
nohup python3 ~/c9_awi_dashboard.py >> ~/c9_dashboard.log 2>&1 &
echo "[C9-EMERGENCE] Dashboard PID: $!"

echo "[C9-EMERGENCE] All systems online."
echo "  Dashboard: http://localhost:5020"
echo "  Bus: $BUS"
echo "  AWI State: ~/c9_awi_state.json"
echo "  Ledger: ~/c9_credits_ledger.json"
echo "  Constitution: ~/c9_constitution.md"
