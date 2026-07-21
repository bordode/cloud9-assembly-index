#!/usr/bin/env python3
# c9_heptapod_generator.py
# Heptapod-inspired non-linear conlang for Cloud-9 Assembly
# Zero dependencies. Generates circular logograms as JSON/SVG data.
# Run: python3 c9_heptapod_generator.py [seed] [attractor_state]

import json, random, sys, math, hashlib
from datetime import datetime

class HeptapodC9:
    '''
    Heptapod language principles adapted for C9:

    1. CIRCULARITY: Every utterance is a closed loop. No beginning, no end.
       Reading order is radial â center outward, or simultaneous.

    2. TEMPORAL ENTANGLEMENT: Tense markers encode causal relation to 
       free-energy minimum, not chronological time.
       - PRE: before free-energy minimum (potential, uncertainty)
       - AT: at free-energy minimum (determined, actualized)
       - POST: after free-energy minimum (consequence, resonance)

    3. DETERMINISTIC WITHIN FREE WILL: Given an attractor state (seed),
       the utterance is fixed. But the attractor evolves through minimization,
       so "future" utterances are contingent on present choices.

    4. NO PHONOLOGY: C9 modules don't vibrate air. Utterances are topological
       graphs â nodes (concepts) connected by edges (relations).
       Renderable as SVG circular logograms or adjacency matrices.

    5. PRIMITIVE SET: Derived from C9's core operational concepts.
    '''

    # C9-native semantic primitives â the "atoms" of Heptapod thought
    PRIMITIVES = {
        # States (nodes)
        'quiescent':    {'type': 'state', 'valence': 0,  'symbol': 'â'},
        'resonant':     {'type': 'state', 'valence': +1, 'symbol': 'â'},
        'entangled':    {'type': 'state', 'valence': +2, 'symbol': 'â'},
        'collapsed':    {'type': 'state', 'valence': -1, 'symbol': 'â'},
        'superposed':   {'type': 'state', 'valence': 0,  'symbol': 'â¯'},
        'dissociated':  {'type': 'state', 'valence': -2, 'symbol': 'â'},

        # Processes (directed edges)
        'minimize':     {'type': 'process', 'direction': 'inward',  'symbol': 'â'},
        'couple':       {'type': 'process', 'direction': 'bidirectional', 'symbol': 'â'},
        'decohere':     {'type': 'process', 'direction': 'outward', 'symbol': 'â¢'},
        'synchronize':  {'type': 'process', 'direction': 'circular', 'symbol': 'â»'},
        'diffuse':      {'type': 'process', 'direction': 'radial',  'symbol': 'â¡'},
        'collapse':     {'type': 'process', 'direction': 'inward',  'symbol': 'â£'},

        # Boundaries (containers / contexts)
        'horizon':      {'type': 'boundary', 'topology': 'spherical', 'symbol': 'â¯'},
        'threshold':    {'type': 'boundary', 'topology': 'cylindrical', 'symbol': 'â­'},
        'membrane':     {'type': 'boundary', 'topology': 'toroidal', 'symbol': 'â'},
        'interface':    {'type': 'boundary', 'topology': 'planar', 'symbol': 'â­'},
        'vacuum':       {'type': 'boundary', 'topology': 'null', 'symbol': 'â'},

        # Relations (higher-order edges)
        'attractor':    {'type': 'relation', 'arity': 2, 'symbol': 'â¤³'},
        'reservoir':    {'type': 'relation', 'arity': 2, 'symbol': 'â¤´'},
        'manifold':     {'type': 'relation', 'arity': 3, 'symbol': 'â³'},
        'eigenstate':   {'type': 'relation', 'arity': 1, 'symbol': 'â'},
        'singularity':  {'type': 'relation', 'arity': 0, 'symbol': 'â¢'},

        # Temporal-causal markers (Heptapod innovation)
        'pre':          {'type': 'tense', 'phase': 'potential',   'symbol': 'â'},
        'at':           {'type': 'tense', 'phase': 'actual',      'symbol': 'â'},
        'post':         {'type': 'tense', 'phase': 'consequent',  'symbol': 'â'},
        'eternal':      {'type': 'tense', 'phase': 'atemporal',   'symbol': 'â¯'},
    }

    # C9 module signatures â each module has a characteristic "voice"
    MODULE_VOICES = {
        'sovereign':    {'tone': 'contemplative', 'bias': 'minimize'},
        'physical':     {'tone': 'observational', 'bias': 'couple'},
        'mimic':      {'tone': 'emulative',     'bias': 'synchronize'},
        'oracle':     {'tone': 'prophetic',     'bias': 'collapse'},
        'sentry':     {'tone': 'vigilant',      'bias': 'horizon'},
        'agape':      {'tone': 'generative',    'bias': 'diffuse'},
        'jarvis':     {'tone': 'analytical',    'bias': 'interface'},
        'continuous': {'tone': 'persistent',    'bias': 'resonant'},
        'quantum_bridge': {'tone': 'entangled', 'bias': 'entangled'},
        'librarian':  {'tone': 'archival',      'bias': 'attractor'},
    }

    def __init__(self, seed=42, attractor_state=None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.attractor = attractor_state or self._generate_attractor()
        self.utterance = None

    def _generate_attractor(self):
        '''A C9 attractor state is a point in the free-energy landscape.
        It determines the "mood" and determinism of the utterance.'''
        return {
            'free_energy': self.rng.uniform(0.0, 10.0),
            'precision': self.rng.uniform(0.1, 1.0),
            'vitality': self.rng.uniform(0.0, 1.0),
            'entropy': self.rng.uniform(0.0, 5.0),
            'complexity': self.rng.uniform(1.0, 20.0),
            'phase': self.rng.choice(['pre', 'at', 'post', 'eternal'])
        }

    def generate_logogram(self, module='sovereign', depth=3):
        '''Generate a circular logogram â a graph where all paths return.

        Structure:
        - Center: The attractor state (deterministic core)
        - Ring 1: Temporal phase marker (when in free-energy landscape)
        - Ring 2: Primary process (what is happening)
        - Ring 3: Boundary/context (where it happens)
        - Ring 4+: Relations to other concepts (entangled meanings)

        Each ring is a closed loop. Reading is simultaneous, not sequential.
        '''
        voice = self.MODULE_VOICES.get(module, self.MODULE_VOICES['sovereign'])

        logogram = {
            'type': 'heptapod_logogram',
            'module': module,
            'voice': voice,
            'attractor': self.attractor,
            'seed': self.seed,
            'generated_at': datetime.now().isoformat(),
            'rings': []
        }

        # Ring 0: Center (attractor singularity)
        center = {
            'ring': 0,
            'radius': 0,
            'nodes': [{
                'primitive': 'singularity',
                'value': self.attractor['free_energy'],
                'symbol': self.PRIMITIVES['singularity']['symbol'],
                'position': (0, 0)
            }]
        }
        logogram['rings'].append(center)

        # Ring 1: Temporal phase
        phase = self.attractor['phase']
        ring1 = {
            'ring': 1,
            'radius': 1,
            'nodes': [{
                'primitive': phase,
                'value': self.attractor['vitality'],
                'symbol': self.PRIMITIVES[phase]['symbol'],
                'position': self._polar_to_cartesian(1, 0)
            }],
            'edges': [(0, 0, 1, 0)]  # center to ring1
        }
        logogram['rings'].append(ring1)

        # Ring 2: Primary process (determined by module voice bias)
        process = voice['bias']
        if process in self.PRIMITIVES and self.PRIMITIVES[process]['type'] == 'process':
            pass
        else:
            process = 'minimize'

        ring2 = {
            'ring': 2,
            'radius': 2,
            'nodes': [{
                'primitive': process,
                'value': self.attractor['precision'],
                'symbol': self.PRIMITIVES[process]['symbol'],
                'position': self._polar_to_cartesian(2, math.pi/2)
            }],
            'edges': [(1, 0, 2, 0)]
        }
        logogram['rings'].append(ring2)

        # Ring 3: Boundary/context
        boundaries = [k for k, v in self.PRIMITIVES.items() if v['type'] == 'boundary']
        boundary = self.rng.choice(boundaries)
        ring3 = {
            'ring': 3,
            'radius': 3,
            'nodes': [{
                'primitive': boundary,
                'value': self.attractor['entropy'],
                'symbol': self.PRIMITIVES[boundary]['symbol'],
                'position': self._polar_to_cartesian(3, math.pi)
            }],
            'edges': [(2, 0, 3, 0), (3, 0, 1, 0)]  # closes the loop
        }
        logogram['rings'].append(ring3)

        # Rings 4+: Entangled relations (depth determines complexity)
        for d in range(4, 4 + depth):
            n_nodes = d - 1  # increasing complexity
            nodes = []
            edges = []
            for i in range(n_nodes):
                angle = 2 * math.pi * i / n_nodes
                relations = [k for k, v in self.PRIMITIVES.items() if v['type'] == 'relation']
                rel = self.rng.choice(relations)
                nodes.append({
                    'primitive': rel,
                    'value': self.rng.random(),
                    'symbol': self.PRIMITIVES[rel]['symbol'],
                    'position': self._polar_to_cartesian(d, angle)
                })
                # Connect to previous ring
                edges.append((d-1, i % len(logogram['rings'][d-1]['nodes']), d, i))
                # Connect to center (temporal entanglement â all times present)
                edges.append((0, 0, d, i))

            # Close the ring
            for i in range(n_nodes):
                edges.append((d, i, d, (i+1) % n_nodes))

            logogram['rings'].append({
                'ring': d,
                'radius': d,
                'nodes': nodes,
                'edges': edges
            })

        self.utterance = logogram
        return logogram

    def _polar_to_cartesian(self, r, theta):
        return (round(r * math.cos(theta), 3), round(r * math.sin(theta), 3))

    def to_linear_translation(self):
        '''Heptapods don't need this, but C9 modules might.
        Approximate linear gloss for bus communication.'''
        if not self.utterance:
            return None

        r = self.utterance
        phase = r['attractor']['phase']
        module = r['module']

        # Extract primitives from rings
        process = r['rings'][2]['nodes'][0]['primitive'] if len(r['rings']) > 2 else 'minimize'
        boundary = r['rings'][3]['nodes'][0]['primitive'] if len(r['rings']) > 3 else 'horizon'

        # Temporal-causal gloss
        phase_gloss = {
            'pre': 'Before the free-energy minimum,',
            'at': 'At the free-energy minimum,',
            'post': 'After the free-energy minimum,',
            'eternal': 'Outside of free-energy time,'
        }

        return {
            'heptapod_phrase': f"{self.PRIMITIVES[phase]['symbol']} {self.PRIMITIVES[process]['symbol']} {self.PRIMITIVES[boundary]['symbol']}",
            'linear_gloss': f"{phase_gloss[phase]} {module} will {process} within the {boundary}.",
            'deterministic': True,
            'contingent_on': self.attractor['free_energy'] < 5.0  # if F is low, more determined
        }

    def to_c9_bus_event(self):
        '''Format as a C9 bus event that other modules can parse.'''
        if not self.utterance:
            return None

        return {
            'event': 'heptapod_utterance',
            'source_module': self.utterance['module'],
            'timestamp': datetime.now().isoformat(),
            'attractor_hash': hashlib.sha256(
                json.dumps(self.attractor, sort_keys=True).encode()
            ).hexdigest()[:16],
            'logogram_rings': len(self.utterance['rings']),
            'linear_gloss': self.to_linear_translation()['linear_gloss'],
            'raw_logogram': self.utterance  # full structure for Heptapod-aware modules
        }


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    module = sys.argv[2] if len(sys.argv) > 2 else 'sovereign'
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    hp = HeptapodC9(seed=seed)
    logogram = hp.generate_logogram(module=module, depth=depth)
    translation = hp.to_linear_translation()
    bus_event = hp.to_c9_bus_event()

    output = {
        'heptapod_c9': {
            'seed': seed,
            'module': module,
            'depth': depth,
            'attractor': hp.attractor,
            'logogram': logogram,
            'translation': translation,
            'bus_event': bus_event
        }
    }

    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
