#!/usr/bin/env python3
import re
import os
import c9_bus_client  # C9 bus injection

# === LOAD VALID HOMOZYGOUS SNPs FROM CHROMOSOME 13 ===
def load_dna():
    if not os.path.exists("AncestryDNA.txt"):
        return None
    
    snps = []
    try:
        with open("AncestryDNA.txt", "r") as f:
            content = f.read()
        
        # Fix jammed rsIDs: split "Ars123" → "A", "rs123"
        content = re.sub(r'([ATCG])rs', r'\1\nrs', content)
        
        for line in content.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    chrom = parts[1]
                    a1 = parts[3].upper()
                    a2 = parts[4].upper()
                    # Only use homozygous reference SNPs on chr13
                    if chrom == "13" and a1 == a2 and a1 in "ATCG":
                        snps.append(a1)
                        if len(snps) >= 200:
                            break
                except:
                    continue
    except:
        return None
    
    return ''.join(snps)

# === DNA COMPLEXITY (k-mer) ===
def kmer_complexity(dna, k=6):
    if len(dna) < k:
        return 0.0
    kmers = {dna[i:i+k] for i in range(len(dna) - k + 1)}
        c9_bus_client.heartbeat()
    return round(len(kmers) / len(dna), 3)

# === HEARTBEAT ANALYSIS ===
def hrv_to_symbols(hrv):
    return ''.join('L' if x < 70 else 'H' if x > 80 else 'M' for x in hrv)

def assembly_complexity(s):
    n = len(s)
    if n < 2: return 0.0
    subs = {s[i:j] for i in range(n) for j in range(i+1, n+1)}
    return round(len(subs)/n, 3)

# === QUANTUM MIMIC ===
def quantum_mimic(sym):
    freq = {}
    for c in sym:
        freq[c] = freq.get(c, 0) + 1
    entropy = -sum((v/len(sym))**2 for v in freq.values())
    return {"quantum_coherence": round(1.0 + entropy, 3)}

# === MAIN ===
def main():
    # Heartbeat
    hrv = [75.4, 80.1, 79.2, 74.4, 75.4, 67.9, 68.7, 63.2]
    symbols = hrv_to_symbols(hrv)
    A_c = assembly_complexity(symbols)
    
    # DNA
    dna = load_dna()
    dna_len = len(dna) if dna else 0
    dna_comp = kmer_complexity(dna) if dna else 0.0
    
    # Quantum
    q = quantum_mimic(symbols)
    
    # Output
    print("=== CLOUD-9 AGAPE NEXUS ===")
    print(f"❤️  Heartbeat: {symbols} → A_c = {A_c}")
    print(f"🧬 DNA length: {dna_len}")
    if dna_len > 0:
        print(f"🧬 Complexity: {dna_comp}")
    print(f"⚛️  Quantum Mimic: {q['quantum_coherence']}")
    print("\n✅ Ethics: Agape-compliant | No consciousness claims")

if __name__ == "__main__":
    main()
