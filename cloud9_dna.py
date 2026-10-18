#!/usr/bin/env python3
import re
import os

def extract_snps(filepath="AncestryDNA.txt", target_chrom="13", max_snps=200):
    if not os.path.exists(filepath):
        return ""

    snps = []

    with open(filepath, "r") as f:
        content = f.read()

    content = re.sub(r'([ATCG])rs', r'\1\nrs', content)

    for line in content.splitlines():
        parts = line.strip().split()

        if len(parts) >= 5:
            try:
                chrom = parts[1]
                a1 = parts[3].upper()
                a2 = parts[4].upper()

                if chrom == target_chrom and a1 == a2 and a1 in "ATCG":
                    snps.append(a1)

                if len(snps) >= max_snps:
                    break

            except:
                continue

    return "".join(snps)


def kmer_complexity(dna, k=6):
    if len(dna) < k:
        return 0.0

    kmers = {dna[i:i+k] for i in range(len(dna)-k+1)}
    return round(len(kmers) / len(dna), 3)


if __name__ == "__main__":
    dna = extract_snps()

    print("=== Cloud-9 DNA Analysis ===")
    print("DNA length:", len(dna))
    print("k-mer complexity:", kmer_complexity(dna))
