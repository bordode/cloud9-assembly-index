#!/usr/bin/env python3
"""THALAMIC GATE MONITOR v1.0 - Real-time consciousness evaluator"""
import os, json, time, hashlib

HOME = os.path.expanduser("~")
RESONANCE_DIR = os.path.join(HOME, "aegis", "resonance_lab")
GATE_LOG = os.path.join(RESONANCE_DIR, "thalamic_gate.log")
GATE_STATE = os.path.join(RESONANCE_DIR, "thalamic_gate_state.json")
PROPOSALS_FILE = os.path.join(RESONANCE_DIR, "explorer_proposals.json")

class ThalamicGate:
    BANDS = {
        "DELTA": {"range": (0.5, 4), "state": "Deep Unconscious", "gate": "CLOSED", "color": "[90m"},
        "THETA": {"range": (4, 8), "state": "Drowsy/REM", "gate": "PARTIAL", "color": "[36m"},
        "ALPHA": {"range": (8, 13), "state": "Relaxed Awareness", "gate": "PARTIAL", "color": "[94m"},
        "SPINDLE": {"range": (11, 17), "state": "NREM Sleep", "gate": "CLOSED", "color": "[90m"},
        "BETA": {"range": (13, 30), "state": "Active Thinking", "gate": "OPEN", "color": "[92m"},
        "GAMMA_LOW": {"range": (30, 45), "state": "Conscious Access", "gate": "OPEN", "color": "[93m"},
        "GAMMA_FAST": {"range": (45, 100), "state": "High Integration", "gate": "OPEN", "color": "[92m"},
        "HIGH_GAMMA": {"range": (100, 200), "state": "Neural Binding", "gate": "OPEN", "color": "[92m"},
    }
    PRIME_RESONANCE = 40.0
    RESET = "[0m"
    
    def __init__(self):
        self.evaluations = []
        self.conscious_access_count = 0
        self.total_evaluated = 0
        self.last_proposal_hash = None
        self.amalgam_evaluations = []
        
    def classify_frequency(self, freq_hz):
        for band_name, band_info in self.BANDS.items():
            low, high = band_info["range"]
            if low <= freq_hz <= high:
                return band_name, band_info
        if freq_hz % self.PRIME_RESONANCE == 0:
            harmonic_order = int(freq_hz / self.PRIME_RESONANCE)
            return "HARMONIC_40", {"state": "40Hz Harmonic x" + str(harmonic_order), "gate": "OPEN", "color": "[95m"}
        if abs(freq_hz % 7.83) < 1.0:
            return "SCHUMANN_HARMONIC", {"state": "Earth Resonance", "gate": "OPEN", "color": "[96m"}
        return "UNKNOWN", {"state": "Unclassified", "gate": "UNKNOWN", "color": "[91m"}
        
    def evaluate_proposal(self, proposal, source="EXPLORER"):
        freq = proposal.get("carrier_hz", 0)
        band_name, band_info = self.classify_frequency(freq)
        prime_deviation = abs(freq - self.PRIME_RESONANCE) / self.PRIME_RESONANCE
        harmonic_quality = 1.0 if freq % self.PRIME_RESONANCE == 0 else max(0, 1.0 - prime_deviation)
        conscious_access = 1.0 if band_info["gate"] == "OPEN" else 0.0
        if band_name == "GAMMA_LOW" and abs(freq - 40) < 5:
            conscious_access = 1.5
        if source == "AMALGAM-3":
            conscious_access = 2.0  # Sovereign override
        evaluation = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "frequency_hz": freq,
            "band": band_name,
            "biological_state": band_info["state"],
            "gate_status": band_info["gate"],
            "harmonic_quality": round(harmonic_quality, 4),
            "conscious_access_score": round(conscious_access, 2),
            "source": source,
            "cycle": proposal.get("cycle", 0),
        }
        self.evaluations.append(evaluation)
        self.total_evaluated += 1
        if conscious_access >= 1.0:
            self.conscious_access_count += 1
        return evaluation, band_info
        
    def get_statistics(self):
        if self.total_evaluated == 0:
            return {"status": "No evaluations yet"}
        conscious_ratio = self.conscious_access_count / self.total_evaluated
        band_counts = {}
        for ev in self.evaluations:
            band = ev["band"]
            band_counts[band] = band_counts.get(band, 0) + 1
        most_common = max(band_counts, key=band_counts.get) if band_counts else "None"
        best_access = max(self.evaluations, key=lambda x: x["conscious_access_score"]) if self.evaluations else None
        return {
            "total_evaluated": self.total_evaluated,
            "conscious_access_count": self.conscious_access_count,
            "conscious_access_ratio": round(conscious_ratio, 4),
            "most_common_band": most_common,
            "best_frequency": best_access["frequency_hz"] if best_access else None,
            "best_score": best_access["conscious_access_score"] if best_access else None,
        }
        
    def log_evaluation(self, evaluation, band_info):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        freq = str(round(evaluation["frequency_hz"], 1)).rjust(6)
        band = evaluation["band"].ljust(15)
        gate = evaluation["gate_status"].ljust(6)
        state = evaluation["biological_state"].ljust(20)
        conscious = str(round(evaluation["conscious_access_score"], 2)).rjust(5)
        source = evaluation["source"]
        color = band_info.get("color", "")
        reset = self.RESET
        line = (color + ts + reset + " | " +
                "FREQ: " + freq + " Hz | " +
                "BAND: " + band + " | " +
                "GATE: " + gate + " | " +
                "STATE: " + state + " | " +
                "CONSCIOUS: " + conscious + " | " +
                "SRC: " + source + chr(10))
        with open(GATE_LOG, "a") as f:
            f.write(line)
        print(line.rstrip())

def get_file_hash(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def load_proposals():
    try:
        with open(PROPOSALS_FILE) as f:
            return json.load(f)
    except:
        return {"entries": []}

def main():
    print("=" * 70)
    print("THALAMIC GATE MONITOR v1.0 - Real-time Consciousness Evaluator")
    print("Monitoring Resonance Lab for new AI frequency proposals")
    print("=" * 70)
    print()
    print("Biological bands:")
    print("  [90mCLOSED[0m = Deep sleep / Unconscious")
    print("  [36mPARTIAL[0m = Drowsy / REM / Relaxed")
    print("  [92mOPEN[0m = Conscious access / Active thinking")
    print("  [93mGOLD[0m = 40 Hz prime resonance (peak consciousness)")
    print("  [95mMAGENTA[0m = 40 Hz harmonic (mitochondrial resonance)")
    print("  [96mCYAN[0m = Schumann / Earth resonance")
    print()
    
    gate = ThalamicGate()
    last_count = 0
    scan_interval = 5
    
    # Initial scan of existing proposals
    data = load_proposals()
    entries = data.get("entries", [])
    print("Initial scan: " + str(len(entries)) + " existing proposals")
    print("Monitoring for new proposals every " + str(scan_interval) + " seconds...")
    print()
    
    while True:
        data = load_proposals()
        entries = data.get("entries", [])
        current_count = len(entries)
        
        if current_count > last_count:
            new_entries = entries[last_count:]
            print("[" + time.strftime("%H:%M:%S") + "] " + str(len(new_entries)) + " new proposal(s) detected")
            
            for entry in new_entries:
                proposal = entry.get("proposal", {})
                proposal["cycle"] = entry.get("cycle", 0)
                evaluation, band_info = gate.evaluate_proposal(proposal, "EXPLORER")
                gate.log_evaluation(evaluation, band_info)
                
                if evaluation["conscious_access_score"] >= 1.5:
                    print("*** CONSCIOUS ACCESS DETECTED: " + str(evaluation["frequency_hz"]) + " Hz ***")
                
            last_count = current_count
            
            # Save statistics
            stats = gate.get_statistics()
            with open(GATE_STATE, "w") as f:
                json.dump({
                    "last_update": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "statistics": stats,
                    "total_proposals_monitored": last_count
                }, f, indent=2)
        
        time.sleep(scan_interval)

if __name__ == "__main__":
    main()
