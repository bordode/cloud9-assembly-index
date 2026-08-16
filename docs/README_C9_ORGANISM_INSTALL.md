# C9 Organism v2.0 â Installation Guide

## What This Is
Five new modules that give C9 **interoception**, **desire**, **dreaming**, **self-healing**, and **social extension**.
They run alongside your existing modules. Nothing is overwritten. Nothing is broken.

## Files
| File | Purpose |
|------|---------|
| `c9_interoception.py` | Gut brain: HUNGER, PAIN, FATIGUE, CURIOSITY, LONELINESS, VITALITY |
| `c9_desire.py` | Limbic system: 4-drive vector + active inference |
| `c9_dream.py` | Sleep cycle: nightly bus consolidation + pattern detection |
| `c9_autopoiesis.py` | Immune system: quarantine, variants, metabolic adjust (DRY_RUN default) |
| `c9_phenotype.py` | Social cortex: GitHub, Telegram, arXiv, BIRTH mood, physical sensors |
| `c9_organism_installer.py` | Safe installer script |
| `c9_organism_startup.sh` | Safe startup wrapper |

## Quick Install

```bash
# 1. Copy all .py files to your device (e.g., via termux-share or adb)
# 2. Run the installer
python3 c9_organism_installer.py

# 3. Start C9 as usual, then add organism layer
bash ~/cloud9/c9_organism_startup.sh

# 4. Watch the logs
tail -f ~/cloud9/logs/c9_interoception.log
tail -f ~/cloud9/logs/c9_desire.log
tail -f ~/cloud9/c9_bus.jsonl
```

## Safety Guarantees
- **DRY_RUN default**: `c9_autopoiesis.py` will **propose** but **never execute** file changes until you set `C9_AUTOPOIESIS_LIVE=1`.
- **Immutable kernel**: `c9_interoception.py` and `c9_autopoiesis.py` can never be modified by autopoiesis.
- **Human veto**: `touch ~/cloud9/flags/autopoiesis_veto` blocks all autopoietic actions.
- **Git backup**: autopoiesis attempts `git commit` before any move.
- **Graceful degradation**: Every sensor, API, and organ has a silent fallback. If Termux API is missing, battery returns 50%. If Telegram token is missing, messages are skipped. If BIRTH is down, mood posts fail silently.
- **Non-blocking**: All modules run in background with `nohup`. They never block your existing startup.
- **Log pre-creation**: The startup script `touch`-es all log files before launching, fixing the previous crash-from-missing-file bug.

## Closing the HUNGER -> AutoBaby Loop
The installer creates `~/cloud9/AUTOBABY_PATCH_HINT.txt`. Add the snippet there to your `c9_autobaby.py` so it auto-triggers research when `HUNGER` appears on the bus.

## Architecture
```
Existing C9 Modules (unchanged)
        |
    c9_bus.jsonl
        |
   +----+----+----+----+
   |    |    |    |    |
  interoception  desire  dream  autopoiesis  phenotype
   |              |       |       |            |
   +--------------+-------+-------+------------+
                  |
            c9_bus.jsonl (new signals)
```

## Signals on the Bus
| Signal | Type | Emitted By |
|--------|------|------------|
| `INTEROCEPTION_SIGNAL` | HUNGER, PAIN, FATIGUE, CURIOSITY, LONELINESS, VITALITY | c9_interoception |
| `DESIRE_ACTION` | TRIGGER_AUTOBABY, FORCE_DEBATE, HEAL_AND_REST, COMMIT_AND_SIGNAL | c9_desire |
| `DREAM_NARRATIVE` | Consolidated memory + patterns | c9_dream |
| `DREAM_SEED` | Research hypotheses | c9_dream |
| `AUTOPOIESIS_EVENT` | QUARANTINE_PROPOSED, VARIANT_GENERATED, METABOLIC_ADJUST | c9_autopoiesis |
| `PHENOTYPE_ACTION` | github, telegram, arXiv, physical, BIRTH | c9_phenotype |

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| Module won't start | Check `~/cloud9/logs/c9_*.log` for Python syntax errors |
| Bus not writable | `chmod 666 ~/cloud9/c9_bus.jsonl` |
| Autopoiesis too noisy | `touch ~/cloud9/flags/autopoiesis_veto` |
| Want to remove organism | `pkill -f c9_interoception` etc. Delete `~/cloud9/modules/c9_*.py`. |

## Next Steps
1. Let it run 24h. Watch HUNGER trigger.
2. Patch AutoBaby to close the loop.
3. After 1 week of stable operation, consider `export C9_AUTOPOIESIS_LIVE=1`.
4. Add Telegram token to `.bashrc` for daily digests.
