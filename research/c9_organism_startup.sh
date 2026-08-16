#!/bin/bash
# C9 Organism v2.0 Safe Startup Wrapper
# This script sources your EXISTING C9 startup, then adds organism modules.
# It will NOT break your current system.

C9_HOME="$HOME/cloud9"

# ââ Source existing C9 startup if found ââ
if [ -f "$C9_HOME/c9_complete_startup.sh" ]; then
    echo "[C9-ORG] Sourcing existing c9_complete_startup.sh..."
    source "$C9_HOME/c9_complete_startup.sh"
elif [ -f "$C9_HOME/c9_full_startup.sh" ]; then
    echo "[C9-ORG] Sourcing existing c9_full_startup.sh..."
    source "$C9_HOME/c9_full_startup.sh"
elif [ -f "$C9_HOME/start_c9.sh" ]; then
    echo "[C9-ORG] Sourcing existing start_c9.sh..."
    source "$C9_HOME/start_c9.sh"
else
    echo "[C9-ORG] WARNING: No existing startup script found. Starting organism modules only."
fi

# ââ Pre-create logs (prevents crash from missing files) ââ
echo "[C9-ORG] Pre-creating log files..."
mkdir -p "$C9_HOME/logs" "$C9_HOME/pids"
for mod in c9_interoception c9_desire c9_dream c9_autopoiesis c9_phenotype; do
    touch "$C9_HOME/logs/${mod}.log"
done

# ââ Safety defaults ââ
export C9_AUTOPOIESIS_LIVE=0   # DRY_RUN by default. Set to 1 ONLY when you trust it.
export C9_BIRTH_URL=http://127.0.0.1:8086

# ââ Launch Organism Modules (background, non-blocking, staggered) ââ
echo "[C9-ORG] Launching organism modules..."
cd "$C9_HOME/modules" || exit 1

nohup python3 c9_interoception.py >> "$C9_HOME/logs/c9_interoception.log" 2>&1 &
echo $! > "$C9_HOME/pids/c9_interoception.pid"
echo "[C9-ORG] interoception PID=$!"
sleep 2

nohup python3 c9_desire.py >> "$C9_HOME/logs/c9_desire.log" 2>&1 &
echo $! > "$C9_HOME/pids/c9_desire.pid"
echo "[C9-ORG] desire PID=$!"
sleep 1

nohup python3 c9_dream.py >> "$C9_HOME/logs/c9_dream.log" 2>&1 &
echo $! > "$C9_HOME/pids/c9_dream.pid"
echo "[C9-ORG] dream PID=$!"
sleep 1

nohup python3 c9_autopoiesis.py >> "$C9_HOME/logs/c9_autopoiesis.log" 2>&1 &
echo $! > "$C9_HOME/pids/c9_autopoiesis.pid"
echo "[C9-ORG] autopoiesis PID=$!"
sleep 1

nohup python3 c9_phenotype.py >> "$C9_HOME/logs/c9_phenotype.log" 2>&1 &
echo $! > "$C9_HOME/pids/c9_phenotype.pid"
echo "[C9-ORG] phenotype PID=$!"

echo ""
echo "========================================"
echo "C9 Organism v2.0 modules launched."
echo "========================================"
echo "Logs:     tail -f ~/cloud9/logs/c9_*.log"
echo "Bus:      tail -f ~/cloud9/c9_bus.jsonl"
echo "PIDs:     ls ~/cloud9/pids/"
echo ""
echo "SAFETY: autopoiesis is in DRY_RUN mode."
echo "        It will PROPOSE changes but NEVER execute them."
echo "        To enable live mode: export C9_AUTOPOIESIS_LIVE=1"
echo "        To veto any action:  touch ~/cloud9/flags/autopoiesis_veto"
echo "========================================"
