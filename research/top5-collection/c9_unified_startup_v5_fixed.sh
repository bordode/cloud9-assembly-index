#!/data/data/com.termux/files/usr/bin/bash
# C9 Unified Startup v5.0 — Fixed 2026-08-23
# Fixes: correct paths, correct ports, python3 prefix, no interactive modules

set -e

C9_HOME="$HOME"
C9_LOGS="$HOME/cloud9/logs"
mkdir -p "$C9_LOGS"

echo "========================================"
echo "  C9 UNIFIED STARTUP v5.0"
echo "  $(date)"
echo "========================================"

# Kill stale processes
echo "[1/6] Killing stale processes..."
pkill -f ollama 2>/dev/null || true
pkill -f birth_proxy_v3 2>/dev/null || true
pkill -f c9_ai_bridge 2>/dev/null || true
pkill -f c9_oracle 2>/dev/null || true
pkill -f c9_autobaby_v2 2>/dev/null || true
sleep 1

# 2. Ollama on port 8080 (NOT 11434)
echo "[2/6] Starting Ollama on port 8080..."
OLLAMA_HOST=0.0.0.0:8080 nohup ollama serve > "$C9_LOGS/ollama.log" 2>&1 &
sleep 3
if curl -s --max-time 3 http://localhost:8080/api/tags > /dev/null 2>&1; then
    echo "      ✓ Ollama healthy (port 8080)"
else
    echo "      ✗ Ollama failed to start"
fi

# 3. BIRTH Proxy v3 on port 8086 (NOT 8082)
echo "[3/6] Starting BIRTH Proxy v3 on port 8086..."
nohup python3 "$C9_HOME/birth_proxy_v3.py" > "$C9_LOGS/birth_v3.log" 2>&1 &
sleep 2
if curl -s --max-time 3 http://localhost:8086/health > /dev/null 2>&1; then
    echo "      ✓ BIRTH v3 healthy (port 8086)"
else
    echo "      ✗ BIRTH v3 failed"
fi

# 4. C9 Bridge on port 5010 (correct path: ~/ not ~/cloud9/)
echo "[4/6] Starting C9 Bridge on port 5010..."
if [ -f "$C9_HOME/c9_ai_bridge_v2.py" ]; then
    nohup python3 "$C9_HOME/c9_ai_bridge_v2.py" > "$C9_LOGS/bridge.log" 2>&1 &
    sleep 2
    if curl -s --max-time 3 http://localhost:5010/health > /dev/null 2>&1; then
        echo "      ✓ C9 Bridge healthy (port 5010)"
    else
        echo "      ⚠ Bridge starting (check logs)"
    fi
else
    echo "      ✗ c9_ai_bridge_v2.py not found at $C9_HOME"
fi

# 5. Oracle on port 5009 (correct path: ~/ not ~/cloud9/)
echo "[5/6] Starting Oracle on port 5009..."
if [ -f "$C9_HOME/c9_oracle.py" ]; then
    nohup python3 "$C9_HOME/c9_oracle.py" > "$C9_LOGS/oracle.log" 2>&1 &
    sleep 2
    if curl -s --max-time 3 http://localhost:5009/health > /dev/null 2>&1; then
        echo "      ✓ Oracle healthy (port 5009)"
    else
        echo "      ⚠ Oracle starting (check logs)"
    fi
else
    echo "      ✗ c9_oracle.py not found at $C9_HOME"
fi

# 6. AutoBaby v2 (correct path: ~/ not ~/cloud9/)
echo "[6/6] Starting AutoBaby v2..."
if [ -f "$C9_HOME/c9_autobaby_v2.py" ]; then
    nohup python3 "$C9_HOME/c9_autobaby_v2.py" > "$C9_LOGS/autobaby_v2.log" 2>&1 &
    sleep 2
    if pgrep -f c9_autobaby_v2 > /dev/null; then
        echo "      ✓ AutoBaby v2 running"
    else
        echo "      ✗ AutoBaby failed"
    fi
else
    echo "      ✗ c9_autobaby_v2.py not found at $C9_HOME"
fi

echo ""
echo "========================================"
echo "  C9 STARTUP COMPLETE"
echo "========================================"
echo ""
echo "Port Map:"
echo "  8080  → Ollama (phi3:mini)"
echo "  8086  → BIRTH Proxy v3"
echo "  5010  → C9 Bridge"
echo "  5009  → Oracle"
echo "  —     → AutoBaby v2 (bus emitter)"
echo ""
echo "Logs: $C9_LOGS"
echo "Bus:  $C9_HOME/c9_bus.jsonl"
echo ""

# Health check
echo "Quick health check:"
for svc in "8080:Ollama" "8086:BIRTH-v3" "5010:C9-Bridge" "5009:Oracle"; do
    port=$(echo $svc | cut -d: -f1)
    name=$(echo $svc | cut -d: -f2)
    if curl -s --max-time 2 "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        echo "  ● $name (port $port) healthy"
    else
        echo "  ✗ $name (port $port) DOWN"
    fi
done
