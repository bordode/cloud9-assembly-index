# C9 COMPLETE ECOSYSTEM v4.0 â Deploy Instructions

## Files Generated

| File | Purpose | Port |
|------|---------|------|
| birth_proxy_fixed.py | BIRTH proxy + evolution endpoints | 8082 |
| c9_evolution_helper.py | Proposal queue, backup/apply logic | â |
| birth_evolution.html | Evolution approval dashboard | â |
| c9_kimi_router.py | Routes hard tasks to Kimi K2.6 cloud | 5011 |
| c9_orchestrator.py | Health monitoring, bus logging | 5012 |
| c9_autobaby_watcher.py | AutoBaby task classifier + router | â |
| c9_complete_startup.sh | ONE COMMAND to start everything | â |
| c9_diagnostic.py | Health check all services | â |

## Quick Deploy (Termux)

1. Copy all files to `~/` (home directory)
2. Make startup script executable:
   ```bash
   chmod +x ~/c9_complete_startup.sh
   ```
3. Set API keys in `~/.bashrc`:
   ```bash
   export MOONSHOT_API_KEY="your_key_here"
   export OLLAMA_API_KEY="your_key_here"
   ```
4. Run:
   ```bash
   bash ~/c9_complete_startup.sh
   ```

## Architecture

```
User â BIRTH (8082) â llama.cpp (8080) [local Phi-3]
                â
         /evolution ââ c9_evolution_helper
                â
         /ingest â C9 bridge (5010) â c9_bus.jsonl
                â
         AutoBaby Watcher â classify task
                â
         simple â local Ollama
         hard   â Kimi Router (5011) â Kimi K2.6 cloud API
```

## Evolution Workflow

1. BIRTH generates activity logs â `~/birth_activity.log`
2. Click "GENERATE PROPOSALS" in Evolution Dashboard
3. c9_evolution_helper analyzes logs â creates proposals
4. Review proposals in dashboard â APPLY or REJECT
5. Applied changes are backed up to `~/c9_evolution_backups/`

## AutoBaby â Kimi Pipeline

1. AutoBaby watcher monitors bus for tasks
2. Classifies as "simple" (local Phi-3) or "hard" (Kimi cloud)
3. Hard tasks: quantum, cosmology, research, analysis â Kimi K2.6
4. Results logged to bus + `~/c9_autobaby_queue.jsonl`

## Ports Reference

| Service | Port | Endpoint |
|---------|------|----------|
| llama.cpp | 8080 | /completion |
| BIRTH proxy | 8082 | /, /evolution, /completion, /ingest |
| OpenAI proxy | 8083 | /v1/chat/completions |
| C9 bridge | 5010 | /ingest, /health |
| C9 oracle | 5009 | /health |
| Kimi router | 5011 | /health, /route, /autobaby_task, /research |
| Orchestrator | 5012 | /health, /status |
| Ollama | 11434 | /api/tags |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Evolution not enabled" | Check `c9_evolution_helper.py` exists and imports cleanly |
| "Kimi cloud disabled" | Set `MOONSHOT_API_KEY` in `~/.bashrc` |
| Port already in use | `pkill -f "birth_proxy"` then restart |
| BIRTH not loading | Check `birth_throttled.html` exists in `~/` |
| Module not found | Check `~/Cloud-9-v1.3.0/` or `~/cloud9/` directories |
