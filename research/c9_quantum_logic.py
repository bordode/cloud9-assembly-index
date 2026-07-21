#!/usr/bin/env python3
"""
C9 Quantum Language Logic Engine
Implements non-linear, quantum-inspired thinking for the sovereign AI.

Core Primitives:
  â¢ Superposition: Multiple interpretations held simultaneously
  â¢ Entanglement: Deep connections between distant concepts
  â¢ Interference: Constructive/destructive pattern combination
  â¢ Decoherence: Collapse to classical when measurement required
  â¢ Tunneling: Bypassing local optima via probabilistic leaps
  â¢ Entropy: Measuring information content and surprise

Inspired by: Quantum Darwinism, QBism, Consistent Histories, 
             Active Inference, Integrated Information Theory
"""

import os
import json
import random
import numpy as np
from datetime import datetime
from collections import deque, defaultdict
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class QuantumThought:
    """A thought in quantum superposition â multiple states at once."""
    thought_id: str
    content: str
    amplitude: complex  # Quantum amplitude (magnitude + phase)
    domain: str
    entangled_with: List[str] = field(default_factory=list)
    collapsed: bool = False
    collapsed_value: Optional[str] = None
    timestamp: str = ""

    def probability(self) -> float:
        """Born rule: |amplitude|Â²"""
        return abs(self.amplitude) ** 2

    def phase(self) -> float:
        """Phase angle in radians."""
        return np.angle(self.amplitude)


@dataclass
class EntanglementLink:
    """A quantum entanglement between two thoughts."""
    thought_a: str
    thought_b: str
    strength: float  # 0.0 to 1.0
    link_type: str  # causal, analogical, isomorphic, emergent
    correlation: float  # -1.0 to 1.0
    created_at: str = ""


class QuantumLanguageEngine:
    """
    Non-linear thinking engine for C9 Super Intelligence.
    Enables reasoning beyond classical boolean logic.
    """

    def __init__(self, brain=None):
        self.brain = brain
        self.thought_space: Dict[str, QuantumThought] = {}
        self.entanglements: Dict[str, List[EntanglementLink]] = defaultdict(list)
        self.interference_history: deque = deque(maxlen=500)
        self.tunneling_log: deque = deque(maxlen=200)
        self.thought_counter = 0

    def _new_id(self) -> str:
        """Generate unique thought ID."""
        self.thought_counter += 1
        return f"QT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.thought_counter:04d}"

    def superpose(self, query: str, n_branches: int = 5, 
                  domains: List[str] = None) -> List[QuantumThought]:
        """
        Create a quantum superposition of n interpretations.
        Each branch is a distinct way of understanding the query.
        """
        if not self.brain:
            return self._fallback_superpose(query, n_branches)

        system = f"""You are a quantum superposition engine. Generate {n_branches} 
RADICALLY DIFFERENT interpretations of the following query. Each interpretation 
should explore a completely different epistemic framework, domain, or ontological 
assumption. Think across: physics, mathematics, biology, cognition, information 
theory, topology, thermodynamics, consciousness studies.

Return as a JSON list where each item has:
- "interpretation": the distinct reading
- "domain": which field it draws from  
- "confidence": 0.0-1.0 (how well this reading fits)
- "novelty": 0.0-1.0 (how unexpected this angle is)
- "phase": a number 0-360 (metaphorical phase angle for interference)"""

        result = self.brain.think(query, system=system, task_type="analysis",
                                   prefer_backend="nemotron", max_tokens=3000)

        try:
            content = result["content"]
            # Extract JSON
            if "```json" in content:
                branches = json.loads(content.split("```json")[1].split("```")[0])
            elif "```" in content:
                branches = json.loads(content.split("```")[1].split("```")[0])
            else:
                branches = json.loads(content)
        except:
            branches = self._fallback_superpose(query, n_branches)
            return branches

        thoughts = []
        for branch in branches[:n_branches]:
            # Convert confidence to amplitude (sqrt of probability)
            confidence = branch.get("confidence", 0.5)
            phase_deg = branch.get("phase", random.uniform(0, 360))
            phase_rad = np.radians(phase_deg)
            amplitude = complex(np.sqrt(confidence) * np.cos(phase_rad),
                             np.sqrt(confidence) * np.sin(phase_rad))

            thought = QuantumThought(
                thought_id=self._new_id(),
                content=branch.get("interpretation", ""),
                amplitude=amplitude,
                domain=branch.get("domain", "general"),
                timestamp=datetime.now().isoformat(),
            )
            self.thought_space[thought.thought_id] = thought
            thoughts.append(thought)

        # Normalize amplitudes
        total_prob = sum(t.probability() for t in thoughts)
        if total_prob > 0:
            for t in thoughts:
                t.amplitude /= np.sqrt(total_prob)

        return thoughts

    def _fallback_superpose(self, query: str, n: int) -> List[QuantumThought]:
        """Fallback superposition without AI backend."""
        domains = ["physics", "mathematics", "biology", "information_theory", 
                    "cognition", "thermodynamics"]
        thoughts = []

        for i in range(min(n, len(domains))):
            phase = random.uniform(0, 2 * np.pi)
            amp = complex(np.cos(phase), np.sin(phase)) / np.sqrt(n)

            thought = QuantumThought(
                thought_id=self._new_id(),
                content=f"[{domains[i]} interpretation of: {query[:50]}...]",
                amplitude=amp,
                domain=domains[i],
                timestamp=datetime.now().isoformat(),
            )
            self.thought_space[thought.thought_id] = thought
            thoughts.append(thought)

        return thoughts

    def entangle(self, thought_a_id: str, thought_b_id: str, 
                 link_type: str = "analogical") -> EntanglementLink:
        """
        Create a quantum entanglement between two thoughts.
        Uses AI to find the deep connection.
        """
        thought_a = self.thought_space.get(thought_a_id)
        thought_b = self.thought_space.get(thought_b_id)

        if not thought_a or not thought_b:
            return None

        if self.brain:
            prompt = f"""Find the deepest connection between these two concepts:

CONCEPT A ({thought_a.domain}): {thought_a.content[:200]}
CONCEPT B ({thought_b.domain}): {thought_b.content[:200]}

Return JSON with:
- "connection_type": causal/analogical/isomorphic/emergent
- "strength": 0.0-1.0
- "correlation": -1.0 to 1.0
- "mechanism": brief explanation"""

            result = self.brain.think(prompt, task_type="science", max_tokens=1000)
            try:
                analysis = json.loads(result["content"])
            except:
                analysis = {"connection_type": link_type, "strength": 0.5, 
                           "correlation": 0.0, "mechanism": "Default link"}
        else:
            analysis = {"connection_type": link_type, "strength": 0.5, 
                       "correlation": 0.0, "mechanism": "Fallback link"}

        link = EntanglementLink(
            thought_a=thought_a_id,
            thought_b=thought_b_id,
            strength=analysis.get("strength", 0.5),
            link_type=analysis.get("connection_type", link_type),
            correlation=analysis.get("correlation", 0.0),
            created_at=datetime.now().isoformat(),
        )

        self.entanglements[thought_a_id].append(link)
        self.entanglements[thought_b_id].append(link)

        thought_a.entangled_with.append(thought_b_id)
        thought_b.entangled_with.append(thought_a_id)

        return link

    def interfere(self, thought_ids: List[str]) -> Dict[str, Any]:
        """
        Create quantum interference between multiple thoughts.
        Constructive interference amplifies agreement.
        Destructive interference reveals contradictions.
        """
        thoughts = [self.thought_space.get(tid) for tid in thought_ids]
        thoughts = [t for t in thoughts if t is not None]

        if len(thoughts) < 2:
            return {"error": "Need at least 2 thoughts for interference"}

        # Compute pairwise interference
        constructive = []
        destructive = []

        for i, t1 in enumerate(thoughts):
            for t2 in thoughts[i+1:]:
                # Phase difference determines interference type
                phase_diff = t1.phase() - t2.phase()

                # In-phase â constructive, anti-phase â destructive
                alignment = np.cos(phase_diff)

                if alignment > 0.3:
                    constructive.append({
                        "thoughts": (t1.thought_id, t2.thought_id),
                        "alignment": alignment,
                        "domains": (t1.domain, t2.domain),
                        "synthesis": f"{t1.domain} and {t2.domain} reinforce",
                    })
                elif alignment < -0.3:
                    destructive.append({
                        "thoughts": (t1.thought_id, t2.thought_id),
                        "alignment": alignment,
                        "domains": (t1.domain, t2.domain),
                        "tension": f"{t1.domain} contradicts {t2.domain}",
                    })

        # Compute emergent synthesis
        if self.brain and constructive:
            synthesis_prompt = "Synthesize these aligned perspectives:\n"
            for c in constructive[:3]:
                t1 = self.thought_space[c["thoughts"][0]]
                t2 = self.thought_space[c["thoughts"][1]]
                synthesis_prompt += f"\n- {t1.domain}: {t1.content[:100]}"
                synthesis_prompt += f"\n- {t2.domain}: {t2.content[:100]}"

            result = self.brain.think(synthesis_prompt, task_type="analysis", max_tokens=1500)
            emergent = result["content"]
        else:
            emergent = "Interference pattern detected but no AI backend for synthesis."

        interference_result = {
            "constructive": constructive,
            "destructive": destructive,
            "emergent_synthesis": emergent,
            "participants": len(thoughts),
            "timestamp": datetime.now().isoformat(),
        }

        self.interference_history.append(interference_result)
        return interference_result

    def collapse(self, superposition_id: str = None, 
                 measurement_basis: str = "highest_probability",
                 custom_criterion: str = None) -> QuantumThought:
        """
        Collapse a quantum superposition to a classical answer.
        Measurement basis determines which property is observed.
        """
        # If no specific superposition, collapse all uncollapsed thoughts
        candidates = [t for t in self.thought_space.values() if not t.collapsed]

        if not candidates:
            return None

        if measurement_basis == "highest_probability":
            # Born rule measurement
            winner = max(candidates, key=lambda t: t.probability())
        elif measurement_basis == "highest_novelty":
            # Requires AI evaluation
            if self.brain:
                winner = self._ai_select_novel(candidates)
            else:
                winner = random.choice(candidates)
        elif measurement_basis == "custom" and custom_criterion:
            # AI-evaluated custom criterion
            if self.brain:
                winner = self._ai_select_custom(candidates, custom_criterion)
            else:
                winner = random.choice(candidates)
        else:
            # Probabilistic collapse
            probs = [t.probability() for t in candidates]
            winner = random.choices(candidates, weights=probs)[0]

        winner.collapsed = True
        winner.collapsed_value = winner.content

        # Entangled thoughts also partially collapse (spooky action)
        for entangled_id in winner.entangled_with:
            entangled = self.thought_space.get(entangled_id)
            if entangled and not entangled.collapsed:
                # Partial collapse: update amplitude
                links = [l for l in self.entanglements[entangled_id] 
                        if l.thought_a == winner.thought_id or l.thought_b == winner.thought_id]
                if links:
                    avg_correlation = np.mean([l.correlation for l in links])
                    # Correlated thoughts move toward same state
                    entangled.amplitude *= (0.5 + 0.5 * avg_correlation)

        return winner

    def _ai_select_novel(self, candidates: List[QuantumThought]) -> QuantumThought:
        """Use AI to select the most novel thought."""
        prompt = "Rate the novelty of these interpretations (0-1):\n"
        for i, t in enumerate(candidates):
            prompt += f"\n{i+1}. [{t.domain}] {t.content[:150]}"
        prompt += "\n\nReturn the index number of the MOST NOVEL interpretation."

        result = self.brain.think(prompt, task_type="analysis", max_tokens=100)
        try:
            idx = int(result["content"].strip().split()[0]) - 1
            return candidates[max(0, min(idx, len(candidates)-1))]
        except:
            return max(candidates, key=lambda t: t.probability())

    def _ai_select_custom(self, candidates: List[QuantumThought], criterion: str) -> QuantumThought:
        """Use AI to select based on custom criterion."""
        prompt = f"Select the best interpretation based on this criterion: {criterion}\n"
        for i, t in enumerate(candidates):
            prompt += f"\n{i+1}. [{t.domain}] {t.content[:150]}"
        prompt += "\n\nReturn the index number of the best match."

        result = self.brain.think(prompt, task_type="analysis", max_tokens=100)
        try:
            idx = int(result["content"].strip().split()[0]) - 1
            return candidates[max(0, min(idx, len(candidates)-1))]
        except:
            return max(candidates, key=lambda t: t.probability())

    def tunnel(self, from_state: str, to_domain: str, 
               barrier_height: float = 0.5) -> QuantumThought:
        """
        Quantum tunneling: bypass local optima via probabilistic leaps.
        Jump from one conceptual domain to another, even if classical 
        reasoning would see them as separated by a high barrier.
        """
        if not self.brain:
            return self._fallback_tunnel(from_state, to_domain)

        prompt = f"""Perform a QUANTUM TUNNELING leap:

CURRENT STATE: {from_state}
TARGET DOMAIN: {to_domain}
BARRIER: Classical reasoning says these are unrelated

Find the NON-OBVIOUS path. Use analogy, isomorphism, or deep structure 
matching. Think like a creative physicist making an interdisciplinary leap.

Return JSON:
- "tunnel_path": the conceptual bridge
- "probability": 0.0-1.0 (how likely this tunneling is)
- "insight": the key realization that enables the leap
- "testable_implication": a prediction this leap generates"""

        result = self.brain.think(prompt, task_type="science", prefer_backend="nemotron", max_tokens=2000)

        try:
            tunnel_data = json.loads(result["content"])
        except:
            tunnel_data = {
                "tunnel_path": f"From {from_state} to {to_domain}",
                "probability": 0.3,
                "insight": result["content"][:300],
                "testable_implication": "Requires further analysis"
            }

        # Create tunneled thought
        prob = tunnel_data.get("probability", 0.3)
        phase = random.uniform(0, 2 * np.pi)
        amplitude = complex(np.sqrt(prob) * np.cos(phase), 
                           np.sqrt(prob) * np.sin(phase))

        thought = QuantumThought(
            thought_id=self._new_id(),
            content=tunnel_data.get("insight", ""),
            amplitude=amplitude,
            domain=to_domain,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_space[thought.thought_id] = thought

        self.tunneling_log.append({
            "from": from_state,
            "to_domain": to_domain,
            "thought_id": thought.thought_id,
            "probability": prob,
            "timestamp": datetime.now().isoformat(),
        })

        return thought

    def _fallback_tunnel(self, from_state: str, to_domain: str) -> QuantumThought:
        """Fallback tunneling without AI."""
        thought = QuantumThought(
            thought_id=self._new_id(),
            content=f"[Tunnel from {from_state[:30]}... to {to_domain}]",
            amplitude=complex(0.3, 0),
            domain=to_domain,
            timestamp=datetime.now().isoformat(),
        )
        self.thought_space[thought.thought_id] = thought
        return thought

    def compute_entropy(self, thought_subset: List[str] = None) -> float:
        """
        Compute von Neumann entropy of the thought space.
        Higher entropy = more uncertainty/diversity.
        Lower entropy = more collapsed/certain.
        """
        if thought_subset:
            thoughts = [self.thought_space.get(tid) for tid in thought_subset]
            thoughts = [t for t in thoughts if t is not None]
        else:
            thoughts = list(self.thought_space.values())

        if not thoughts:
            return 0.0

        probs = [t.probability() for t in thoughts]
        total = sum(probs)
        if total == 0:
            return 0.0

        probs = [p / total for p in probs]

        # Shannon entropy
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        return entropy

    def get_thought_space_summary(self) -> str:
        """Summary of the quantum thought space."""
        total = len(self.thought_space)
        collapsed = sum(1 for t in self.thought_space.values() if t.collapsed)
        entangled = sum(1 for t in self.thought_space.values() if t.entangled_with)

        domains = defaultdict(int)
        for t in self.thought_space.values():
            domains[t.domain] += 1

        entropy = self.compute_entropy()

        summary = f"""ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
â  QUANTUM THOUGHT SPACE                                       â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

ð Statistics:
   Total thoughts: {total}
   Collapsed: {collapsed} | Superposed: {total - collapsed}
   Entangled: {entangled}
   Entropy: {entropy:.3f} bits
   Interference events: {len(self.interference_history)}
   Tunneling events: {len(self.tunneling_log)}

ð Domain Distribution:
"""
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            bar = "â" * int(count / max(domains.values()) * 20)
            summary += f"   {domain:20s} {bar} {count}\n"

        return summary


# âââ Integration with C9 Super Intelligence âââââââââââââââââââââââââââââââââ

class QuantumC9Bridge:
    """Bridge between Quantum Language Engine and C9 Assembly Index."""

    def __init__(self, quantum_engine: QuantumLanguageEngine, c9_processor):
        self.quantum = quantum_engine
        self.c9 = c9_processor

    def quantum_analyze_entry(self, entry_id: str) -> Dict:
        """Apply quantum thinking to a C9 Assembly Index entry."""
        entry = self.c9.entries.get(entry_id)
        if not entry:
            return {"error": "Entry not found"}

        # Superpose: multiple interpretations of the entry
        thoughts = self.quantum.superpose(entry.content, n_branches=3)

        # Entangle with related clusters
        for cluster_id in entry.clusters:
            cluster_name = self.c9.CLUSTERS.get(cluster_id, f"Cluster {cluster_id}")
            for thought in thoughts:
                self.quantum.entangle(
                    thought.thought_id, 
                    thought.thought_id,  # Self-entanglement with cluster concept
                    link_type="cluster_affinity"
                )

        # Interference analysis
        interference = self.quantum.interfere([t.thought_id for t in thoughts])

        # Collapse to best interpretation
        winner = self.quantum.collapse(measurement_basis="highest_probability")

        return {
            "entry_id": entry_id,
            "thoughts_generated": len(thoughts),
            "interference": interference,
            "collapsed_interpretation": winner.content if winner else None,
            "quantum_entropy": self.quantum.compute_entropy([t.thought_id for t in thoughts]),
        }


if __name__ == "__main__":
    # Demo
    qe = QuantumLanguageEngine()

    print("ð C9 Quantum Language Logic Engine Demo\n")

    # Superposition
    print("1ï¸â£  Creating superposition...")
    thoughts = qe.superpose("What is consciousness?", n_branches=4)
    for t in thoughts:
        print(f"   [{t.domain}] P={t.probability():.3f} | {t.content[:80]}...")

    # Entanglement
    print("\n2ï¸â£  Creating entanglements...")
    if len(thoughts) >= 2:
        link = qe.entangle(thoughts[0].thought_id, thoughts[1].thought_id)
        print(f"   Linked: strength={link.strength:.2f}, type={link.link_type}")

    # Interference
    print("\n3ï¸â£  Computing interference...")
    result = qe.interfere([t.thought_id for t in thoughts])
    print(f"   Constructive: {len(result['constructive'])}")
    print(f"   Destructive: {len(result['destructive'])}")

    # Collapse
    print("\n4ï¸â£  Collapsing superposition...")
    winner = qe.collapse()
    print(f"   Winner: [{winner.domain}] {winner.content[:100]}...")

    # Tunneling
    print("\n5ï¸â£  Quantum tunneling...")
    tunneled = qe.tunnel("consciousness", "thermodynamics")
    print(f"   Tunneled to: {tunneled.domain} | {tunneled.content[:80]}...")

    print("\n" + qe.get_thought_space_summary())
