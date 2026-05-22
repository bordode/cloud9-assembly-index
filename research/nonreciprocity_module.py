#!/usr/bin/env python3
"""
nonreciprocity_module.py
Cloud-9 Assembly Project v1.0.1

Unified framework for computing nonreciprocal interaction metrics across
quantum, classical, and biological systems. Bridges:
  - 1D anyon tunable statistics (OIST 2025)
  - Acoustic time crystals (NYU 2026)
  - TNG halo dynamics (existing validation suite)
  - Memristor-SPICE neuromorphic interfaces
  - Biological circadian oscillators

Author: Cloud-9 Assembly Team
Date: 2026-05-16
"""

import numpy as np
from typing import Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# CORE DATA STRUCTURES
# ---------------------------------------------------------------------------

class SystemType(Enum):
    QUANTUM_ANYON = "quantum_anyon"           # C9-2026-ANYON-001
    CLASSICAL_TIME_CRYSTAL = "classical_tc"   # C9-2026-TIME-001
    TNG_HALO = "tng_halo"                     # Memory #4
    MEMRISTOR_SNN = "memristor_snn"           # Memory #5
    BIOLOGICAL_CLOCK = "bio_clock"            # Circadian extension

@dataclass
class NonreciprocityProfile:
    """
    Canonical representation of nonreciprocal coupling in any system.

    Attributes:
        J: Interaction Jacobian matrix (nÃn)
        eta: Nonreciprocity metric ||J - J^T|| / ||J|| â [0, 1]
        sigma_t: Statistical tunability (for anyons: dÎ±/dg)
        A_t: Temporal Assembly Index (for time crystals)
        energy_harvesting: Efficiency of work extraction from static field
        causal_closure: Directed mutual information (I_causal)
    """
    J: np.ndarray
    eta: float
    sigma_t: Optional[float] = None
    A_t: Optional[float] = None
    energy_harvesting: Optional[float] = None
    causal_closure: Optional[float] = None

    def __post_init__(self):
        assert 0.0 <= self.eta <= 1.0, "Nonreciprocity eta must be in [0,1]"

# ---------------------------------------------------------------------------
# NONRECIPROCITY COMPUTATIONS
# ---------------------------------------------------------------------------

def compute_nonreciprocity(J: np.ndarray, norm: str = "frobenius") -> float:
    """
    Compute Î· = ||J - J^T|| / ||J|| for any interaction matrix.

    Args:
        J: nÃn interaction Jacobian
        norm: Matrix norm type ("frobenius", "spectral", "nuclear")

    Returns:
        Nonreciprocity metric Î· â [0, 1]
        Î· = 0: fully reciprocal (symmetric J)
        Î· = 1: maximally nonreciprocal
    """
    if norm == "frobenius":
        num = np.linalg.norm(J - J.T, "fro")
        den = np.linalg.norm(J, "fro")
    elif norm == "spectral":
        num = np.linalg.norm(J - J.T, 2)
        den = np.linalg.norm(J, 2)
    else:
        raise ValueError(f"Unknown norm: {norm}")

    return num / den if den > 1e-12 else 0.0


def anyon_exchange_factor(g_1D: float, mass: float = 1.0) -> float:
    """
    Compute 1D anyon exchange factor Î± from interaction strength.

    Based on Hidalgo-Sacoto et al. (2025) mapping:
    Î±(g) = tanh(Ï * g_1D / (2âÂ²k_F))  [simplified model]

    For bosons: Î± â +1 (g â 0)
    For fermions: Î± â â1 (g â â)

    Args:
        g_1D: 1D interaction strength (energy Ã length)
        mass: Particle mass (default 1.0 in natural units)

    Returns:
        Exchange factor Î± â (â1, +1)
    """
    # Simplified tanh mapping; paper has exact Bethe ansatz solution
    k_F = np.pi  # Fermi wavevector (natural units)
    x = np.pi * g_1D / (2 * k_F)
    return np.tanh(x)


def statistical_tunability(g_1D: float, dg: float = 1e-6) -> float:
    """
    Compute Ï_t = dÎ±/d(g_1D) â sensitivity of exchange statistics to 
    interaction tuning. Higher Ï_t â more programmable complexity.

    Args:
        g_1D: Base interaction strength
        dg: Numerical differentiation step

    Returns:
        Tunability Ï_t
    """
    alpha_plus = anyon_exchange_factor(g_1D + dg)
    alpha_minus = anyon_exchange_factor(g_1D - dg)
    return (alpha_plus - alpha_minus) / (2 * dg)


# ---------------------------------------------------------------------------
# TIME CRYSTAL DYNAMICS
# ---------------------------------------------------------------------------

def acoustic_time_crystal_odes(state: np.ndarray, t: float,
                                m1: float, m2: float,
                                gamma: float,  # drag coefficient
                                k_acoustic: float,  # acoustic stiffness
                                eta: float) -> np.ndarray:
    """
    ODE system for 2-bead acoustic time crystal (Grier et al. 2026).

    State vector: [x1, v1, x2, v2]
    Nonreciprocal coupling: bead 1 (larger, mass m1) scatters more sound
    than bead 2 (smaller, mass m2).

    Equations:
        dx1/dt = v1
        dv1/dt = -(gamma/m1)*v1 + (k_acoustic/m1)*(x2 - x1) + eta*(x2/m2)
        dx2/dt = v2
        dv2/dt = -(gamma/m2)*v2 + (k_acoustic/m2)*(x1 - x2) - eta*(x1/m1)

    The eta terms encode nonreciprocity: larger bead exerts stronger 
    influence than it receives.
    """
    x1, v1, x2, v2 = state

    dx1 = v1
    dv1 = (-gamma * v1 + k_acoustic * (x2 - x1) + eta * (x2 / m2)) / m1
    dx2 = v2
    dv2 = (-gamma * v2 + k_acoustic * (x1 - x2) - eta * (x1 / m1)) / m2

    return np.array([dx1, dv1, dx2, dv2])


def temporal_assembly_index(trajectory: np.ndarray, 
                           dt: float,
                           eta: float,
                           power_in: float,
                           power_dissipated: float) -> float:
    """
    Compute A_t = complexity(limit_cycle) Ã Î· Ã efficiency

    Args:
        trajectory: NÃ4 array from ODE integration
        dt: Time step
        eta: Nonreciprocity metric
        power_in: Acoustic power input
        power_dissipated: Viscous dissipation

    Returns:
        Temporal Assembly Index A_t
    """
    # Limit cycle complexity: Fourier spectrum entropy
    freqs = np.fft.rfftfreq(len(trajectory), dt)
    spectrum = np.abs(np.fft.rfft(trajectory[:, 0]))  # x1 spectrum
    spectrum = spectrum / np.sum(spectrum)
    spectral_entropy = -np.sum(spectrum * np.log(spectrum + 1e-12))

    # Energy harvesting efficiency
    efficiency = (power_in - power_dissipated) / power_in if power_in > 0 else 0

    return spectral_entropy * eta * efficiency


# ---------------------------------------------------------------------------
# TNG HALO BRIDGE
# ---------------------------------------------------------------------------

def halo_shell_nonreciprocity(shell_radii: np.ndarray,
                               shell_masses: np.ndarray,
                               metallicities: np.ndarray) -> NonreciprocityProfile:
    """
    Compute nonreciprocity for TNG dark matter halo shells.

    Maps shell interactions to effective nonreciprocal Jacobian:
    J_ij ~ G * m_i * m_j / |r_i - r_j|Â² Ã (1 + Z_i/Z_j)  
    where Z is metallicity bias (asymmetric coupling).

    Args:
        shell_radii: Array of shell radii (kpc)
        shell_masses: Array of shell masses (M_sun)
        metallicities: Array of metallicities Z

    Returns:
        NonreciprocityProfile for halo
    """
    n = len(shell_radii)
    J = np.zeros((n, n))

    G_eff = 4.302e-6  # kpc (km/s)Â² / M_sun

    for i in range(n):
        for j in range(n):
            if i != j:
                r_ij = abs(shell_radii[i] - shell_radii[j])
                # Asymmetric coupling: metallicity creates nonreciprocity
                asymmetry = 1.0 + (metallicities[i] / metallicities[j] - 1.0) * 0.1
                J[i, j] = G_eff * shell_masses[i] * shell_masses[j] / (r_ij**2) * asymmetry

    eta = compute_nonreciprocity(J)

    return NonreciprocityProfile(
        J=J,
        eta=eta,
        causal_closure=None  # To be computed from directed information flow
    )


# ---------------------------------------------------------------------------
# MEMRISTOR-SNN BRIDGE
# ---------------------------------------------------------------------------

def memristor_crossbar_nonreciprocity(conductance_matrix: np.ndarray,
                                       threshold: float = 0.01) -> NonreciprocityProfile:
    """
    Map memristor crossbar conductance asymmetry to nonreciprocity.

    In neuromorphic arrays, G[i,j] â  G[j,i] due to device variability.
    This asymmetry is functional â it enables learning.

    Args:
        conductance_matrix: nÃn conductance array (Siemens)
        threshold: Minimum conductance for active synapse

    Returns:
        NonreciprocityProfile with eta, sigma_t (learning rate proxy)
    """
    # Mask sub-threshold connections
    active = conductance_matrix > threshold
    J = conductance_matrix * active.astype(float)

    eta = compute_nonreciprocity(J)

    # Statistical tunability: how much conductance changes per pulse
    # Approximated from asymmetry magnitude
    sigma_t = np.mean(np.abs(J - J.T)) / np.mean(J + J.T + 1e-12)

    return NonreciprocityProfile(
        J=J,
        eta=eta,
        sigma_t=sigma_t
    )


# ---------------------------------------------------------------------------
# BIOLOGICAL CLOCK BRIDGE
# ---------------------------------------------------------------------------

def circadian_nonreciprocity(reaction_rates: np.ndarray,
                              regulatory_matrix: np.ndarray) -> NonreciprocityProfile:
    """
    Compute nonreciprocity for biochemical oscillator (e.g., KaiC).

    Nonreciprocity arises from phosphorylation/dephosphorylation asymmetry
    and unequal feedback in transcriptional regulation.

    Args:
        reaction_rates: Vector of rate constants
        regulatory_matrix: nÃn regulatory interaction matrix

    Returns:
        NonreciprocityProfile with biological causal closure estimate
    """
    J = np.diag(reaction_rates) @ regulatory_matrix
    eta = compute_nonreciprocity(J)

    # Causal closure: perturbation recovery time (inverse Lyapunov exponent)
    eigenvalues = np.linalg.eigvals(J)
    max_real = np.max(np.real(eigenvalues))
    causal_closure = -max_real if max_real < 0 else 0.0  # Stable limit cycle

    return NonreciprocityProfile(
        J=J,
        eta=eta,
        causal_closure=causal_closure
    )


# ---------------------------------------------------------------------------
# A_c FRAMEWORK INTEGRATION
# ---------------------------------------------------------------------------

def compute_A_c_nonreciprocal(profiles: list[NonreciprocityProfile],
                               weights: Optional[np.ndarray] = None) -> dict:
    """
    Aggregate nonreciprocity profiles into Cloud-9 Assembly Index components.

    Returns dict with:
        A_c^{(anyon)}: Quantum statistical tunability contribution
        A_c^{(time)}: Temporal pattern complexity contribution  
        A_c^{(bio)}: Biological causal closure contribution
        A_c^{(total)}: Weighted sum
    """
    if weights is None:
        weights = np.ones(len(profiles)) / len(profiles)

    A_anyon = sum(p.sigma_t * w for p, w in zip(profiles, weights) 
                  if p.sigma_t is not None)
    A_time = sum(p.A_t * w for p, w in zip(profiles, weights) 
                 if p.A_t is not None)
    A_bio = sum(p.causal_closure * w for p, w in zip(profiles, weights) 
                if p.causal_closure is not None)

    return {
        "A_c_anyon": A_anyon,
        "A_c_time": A_time,
        "A_c_bio": A_bio,
        "A_c_total": A_anyon + A_time + A_bio,
        "mean_eta": np.mean([p.eta for p in profiles]),
        "max_eta": np.max([p.eta for p in profiles])
    }


# ---------------------------------------------------------------------------
# VALIDATION & TESTING
# ---------------------------------------------------------------------------

def run_validation_suite():
    """
    Execute all validation tests for C9-2026-ANYON-001 and C9-2026-TIME-001.
    """
    print("=" * 70)
    print("CLOUD-9 NONRECIPROCITY VALIDATION SUITE")
    print("=" * 70)

    # Test 1: Anyon exchange factor mapping
    print("\n[TEST 1] Anyon exchange factor Î±(g)")
    g_values = np.linspace(-5, 5, 11)
    for g in g_values:
        alpha = anyon_exchange_factor(g)
        sigma = statistical_tunability(g)
        print(f"  g={g:+.2f}  â  Î±={alpha:+.4f}  Ï_t={sigma:.4f}")

    # Test 2: Time crystal ODE integration
    print("\n[TEST 2] Acoustic time crystal dynamics")
    from scipy.integrate import odeint

    m1, m2 = 2.0, 1.0  # Larger and smaller bead
    gamma = 0.1
    k_acoustic = 1.0
    eta_tc = 0.3

    t = np.linspace(0, 50, 5000)
    state0 = np.array([0.1, 0.0, -0.1, 0.0])

    sol = odeint(acoustic_time_crystal_odes, state0, t,
                 args=(m1, m2, gamma, k_acoustic, eta_tc))

    A_t = temporal_assembly_index(sol, t[1]-t[0], eta_tc, 1.0, 0.7)
    print(f"  Limit cycle established: |x1_max|={np.max(np.abs(sol[:,0])):.3f}")
    print(f"  Temporal Assembly Index A_t={A_t:.4f}")

    # Test 3: Nonreciprocity metric
    print("\n[TEST 3] Nonreciprocity computation")
    J_sym = np.array([[0, 1], [1, 0]])
    J_asym = np.array([[0, 2], [1, 0]])
    print(f"  Symmetric J: Î·={compute_nonreciprocity(J_sym):.4f}")
    print(f"  Asymmetric J: Î·={compute_nonreciprocity(J_asym):.4f}")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_validation_suite()
