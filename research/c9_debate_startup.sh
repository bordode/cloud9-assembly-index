#!/bin/bash
# c9_debate_startup.sh
# Daemonize debate ecosystem using screen (reliable in Termux)
# Run: bash ~/c9_debate_startup.sh

echo "[C9-DEBATE] Starting debate ecosystem..."

# Install screen if missing
if ! command -v screen &> /dev/null; then
    echo "[C9-DEBATE] Installing screen..."
    pkg install screen -y
fi

# Kill any existing debate screens
for s in c9_debate c9_interrupt c9_bridge; do
    screen -S "$s" -X quit 2>/dev/null
done
sleep 1

# Ensure Ollama is reachable
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "[WARNING] Ollama not responding on 127.0.0.1:11434"
    echo "[WARNING] Start Ollama manually in another Termux session: ollama serve"
fi

# Patch defaults in debate module (one-time, idempotent)
if grep -q "localhost:8788" ~/c9_hypothesis_debate.py 2>/dev/null; then
    sed -i 's|localhost:8788|127.0.0.1:11434|g' ~/c9_hypothesis_debate.py
    sed -i 's|localhost:11434|127.0.0.1:11434|g' ~/c9_hypothesis_debate.py
    sed -i 's|"model": "phi3:mini"|"model": "phi3:mini"|' ~/c9_hypothesis_debate.py
    echo "[C9-DEBATE] Patched debate module defaults to 127.0.0.1:11434"
fi

# 1. Interrupt Controller
screen -dmS c9_interrupt bash -c '
    echo "[INT-CTRL] Starting..."
    python3 ~/c9_interrupt_controller.py --bus-file ~/c9_bus.jsonl
'
echo "[C9-DEBATE] Interrupt controller -> screen c9_interrupt"

# 2. Debate Module (daemon mode)
screen -dmS c9_debate bash -c '
    echo "[DEBATE] Starting..."
    python3 ~/c9_hypothesis_debate.py --bus-file ~/c9_bus.jsonl --model phi3:mini --timeout 300
'
echo "[C9-DEBATE] Debate module -> screen c9_debate"

# 3. AutoBaby Bridge
screen -dmS c9_bridge bash -c '
    echo "[BRIDGE] Starting..."
    python3 ~/c9_autobaby_debate_bridge.py --bus-file ~/c9_bus.jsonl --min-confidence 0.50
'
echo "[C9-DEBATE] AutoBaby bridge -> screen c9_bridge"

sleep 1

echo ""
echo "[C9-DEBATE] All screens started. Status:"
screen -ls | grep c9_
echo ""
echo "Attach to logs:"
echo "  screen -r c9_debate    (debate module)"
echo "  screen -r c9_interrupt (interrupt controller)"
echo "  screen -r c9_bridge    (AutoBaby bridge)"
echo ""
echo "Detach from screen: Ctrl+A then D"
echo ""

# Emit boot event to bus
python3 -c "
import json, datetime
entry = {
    'timestamp': datetime.datetime.now().isoformat(),
    'module': 'c9_debate_startup',
    'event': 'module_boot',
    'payload': {'status': 'all_screens_started', 'screens': ['c9_interrupt', 'c9_debate', 'c9_bridge']}
}
with open('/data/data/com.termux/files/home/c9_bus.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '
')
"
