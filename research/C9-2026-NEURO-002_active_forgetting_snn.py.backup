#!/usr/bin/env python3
"""
================================================================================
CLOUD-9 ASSEMBLY PROJECT: ACTIVE FORGETTING IN SPIKING NEURAL NETWORKS
================================================================================
Entry ID: C9-2026-NEURO-002
Domain: Neurobiology -> Neuromorphic Computing
Theoretical Clusters: (4) Complexity Science, (6) Neuromorphic Computing, 
                      (8) Consciousness Studies

Core Claim: Active forgetting is a regulated disassembly process quantifiable 
by a Neural Assembly Index (A_n). Implementing this in SNNs improves continual 
learning beyond mere catastrophic forgetting prevention.

Author: Cloud-9 Research Repository
Date: 2026-05-09
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

class Config:
    """Hyperparameters for the active forgetting experiment"""
    # Network architecture
    N_INPUT = 100
    N_HIDDEN = 50
    N_OUTPUT = 10

    # Neuron dynamics
    TAU_MEM = 20.0      # ms
    TAU_SYN = 5.0       # ms
    V_THRESH = 1.0
    V_RESET = 0.0
    DT = 1.0            # ms

    # Learning
    STDP_LR = 0.05
    TAU_STDP = 20.0

    # Active forgetting
    DEPOTENTIATION_RATE = 0.02
    PRUNING_THRESHOLD = 0.15
    MIN_ACTIVE_SYNAPSES = 0.25

    # Experiment
    N_PATTERNS_PER_TASK = 5
    N_EPOCHS = 3
    PRESENTATION_STEPS = 100
    FORGETTING_STRENGTH = 2.0
    PASSIVE_DECAY_RATE = 0.05
    N_PASSIVE_STEPS = 10


# ============================================================
# NEURAL ASSEMBLY INDEX (A_n) FORMALISM
# ============================================================

def compute_A_n(W, activity_mask=None, complexity_weight=1.0):
    """
    Compute Neural Assembly Index for a synaptic weight matrix.

    Mathematical Definition:
    ------------------------
    A_n(W) = sum_{i,j} [ w_{ij} * C(s_{ij}) * R(p_{ij}) ]

    Where:
    - w_{ij}: synaptic weight (strength of connection)
    - C(s_{ij}): structural complexity of synapse i->j
                 ~ local connectivity density * dendritic spine volume
    - R(p_{ij}): recency/consolidation factor
                 ~ co-activity trace (hippocampal -> cortical transfer)

    For prototype: simplified to weight * local_clustering * activity_factor

    Parameters:
    -----------
    W : ndarray, shape (n_post, n_pre)
        Synaptic weight matrix
    activity_mask : ndarray, optional, shape (n_post, n_pre)
        Co-activity trace matrix (recency factor)
    complexity_weight : float
        Scaling factor for structural complexity

    Returns:
    --------
    A_n_total : float
        Total assembly index
    A_n_per_neuron : ndarray, shape (n_post,)
        Per-post-neuron assembly index
    A_n_matrix : ndarray, shape (n_post, n_pre)
        Full assembly index matrix
    """
    n_pre = W.shape[1]
    n_post = W.shape[0]

    # 1. Weight component
    weight_comp = W.copy()

    # 2. Structural complexity: local connectivity density
    complexity = np.zeros_like(W)
    for j in range(n_post):
        strong_mask = W[j, :] > np.mean(W[j, :])
        if np.sum(strong_mask) > 2:
            complexity[j, :] = np.mean(strong_mask) * complexity_weight
        else:
            complexity[j, :] = 0.1

    # 3. Recency factor
    if activity_mask is not None:
        recency = activity_mask / (activity_mask.max() + 1e-8)
    else:
        recency = np.ones_like(W)

    # Assembly Index computation
    A_n_matrix = weight_comp * complexity * recency
    A_n_total = np.sum(A_n_matrix)
    A_n_per_neuron = np.sum(A_n_matrix, axis=1)

    return A_n_total, A_n_per_neuron, A_n_matrix


# ============================================================
# SPIKING NEURAL NETWORK COMPONENTS
# ============================================================

class LIFNeuron:
    """Leaky Integrate-and-Fire neuron with exponential synaptic currents"""

    def __init__(self, cfg: Config):
        self.tau_mem = cfg.TAU_MEM
        self.tau_syn = cfg.TAU_SYN
        self.v_thresh = cfg.V_THRESH
        self.v_reset = cfg.V_RESET
        self.dt = cfg.DT

        self.v = cfg.V_RESET
        self.I_syn = 0.0
        self.spike = False
        self.trace = 0.0  # Eligibility trace for STDP

    def step(self, I_in=0.0):
        # Exponential synaptic current decay
        self.I_syn *= np.exp(-self.dt / self.tau_syn)
        self.I_syn += I_in

        # Membrane potential update
        dv = (-(self.v - self.v_reset) + self.I_syn) / self.tau_mem * self.dt
        self.v += dv

        # Spike detection
        self.spike = self.v >= self.v_thresh
        if self.spike:
            self.v = self.v_reset

        # Eligibility trace
        self.trace *= np.exp(-self.dt / self.tau_syn)
        if self.spike:
            self.trace += 1.0

        return float(self.spike)

    def reset(self):
        self.v = self.v_reset
        self.I_syn = 0.0
        self.spike = False
        self.trace = 0.0


class ActiveForgettingSNN:
    """
    2-layer Spiking Neural Network with STDP and active forgetting mechanisms.

    Architecture: N_INPUT -> N_HIDDEN -> N_OUTPUT

    Active Forgetting Mechanisms:
    1. Depotentiation: Weaken synapses with low co-activity
    2. Structural Pruning: Remove edges below threshold (preserve backbone)
    3. Reconsolidation Modulation: Post-recall labile window
    """

    def __init__(self, cfg: Config, mode='active'):
        self.cfg = cfg
        self.mode = mode  # 'active', 'passive', or 'none'

        # Initialize layers
        self.hidden = [LIFNeuron(cfg) for _ in range(cfg.N_HIDDEN)]
        self.output = [LIFNeuron(cfg) for _ in range(cfg.N_OUTPUT)]

        # Weight matrices
        self.W_ih = np.random.normal(0.5, 0.2, (cfg.N_HIDDEN, cfg.N_INPUT))
        self.W_ho = np.random.normal(0.5, 0.2, (cfg.N_OUTPUT, cfg.N_HIDDEN))
        self.W_ih = np.clip(self.W_ih, 0.01, 2.0)
        self.W_ho = np.clip(self.W_ho, 0.01, 2.0)

        # Activity tracking for depotentiation
        self.co_activity_ih = np.zeros((cfg.N_HIDDEN, cfg.N_INPUT))
        self.co_activity_ho = np.zeros((cfg.N_OUTPUT, cfg.N_HIDDEN))
        self.last_pre_spike_ih = np.full((cfg.N_HIDDEN, cfg.N_INPUT), -np.inf)
        self.last_post_spike_ih = np.full((cfg.N_HIDDEN, cfg.N_INPUT), -np.inf)

        # Time tracking
        self.t = 0

        # History
        self.history = {
            'A_n_ih': [],
            'A_n_ho': [],
            'mean_w_ih': [],
            'mean_w_ho': [],
            'n_active_ih': [],
            'n_active_ho': [],
        }

    def forward(self, input_spikes, record=True):
        """Run one timestep"""
        hidden_spikes = np.zeros(self.cfg.N_HIDDEN)
        for j, neuron in enumerate(self.hidden):
            I_in = np.dot(self.W_ih[j, :], input_spikes)
            hidden_spikes[j] = neuron.step(I_in)

        output_spikes = np.zeros(self.cfg.N_OUTPUT)
        for k, neuron in enumerate(self.output):
            I_in = np.dot(self.W_ho[k, :], hidden_spikes)
            output_spikes[k] = neuron.step(I_in)

        self._update_traces(input_spikes, hidden_spikes, output_spikes)
        self.t += self.cfg.DT

        if record and self.t % 100 == 0:
            self._record_metrics()

        return hidden_spikes, output_spikes

    def _update_traces(self, pre, post_h, post_o):
        """Update co-activity traces"""
        for j in range(self.cfg.N_HIDDEN):
            for i in range(self.cfg.N_INPUT):
                if pre[i] > 0:
                    self.last_pre_spike_ih[j, i] = self.t
                if post_h[j] > 0:
                    self.last_post_spike_ih[j, i] = self.t

        self.co_activity_ih *= 0.99
        self.co_activity_ho *= 0.99
        self.co_activity_ih += np.outer(post_h, pre) * 0.1
        self.co_activity_ho += np.outer(post_o, post_h) * 0.1

    def learn(self, pattern, target, n_steps=None):
        """Present pattern and apply STDP learning"""
        if n_steps is None:
            n_steps = self.cfg.PRESENTATION_STEPS

        for n in self.hidden + self.output:
            n.reset()

        for step in range(n_steps):
            input_spikes = (np.random.rand(self.cfg.N_INPUT) < pattern * 0.3).astype(float)
            hidden_spikes, output_spikes = self.forward(input_spikes, record=False)

            if step > 10:
                # STDP for input->hidden
                self._stdp_ih(input_spikes, hidden_spikes)
                # Simplified STDP for hidden->output
                self._stdp_ho(hidden_spikes, target)

        self._record_metrics()

    def _stdp_ih(self, pre, post):
        """STDP update for input->hidden weights"""
        delta = np.zeros_like(self.W_ih)
        for j in range(self.cfg.N_HIDDEN):
            for i in range(self.cfg.N_INPUT):
                if pre[i] > 0 and post[j] > 0:
                    dt_spike = self.last_post_spike_ih[j, i] - self.last_pre_spike_ih[j, i]
                    if dt_spike > 0:
                        delta[j, i] = self.cfg.STDP_LR * np.exp(-abs(dt_spike) / self.cfg.TAU_STDP)
                    elif dt_spike < 0:
                        delta[j, i] = -self.cfg.STDP_LR * 0.5 * np.exp(-abs(dt_spike) / self.cfg.TAU_STDP)
        self.W_ih += delta
        self.W_ih = np.clip(self.W_ih, 0.01, 2.0)

    def _stdp_ho(self, pre, target):
        """Simplified STDP for hidden->output"""
        for k in range(self.cfg.N_OUTPUT):
            for j in range(self.cfg.N_HIDDEN):
                if pre[j] > 0 and target[k] > 0:
                    self.W_ho[k, j] += self.cfg.STDP_LR * 0.5
                elif pre[j] > 0 and target[k] == 0:
                    self.W_ho[k, j] -= self.cfg.STDP_LR * 0.2
        self.W_ho = np.clip(self.W_ho, 0.01, 2.0)

    def active_forgetting(self, strength=None):
        """Active forgetting: regulated disassembly"""
        if strength is None:
            strength = self.cfg.FORGETTING_STRENGTH

        # Depotentiation
        co_norm_ih = self.co_activity_ih / (self.co_activity_ih.max() + 1e-8)
        co_norm_ho = self.co_activity_ho / (self.co_activity_ho.max() + 1e-8)

        depot_ih = (1 - co_norm_ih) ** 2 * self.cfg.DEPOTENTIATION_RATE * strength
        depot_ho = (1 - co_norm_ho) ** 2 * self.cfg.DEPOTENTIATION_RATE * strength

        self.W_ih *= (1 - depot_ih)
        self.W_ho *= (1 - depot_ho)

        # Structural pruning (preserve backbone)
        self._prune_weights(self.W_ih, self.cfg.N_HIDDEN, self.cfg.N_INPUT)
        self._prune_weights(self.W_ho, self.cfg.N_OUTPUT, self.cfg.N_HIDDEN)

        self.W_ih = np.clip(self.W_ih, 0.01, 2.0)
        self.W_ho = np.clip(self.W_ho, 0.01, 2.0)

        # Decay traces
        self.co_activity_ih *= 0.5
        self.co_activity_ho *= 0.5

        self._record_metrics()

    def _prune_weights(self, W, n_post, n_pre):
        """Prune low-weight synapses while protecting backbone"""
        n_total = n_post * n_pre
        current_active = np.sum(W > self.cfg.PRUNING_THRESHOLD)
        min_allowed = int(n_total * self.cfg.MIN_ACTIVE_SYNAPSES)

        if current_active > min_allowed:
            prune_mask = W < self.cfg.PRUNING_THRESHOLD
            for j in range(n_post):
                strong_count = np.sum(W[j, :] > self.cfg.PRUNING_THRESHOLD)
                if strong_count <= 3:
                    prune_mask[j, :] = False
            W[prune_mask] = 0.01

    def passive_forgetting(self):
        """Uniform weight decay (baseline)"""
        for _ in range(self.cfg.N_PASSIVE_STEPS):
            self.W_ih *= (1 - self.cfg.PASSIVE_DECAY_RATE)
            self.W_ho *= (1 - self.cfg.PASSIVE_DECAY_RATE)
        self.W_ih = np.clip(self.W_ih, 0.01, 2.0)
        self.W_ho = np.clip(self.W_ho, 0.01, 2.0)
        self._record_metrics()

    def _record_metrics(self):
        """Record A_n and network statistics"""
        A_n_ih, _, _ = compute_A_n(self.W_ih, self.co_activity_ih)
        A_n_ho, _, _ = compute_A_n(self.W_ho, self.co_activity_ho)

        self.history['A_n_ih'].append(A_n_ih)
        self.history['A_n_ho'].append(A_n_ho)
        self.history['mean_w_ih'].append(np.mean(self.W_ih))
        self.history['mean_w_ho'].append(np.mean(self.W_ho))
        self.history['n_active_ih'].append(np.sum(self.W_ih > self.cfg.PRUNING_THRESHOLD))
        self.history['n_active_ho'].append(np.sum(self.W_ho > self.cfg.PRUNING_THRESHOLD))

    def test(self, pattern, n_steps=50):
        """Test network response"""
        for n in self.hidden + self.output:
            n.reset()

        output_counts = np.zeros(self.cfg.N_OUTPUT)
        for _ in range(n_steps):
            input_spikes = (np.random.rand(self.cfg.N_INPUT) < pattern * 0.3).astype(float)
            _, output_spikes = self.forward(input_spikes, record=False)
            output_counts += output_spikes

        return output_counts / n_steps

    def pattern_separation(self, patterns):
        """Measure separation between pattern responses"""
        responses = [self.test(p) for p in patterns]
        responses = np.array(responses)

        distances = []
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                distances.append(np.linalg.norm(responses[i] - responses[j]))

        return np.mean(distances) if distances else 0.0


# ============================================================
# EXPERIMENT: CONTINUAL LEARNING WITH ACTIVE FORGETTING
# ============================================================

def generate_pattern(n, seed, n_active=20):
    """Generate structured pattern with clustered activity"""
    np.random.seed(seed)
    p = np.zeros(n)
    centers = np.random.choice(n - 5, size=3, replace=False)
    for c in centers:
        p[c:c+5] = np.random.rand(5) * 0.8 + 0.2
    return np.clip(p, 0, 1)


def run_experiment(cfg: Config):
    """Run the full continual learning experiment"""

    # Generate tasks
    np.random.seed(100)
    patterns_A = [generate_pattern(cfg.N_INPUT, seed=i*10) for i in range(cfg.N_PATTERNS_PER_TASK)]
    targets_A = np.eye(cfg.N_OUTPUT)[:cfg.N_PATTERNS_PER_TASK]

    np.random.seed(200)
    patterns_B = [generate_pattern(cfg.N_INPUT, seed=i*10+500) for i in range(cfg.N_PATTERNS_PER_TASK)]
    targets_B = np.eye(cfg.N_OUTPUT)[cfg.N_PATTERNS_PER_TASK:2*cfg.N_PATTERNS_PER_TASK]

    results = {}

    # --- Active Forgetting ---
    print("\n[Active Forgetting SNN]")
    net = ActiveForgettingSNN(cfg, mode='active')

    for p, t in zip(patterns_A, targets_A):
        net.learn(p, t)
    sep_A = net.pattern_separation(patterns_A)
    print(f"  Task A separation: {sep_A:.3f}")

    net.active_forgetting()

    for p, t in zip(patterns_B, targets_B):
        net.learn(p, t)
    sep_B = net.pattern_separation(patterns_B)
    sep_A_after = net.pattern_separation(patterns_A)
    print(f"  Task B separation: {sep_B:.3f}")
    print(f"  Task A retention: {sep_A_after:.3f}")

    results['active'] = {
        'net': net,
        'sep_A_initial': sep_A,
        'sep_B': sep_B,
        'sep_A_after': sep_A_after
    }

    # --- Passive Forgetting ---
    print("\n[Passive Forgetting SNN]")
    net = ActiveForgettingSNN(cfg, mode='passive')

    for p, t in zip(patterns_A, targets_A):
        net.learn(p, t)
    sep_A = net.pattern_separation(patterns_A)
    print(f"  Task A separation: {sep_A:.3f}")

    net.passive_forgetting()

    for p, t in zip(patterns_B, targets_B):
        net.learn(p, t)
    sep_B = net.pattern_separation(patterns_B)
    sep_A_after = net.pattern_separation(patterns_A)
    print(f"  Task B separation: {sep_B:.3f}")
    print(f"  Task A retention: {sep_A_after:.3f}")

    results['passive'] = {
        'net': net,
        'sep_A_initial': sep_A,
        'sep_B': sep_B,
        'sep_A_after': sep_A_after
    }

    # --- No Forgetting ---
    print("\n[No Forgetting SNN]")
    net = ActiveForgettingSNN(cfg, mode='none')

    for p, t in zip(patterns_A, targets_A):
        net.learn(p, t)
    sep_A = net.pattern_separation(patterns_A)
    print(f"  Task A separation: {sep_A:.3f}")

    for p, t in zip(patterns_B, targets_B):
        net.learn(p, t)
    sep_B = net.pattern_separation(patterns_B)
    sep_A_after = net.pattern_separation(patterns_A)
    print(f"  Task B separation: {sep_B:.3f}")
    print(f"  Task A retention: {sep_A_after:.3f}")

    results['none'] = {
        'net': net,
        'sep_A_initial': sep_A,
        'sep_B': sep_B,
        'sep_A_after': sep_A_after
    }

    return results, patterns_A, patterns_B


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    cfg = Config()
    results, pA, pB = run_experiment(cfg)

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"{'Condition':<20} {'A Retention':>12} {'B Learning':>12} {'Final A_n':>12}")
    print("-"*60)
    for mode in ['active', 'passive', 'none']:
        r = results[mode]
        A_n = r['net'].history['A_n_ih'][-1]
        print(f"{mode:<20} {r['sep_A_after']:>12.3f} {r['sep_B']:>12.3f} {A_n:>12.1f}")
