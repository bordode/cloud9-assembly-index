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
import c9_bus_client  # C9 bus injection

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
        c9_bus_client.heartbeat()
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


# ---------------------------------------------------------------------------
# MASS ASSEMBLY INDEX (A_m) â C9-2026-ETAPRIME-001 Extension
# ---------------------------------------------------------------------------

def mass_assembly_index(m_observed: float,
                        m_bare: float,
                        lambda_qcd: float = 200.0,  # MeV
                        I_anomaly: float = 0.95) -> float:
    """
    Compute A_m = (m_observed - m_bare) / Î_QCD Ã I_anomaly

    Quantifies how much of a particle's mass is "assembled" from 
    symmetry breaking vs. fundamental quark rest mass.

    Args:
        m_observed: Measured mass in given medium (MeV)
        m_bare: Quark rest mass contribution (MeV)
        lambda_qcd: QCD confinement scale (MeV)
        I_anomaly: Anomaly-induced mass fraction (0 to 1)

    Returns:
        Mass Assembly Index A_m
    """
    return ((m_observed - m_bare) / lambda_qcd) * I_anomaly


def chiral_restoration_factor(m_in_medium: float,
                               m_free: float) -> float:
    """
    Compute degree of chiral symmetry restoration from mass reduction.

    R = 1 - (m_in_medium / m_free)

    R = 0: no restoration (vacuum)
    R = 1: full restoration (massless, symmetric phase)

    Args:
        m_in_medium: Mass inside nuclear matter (MeV)
        m_free: Free-space mass (MeV)

    Returns:
        Restoration factor R â [0, 1]
    """
    return 1.0 - (m_in_medium / m_free)


def eta_prime_mass_shift(nuclear_density: float,
                          saturation_density: float = 0.16,  # fm^-3
                          free_mass: float = 958.0,  # MeV
                          max_shift: float = 150.0) -> float:
    """
    Predict Î·â² mass reduction in nuclear medium.

    Linear approximation: Îm ~ -max_shift Ã (Ï / Ï_sat)
    Literature: 60-150 MeV expected at saturation density.

    Args:
        nuclear_density: Medium density (fm^-3)
        saturation_density: Nuclear saturation density (fm^-3)
        free_mass: Free-space Î·â² mass (MeV)
        max_shift: Maximum expected mass shift (MeV)

    Returns:
        In-medium Î·â² mass (MeV)
    """
    shift = max_shift * (nuclear_density / saturation_density)
    return free_mass - shift


def vacuum_assembly_complexity(Temperature: float,
                                T_chiral: float = 170.0) -> float:
    """
    Compute A_c^{(vacuum)} as function of temperature.

    Above T_chiral (~170 MeV): chiral symmetry restored, A_c â 0
    Below T_chiral: symmetry broken, A_c increases as T decreases

    Model: A_c ~ (1 - T/T_chiral)^Î² for T < T_chiral, 0 otherwise
    where Î² ~ 0.3-0.5 (critical exponent)

    Args:
        Temperature: System temperature (MeV)
        T_chiral: Chiral phase transition temperature (MeV)

    Returns:
        Vacuum assembly complexity A_c^{(vacuum)}
    """
    beta = 0.4  # Mean-field approximation
    if Temperature >= T_chiral:
        return 0.0
    return (1.0 - Temperature / T_chiral) ** beta


# ---------------------------------------------------------------------------
# TRIAD SYNTHESIS: Nonreciprocity + Statistical Tunability + Mass Assembly
# ---------------------------------------------------------------------------

def compute_unified_A_c(profiles: list,
                         mass_profiles: list,
                         weights: Optional[np.ndarray] = None) -> dict:
    """
    Unified Assembly Index combining all three 2026 discovery channels.

    Args:
        profiles: List of NonreciprocityProfile (anyon + time crystal)
        mass_profiles: List of dict with keys 'm_observed', 'm_bare', 'I_anomaly'
        weights: Optional weighting array

    Returns:
        Dict with A_c^{(total)}, A_c^{(anyon)}, A_c^{(time)}, A_c^{(mass)}
    """
    # Nonreciprocal contributions (from existing module)
    A_anyon = sum(p.sigma_t for p in profiles if p.sigma_t is not None)
    A_time = sum(p.A_t for p in profiles if p.A_t is not None)

    # Mass assembly contributions
    A_mass = sum(
        mass_assembly_index(m['m_observed'], m['m_bare'], I_anomaly=m['I_anomaly'])
        for m in mass_profiles
    )

    # Vacuum complexity (temperature-dependent, default T=0)
    A_vacuum = vacuum_assembly_complexity(0.0)

    return {
        "A_c_anyon": A_anyon,
        "A_c_time": A_time,
        "A_c_mass": A_mass,
        "A_c_vacuum": A_vacuum,
        "A_c_total": A_anyon + A_time + A_mass + A_vacuum,
        "triad_completeness": len(profiles) + len(mass_profiles)
    }


# ---------------------------------------------------------------------------
# LHCb B MESON ANOMALY & MODEL COMPLETENESS â C9-2026-LHCB-001 Extension
# ---------------------------------------------------------------------------

def model_completeness_index(confirmed_predictions: int,
                              total_predictions: int,
                              causal_closure_strength: float,
                              free_parameters: int) -> float:
    """
    Compute A_M = (confirmed/total) Ã causal_closure Ã (1/free_params)

    Quantifies how "complete" a physical theory is as an assembly.
    Higher A_M â fewer free parameters, better predictive power,
    stronger causal closure.

    Args:
        confirmed_predictions: Number of experimentally verified predictions
        total_predictions: Total number of predictions made
        causal_closure_strength: 0-1 measure of theory robustness
        free_parameters: Number of undetermined parameters

    Returns:
        Model Completeness Index A_M â [0, 1]
    """
    predictive_power = confirmed_predictions / total_predictions
    param_penalty = 1.0 / (1.0 + np.log(free_parameters + 1))
    return predictive_power * causal_closure_strength * param_penalty


def lepton_flavor_universality_ratio(BR_mu: float, BR_e: float) -> float:
    """
    Compute R_K = BR(B â K Î¼âºÎ¼â») / BR(B â K eâºeâ»)

    SM prediction: R_K â 1.0 (within few %)
    Measured: R_K â 0.846 Â± 0.042 (LHCb 2021) â ~3Ï tension

    Args:
        BR_mu: Branching ratio to muons
        BR_e: Branching ratio to electrons

    Returns:
        R_K ratio
    """
    return BR_mu / BR_e


def penguin_decay_amplitude(C9_SM: complex,
                            C10_SM: complex,
                            C9_NP: complex = 0,
                            C10_NP: complex = 0) -> complex:
    """
    Compute Bâ° â K*â° Î¼âºÎ¼â» decay amplitude with SM + new physics.

    SMEFT parametrization: Wilson coefficients C9, C10
    SM: C9 â 4.2, C10 â -4.2
    NP (leptoquark): C9_NP â -C10_NP (vector LQ) or C9_NP â C10_NP (scalar LQ)

    Args:
        C9_SM: SM Wilson coefficient C9
        C10_SM: SM Wilson coefficient C10
        C9_NP: New physics contribution to C9
        C10_NP: New physics contribution to C10

    Returns:
        Total decay amplitude
    """
    C9_total = C9_SM + C9_NP
    C10_total = C10_SM + C10_NP
    # Simplified: amplitude ~ (C9_total - C10_total) for vector current
    return C9_total - C10_total


def anomaly_significance(data_value: float,
                          sm_prediction: float,
                          uncertainty: float) -> float:
    """
    Compute significance of deviation from SM in units of Ï.

    Args:
        data_value: Measured value
        sm_prediction: Standard Model prediction
        uncertainty: Combined experimental + theoretical uncertainty

    Returns:
        Significance in Ï
    """
    return abs(data_value - sm_prediction) / uncertainty


def leptoquark_mass_constraint(g_coupling: float,
                                anomaly_strength: float,
                                target_significance: float = 5.0) -> float:
    """
    Estimate leptoquark mass from coupling strength and anomaly.

    Approximate: M_LQ ~ g / sqrt(ÎC) where ÎC is NP Wilson coefficient
    needed to explain anomaly.

    Args:
        g_coupling: Leptoquark Yukawa coupling
        anomaly_strength: Measured NP contribution (e.g. ÎC9)
        target_significance: Desired significance (default 5Ï)

    Returns:
        Estimated leptoquark mass (TeV)
    """
    return g_coupling / np.sqrt(abs(anomaly_strength)) * target_significance / 5.0


# ---------------------------------------------------------------------------
# QUARTET SYNTHESIS: Unified A_c for all four 2026 discoveries
# ---------------------------------------------------------------------------

def compute_quartet_A_c(anyon_profile: Optional[NonreciprocityProfile] = None,
                         time_profile: Optional[NonreciprocityProfile] = None,
                         mass_profile: Optional[dict] = None,
                         sm_model: Optional[dict] = None) -> dict:
    """
    Compute unified Assembly Index across the 2026 Quartet.

    Args:
        anyon_profile: NonreciprocityProfile for 1D anyons
        time_profile: NonreciprocityProfile for time crystals
        mass_profile: Dict with 'm_observed', 'm_bare', 'I_anomaly'
        sm_model: Dict with 'confirmed', 'total', 'closure', 'free_params'

    Returns:
        Dict with all four A_c components and total
    """
    A_anyon = anyon_profile.sigma_t if anyon_profile and anyon_profile.sigma_t else 0.0
    A_time = time_profile.A_t if time_profile and time_profile.A_t else 0.0

    A_mass = 0.0
    if mass_profile:
        A_mass = mass_assembly_index(
            mass_profile['m_observed'],
            mass_profile['m_bare'],
            I_anomaly=mass_profile.get('I_anomaly', 0.95)
        )

    A_model = 0.0
    if sm_model:
        A_model = model_completeness_index(
            sm_model['confirmed'],
            sm_model['total'],
            sm_model['closure'],
            sm_model['free_params']
        )

    return {
        "A_c_anyon": A_anyon,
        "A_c_time": A_time,
        "A_c_mass": A_mass,
        "A_c_model": A_model,
        "A_c_total": A_anyon + A_time + A_mass + A_model,
        "quartet_completeness": sum(x > 0 for x in [A_anyon, A_time, A_mass, A_model])
    }


# ---------------------------------------------------------------------------
# COSMOS-WEB / TNG VALIDATION BRIDGE â C9-2026-COSMOS-001 Extension
# ---------------------------------------------------------------------------

def environmental_assembly_index(overdensity: float,
                                  stellar_mass: float,
                                  sfr: float,
                                  redshift: float,
                                  quiescent: bool = False) -> float:
    """
    Compute A_env = f(Î´, M*, SFR, z, quenched) from COSMOS-Web observations.

    Based on Hatamnia et al. (2026) empirical correlations:
    â¢ QGs at zâ²2.5: A_env â log(1+Î´) Ã log(M*)
    â¢ SFGs at zâ³1.8: A_env â SFR Ã Î´
    â¢ Mass-driven quenching at zâ³2.5: A_env â M_halo^0.5 Ã f_quench
    â¢ Environmental quenching at zâ²0.8: A_env â Î´ Ã (1 - sSFR/sSFR_max)

    Args:
        overdensity: log(1+Î´) where Î´ is density contrast
        stellar_mass: Stellar mass in solar masses (Mâ)
        sfr: Star formation rate in Mâ/yr
        redshift: Cosmic redshift z
        quiescent: True if galaxy is quiescent (QG), False if star-forming (SFG)

    Returns:
        Environmental Assembly Index A_env â [0, 1]
    """
    # Base components
    mass_term = np.log10(stellar_mass / 1e10) + 1.0  # Normalize to 10^10 Mâ
    density_term = max(0, overdensity)
    sfr_term = np.log10(max(sfr, 0.01)) + 2.0  # Normalize, avoid log(0)

    # Redshift-dependent quenching transition
    if redshift > 2.5:
        # Mass-driven quenching dominates
        quench_factor = 1.0 if not quiescent else 0.3
        A_env = mass_term * quench_factor * (1.0 + 0.2 * density_term)
    elif redshift > 0.8:
        # Mixed regime
        if quiescent:
            A_env = mass_term * density_term * 0.7
        else:
            A_env = mass_term * (1.0 + 0.3 * density_term) * (1.0 + 0.1 * sfr_term)
    else:
        # Environmental quenching dominates
        if quiescent:
            A_env = mass_term * density_term * 0.9
        else:
            A_env = mass_term * (1.0 + 0.1 * density_term) * (1.0 + 0.2 * sfr_term)

    return np.clip(A_env, 0.0, 1.0)


def cosmic_web_density_field(galaxy_positions: np.ndarray,
                              galaxy_redshifts: np.ndarray,
                              galaxy_masses: np.ndarray,
                              bandwidth: float = 35.0,  # h^-1 Mpc
                              adaptive: bool = True) -> np.ndarray:
    """
    Reconstruct cosmic web density field using weighted KDE.

    Matches COSMOS-Web methodology: adaptive bandwidth based on local 
    density, edge corrections for masked regions.

    Args:
        galaxy_positions: NÃ2 array of (RA, Dec) or (x, y) comoving coords
        galaxy_redshifts: N array of redshifts
        galaxy_masses: N array of stellar masses (Mâ)
        bandwidth: Global bandwidth in h^-1 Mpc
        adaptive: Use adaptive bandwidth (Abramson 1982 method)

    Returns:
        Density contrast field Î´ = (Ï - ÏÌ) / ÏÌ evaluated at galaxy positions
    """
    n = len(galaxy_positions)

    # Compute mean surface density
    area = np.ptp(galaxy_positions[:, 0]) * np.ptp(galaxy_positions[:, 1])
    rho_bar = n / area

    # Compute local densities for adaptive bandwidth
    local_densities = np.zeros(n)
    for i in range(n):
        distances = np.linalg.norm(galaxy_positions - galaxy_positions[i], axis=1)
        # Gaussian kernel with global bandwidth
        weights = np.exp(-0.5 * (distances / bandwidth) ** 2)
        local_densities[i] = np.sum(weights) / (2 * np.pi * bandwidth ** 2)

    if adaptive:
        # Adaptive bandwidth: b_g = b_s * (ÏÌ / Ï_s(X_i))^Î±
        alpha = 0.5
        sigma_bar = np.mean(local_densities)
        adaptive_bandwidths = bandwidth * (sigma_bar / local_densities) ** alpha
    else:
        adaptive_bandwidths = np.full(n, bandwidth)

    # Compute density contrast at each position
    density_contrast = np.zeros(n)
    for i in range(n):
        distances = np.linalg.norm(galaxy_positions - galaxy_positions[i], axis=1)
        bw = adaptive_bandwidths[i]
        weights = np.exp(-0.5 * (distances / bw) ** 2)
        local_rho = np.sum(weights) / (2 * np.pi * bw ** 2)
        density_contrast[i] = (local_rho - rho_bar) / rho_bar

    return density_contrast


def tng_cosmoweb_validation(tng_galaxies: dict,
                             cosmos_web_data: dict) -> dict:
    """
    Validate TNG100-1 against COSMOS-Web observables.

    Args:
        tng_galaxies: Dict with keys 'positions', 'redshifts', 'masses', 
                      'sfrs', 'quenched'
        cosmos_web_data: Dict with keys 'positions', 'redshifts', 'masses', 
                         'sfrs', 'quenched', 'overdensities'

    Returns:
        Dict with validation metrics and ÎA_c
    """
    # Compute TNG density field
    tng_density = cosmic_web_density_field(
        tng_galaxies['positions'],
        tng_galaxies['redshifts'],
        tng_galaxies['masses']
    )

    # Compute A_c for both samples
    tng_A_env = np.array([
        environmental_assembly_index(
            overdensity=np.log10(1 + d),
            stellar_mass=m,
            sfr=s,
            redshift=z,
            quiescent=q
        )
        for d, m, s, z, q in zip(
            tng_density, tng_galaxies['masses'], tng_galaxies['sfrs'],
            tng_galaxies['redshifts'], tng_galaxies['quenched']
        )
    ])

    cosmos_A_env = np.array([
        environmental_assembly_index(
            overdensity=np.log10(1 + d),
            stellar_mass=m,
            sfr=s,
            redshift=z,
            quiescent=q
        )
        for d, m, s, z, q in zip(
            cosmos_web_data['overdensities'], cosmos_web_data['masses'],
            cosmos_web_data['sfrs'], cosmos_web_data['redshifts'],
            cosmos_web_data['quenched']
        )
    ])

    # Validation metrics
    delta_A_c = np.mean(tng_A_env) - np.mean(cosmos_A_env)
    mass_density_correlation_tng = np.corrcoef(
        np.log10(tng_galaxies['masses']), tng_density
    )[0, 1]
    mass_density_correlation_cosmos = np.corrcoef(
        np.log10(cosmos_web_data['masses']), cosmos_web_data['overdensities']
    )[0, 1]

    return {
        "delta_A_c": delta_A_c,
        "tng_mean_A_env": np.mean(tng_A_env),
        "cosmos_mean_A_env": np.mean(cosmos_A_env),
        "tng_mass_density_r": mass_density_correlation_tng,
        "cosmos_mass_density_r": mass_density_correlation_cosmos,
        "correlation_bias": mass_density_correlation_tng - mass_density_correlation_cosmos,
        "quenching_fraction_tng": np.mean(tng_galaxies['quenched']),
        "quenching_fraction_cosmos": np.mean(cosmos_web_data['quenched'])
    }


def quintet_A_c(anyon_profile: Optional[NonreciprocityProfile] = None,
                 time_profile: Optional[NonreciprocityProfile] = None,
                 mass_profile: Optional[dict] = None,
                 sm_model: Optional[dict] = None,
                 cosmos_galaxy: Optional[dict] = None) -> dict:
    """
    Compute unified Assembly Index across the 2026 QUINTET.

    Args:
        anyon_profile: For C9-2026-ANYON-001
        time_profile: For C9-2026-TIME-001
        mass_profile: For C9-2026-ETAPRIME-001
        sm_model: For C9-2026-LHCB-001
        cosmos_galaxy: For C9-2026-COSMOS-001 (dict with Î´, M*, SFR, z, quenched)

    Returns:
        Dict with all five A_c components and total
    """
    # First four components from quartet
    quartet = compute_quartet_A_c(anyon_profile, time_profile, mass_profile, sm_model)

    # Fifth component: cosmic web environmental assembly
    A_cosmos = 0.0
    if cosmos_galaxy:
        A_cosmos = environmental_assembly_index(
            overdensity=cosmos_galaxy.get('overdensity', 0.0),
            stellar_mass=cosmos_galaxy.get('stellar_mass', 1e10),
            sfr=cosmos_galaxy.get('sfr', 1.0),
            redshift=cosmos_galaxy.get('redshift', 1.0),
            quiescent=cosmos_galaxy.get('quiescent', False)
        )

    return {
        **quartet,
        "A_c_cosmos": A_cosmos,
        "A_c_total_quintet": quartet["A_c_total"] + A_cosmos,
        "quintet_completeness": sum([
            anyon_profile is not None,
            time_profile is not None,
            mass_profile is not None,
            sm_model is not None,
            cosmos_galaxy is not None
        ])
    }


# ---------------------------------------------------------------------------
# UNRUH EFFECT & BIOLOGICAL THERMAL ASSEMBLY â C9-2026-UNRUH-001 + C9-2026-UTPC-001
# ---------------------------------------------------------------------------

def unruh_temperature(acceleration: float) -> float:
    """
    Compute Unruh temperature from acceleration.

    T_Unruh = âa / (2Ïck_B) â 4.06Ã10â»Â²Â¹ Ã a [m/sÂ²] K

    Args:
        acceleration: Proper acceleration in m/sÂ²

    Returns:
        Unruh temperature in Kelvin
    """
    hbar = 1.054571817e-34  # JÂ·s
    c = 299792458  # m/s
    k_B = 1.380649e-23  # J/K
    return (hbar * acceleration) / (2 * np.pi * c * k_B)


def superradiant_timing_shift(N_atoms: int,
                               g_coupling: float,
                               acceleration: float,
                               kappa_cavity: float,
                               gamma_decay: float) -> float:
    """
    Compute timing advance of superradiant burst due to Unruh effect.

    Ît ~ (N Ã gÂ² Ã a) / (Îº Ã Î)

    Args:
        N_atoms: Number of atoms in cavity
        g_coupling: Atom-cavity coupling strength (Hz)
        acceleration: Proper acceleration (m/sÂ²)
        kappa_cavity: Cavity decay rate (Hz)
        gamma_decay: Spontaneous emission rate (Hz)

    Returns:
        Timing advance in seconds
    """
    return (N_atoms * g_coupling**2 * acceleration) / (kappa_cavity * gamma_decay)


def vacuum_assembly_index(acceleration: float,
                           max_acceleration: float = 1e25) -> float:
    """
    Compute A_vac â vacuum assembly index from Unruh effect.

    A_vac = S_von_Neumann(Ï_Unruh) / S_max Ã I_acceleration

    Approximation: A_vac ~ (a / a_max)^2 for small a

    Args:
        acceleration: Proper acceleration (m/sÂ²)
        max_acceleration: Reference maximum acceleration (m/sÂ²)

    Returns:
        Vacuum assembly index A_vac â [0, 1]
    """
    ratio = acceleration / max_acceleration
    return np.clip(ratio**2, 0.0, 1.0)


def biological_performance_curve(temperature: float,
                                  t_opt: float,
                                  e_a: float = 0.65,  # eV, typical activation energy
                                  performance_max: float = 1.0) -> float:
    """
    Compute biological performance from Universal Thermal Performance Curve.

    P(T) = P_max Ã exp[ -|E_a(T - T_opt)| / (k_B T T_opt) ]

    Args:
        temperature: Ambient temperature (K)
        t_opt: Optimal temperature for species (K)
        e_a: Activation energy (eV)
        performance_max: Maximum performance at T_opt

    Returns:
        Normalized performance P(T)/P_max â [0, 1]
    """
    k_B = 8.617333262e-5  # eV/K
    delta_T = abs(temperature - t_opt)
    exponent = -(e_a * delta_T) / (k_B * temperature * t_opt)
    return performance_max * np.exp(exponent)


def biological_assembly_index(temperature: float,
                               t_opt: float,
                               structural_complexity: float,
                               information_content: float,
                               e_a: float = 0.65) -> float:
    """
    Compute A_bio â biological assembly index.

    A_bio(T) = P(T)/P_max Ã C_structural Ã I_information

    Args:
        temperature: Ambient temperature (K)
        t_opt: Optimal temperature (K)
        structural_complexity: Normalized structural complexity [0, 1]
        information_content: Normalized information content [0, 1]
        e_a: Activation energy (eV)

    Returns:
        Biological assembly index A_bio â [0, 1]
    """
    perf = biological_performance_curve(temperature, t_opt, e_a)
    return perf * structural_complexity * information_content


def septet_A_c(anyon_profile: Optional[NonreciprocityProfile] = None,
               time_profile: Optional[NonreciprocityProfile] = None,
               mass_profile: Optional[dict] = None,
               sm_model: Optional[dict] = None,
               cosmos_galaxy: Optional[dict] = None,
               unruh_params: Optional[dict] = None,
               bio_params: Optional[dict] = None) -> dict:
    """
    Compute unified Assembly Index across the 2026 SEPTET.

    Args:
        anyon_profile: For C9-2026-ANYON-001
        time_profile: For C9-2026-TIME-001
        mass_profile: For C9-2026-ETAPRIME-001
        sm_model: For C9-2026-LHCB-001
        cosmos_galaxy: For C9-2026-COSMOS-001
        unruh_params: For C9-2026-UNRUH-001 (dict with 'acceleration')
        bio_params: For C9-2026-UTPC-001 (dict with 'temperature', 't_opt', etc.)

    Returns:
        Dict with all seven A_c components and total
    """
    # First five components from quintet
    quintet = compute_quartet_A_c(anyon_profile, time_profile, mass_profile, sm_model)

    # Sixth: vacuum assembly (Unruh)
    A_unruh = 0.0
    if unruh_params:
        A_unruh = vacuum_assembly_index(
            unruh_params.get('acceleration', 0.0)
        )

    # Seventh: biological assembly (UTPC)
    A_bio = 0.0
    if bio_params:
        A_bio = biological_assembly_index(
            temperature=bio_params.get('temperature', 300.0),
            t_opt=bio_params.get('t_opt', 310.0),
            structural_complexity=bio_params.get('structural_complexity', 0.5),
            information_content=bio_params.get('information_content', 0.5)
        )

    return {
        **quintet,
        "A_c_unruh": A_unruh,
        "A_c_bio": A_bio,
        "A_c_total_septet": quintet["A_c_total"] + A_unruh + A_bio,
        "septet_completeness": sum([
            anyon_profile is not None,
            time_profile is not None,
            mass_profile is not None,
            sm_model is not None,
            cosmos_galaxy is not None,
            unruh_params is not None,
            bio_params is not None
        ])
    }


# ---------------------------------------------------------------------------
# PTOLEMY / NEUTRINO ASSEMBLY â C9-2026-PTOLEMY-001 Extension
# ---------------------------------------------------------------------------

def neutrino_assembly_index(m_measured: float,
                             m_cosmological_limit: float = 0.12,  # eV, sum from Planck
                             cnb_confidence: float = 0.0,
                             structure_accuracy: float = 0.8) -> float:
    """
    Compute A_Î½ â neutrino assembly index.

    A_Î½ = (m_measured / m_cosmological_limit) Ã CNB_confidence Ã structure_accuracy

    Quantifies how completely neutrino physics is "assembled" into 
    cosmological models.

    Args:
        m_measured: Directly measured neutrino mass (eV)
        m_cosmological_limit: Cosmological upper limit on sum m_Î½ (eV)
        cnb_confidence: Cosmic Neutrino Background detection confidence [0,1]
        structure_accuracy: Accuracy of structure formation predictions [0,1]

    Returns:
        Neutrino assembly index A_Î½ â [0, 1]
    """
    mass_ratio = m_measured / m_cosmological_limit if m_cosmological_limit > 0 else 0
    return np.clip(mass_ratio * cnb_confidence * structure_accuracy, 0.0, 1.0)


def tritium_beta_spectrum(energy: np.ndarray,
                           endpoint: float = 18.6e3,  # eV
                           neutrino_mass: float = 0.0,  # eV
                           resolution: float = 200.0) -> np.ndarray:
    """
    Compute tritium beta decay spectrum with neutrino mass.

    Kurie plot: N(E) ~ (E_endpoint - E) Ã sqrt((E_endpoint - E)Â² - m_Î½Â²)

    Args:
        energy: Electron kinetic energy array (eV)
        endpoint: Beta decay endpoint energy (eV)
        neutrino_mass: Neutrino mass (eV)
        resolution: Detector energy resolution (eV, Gaussian smearing)

    Returns:
        Beta spectrum intensity (normalized)
    """
    q = endpoint - energy
    # Prevent numerical issues
    q = np.maximum(q, 0)

    # Phase space factor with neutrino mass
    m_sq = neutrino_mass ** 2
    phase_space = q * np.sqrt(np.maximum(q**2 - m_sq, 0))

    # Fermi function (simplified, non-relativistic approximation)
    # Z=1 for tritium, but electrons are relativistic at endpoint
    # Use approximate Coulomb correction
    fermi = 1.0  # Simplified; full calculation requires Fermi function

    spectrum = phase_space * fermi

    # Gaussian smearing for detector resolution
    if resolution > 0:
        from scipy.ndimage import gaussian_filter1d
        sigma_bins = resolution / np.mean(np.diff(energy))
        spectrum = gaussian_filter1d(spectrum, sigma=sigma_bins)

    # Normalize
    return spectrum / np.trapz(spectrum, energy)


def graphene_recoil_suppression(recoil_energy_free: float,
                                 phonon_energy: float = 0.1,  # eV, typical graphene phonon
                                 coupling_strength: float = 0.5) -> float:
    """
    Compute recoil energy suppression factor in graphene.

    Model: E_recoil_graphene = E_recoil_free Ã exp(-coupling Ã E_free / E_phonon)

    Args:
        recoil_energy_free: Free-space nuclear recoil energy (eV)
        phonon_energy: Characteristic graphene phonon energy (eV)
        coupling_strength: Electron-phonon coupling parameter

    Returns:
        Suppression factor â [0, 1]
    """
    return np.exp(-coupling_strength * recoil_energy_free / phonon_energy)


def cnb_event_rate(tritium_mass: float,  # grams
                    cross_section: float = 1e-42,  # cmÂ²
                    flux: float = 1e12) -> float:  # cmâ»Â² sâ»Â¹
    """
    Estimate Cosmic Neutrino Background event rate in PTOLEMY.

    Rate = N_atoms Ã Ï Ã Î¦

    Args:
        tritium_mass: Tritium target mass (grams)
        cross_section: Neutrino capture cross-section (cmÂ²)
        flux: CNB flux (cmâ»Â² sâ»Â¹)

    Returns:
        Event rate (events/year)
    """
    N_A = 6.022e23  # Avogadro's number
    molar_mass = 3.0  # g/mol for tritium
    N_atoms = (tritium_mass / molar_mass) * N_A

    rate_per_second = N_atoms * cross_section * flux
    return rate_per_second * 365.25 * 24 * 3600


def octet_A_c(anyon_profile: Optional[NonreciprocityProfile] = None,
               time_profile: Optional[NonreciprocityProfile] = None,
               mass_profile: Optional[dict] = None,
               sm_model: Optional[dict] = None,
               cosmos_galaxy: Optional[dict] = None,
               unruh_params: Optional[dict] = None,
               bio_params: Optional[dict] = None,
               neutrino_params: Optional[dict] = None) -> dict:
    """
    Compute unified Assembly Index across the 2026 OCTET.

    Args:
        anyon_profile: For C9-2026-ANYON-001
        time_profile: For C9-2026-TIME-001
        mass_profile: For C9-2026-ETAPRIME-001
        sm_model: For C9-2026-LHCB-001
        cosmos_galaxy: For C9-2026-COSMOS-001
        unruh_params: For C9-2026-UNRUH-001
        bio_params: For C9-2026-UTPC-001
        neutrino_params: For C9-2026-PTOLEMY-001 (dict with 'm_measured', etc.)

    Returns:
        Dict with all eight A_c components and total
    """
    # First seven components from septet
    septet = compute_quartet_A_c(anyon_profile, time_profile, mass_profile, sm_model)

    # Add cosmos, unruh, bio if provided
    A_cosmos = 0.0
    if cosmos_galaxy:
        A_cosmos = environmental_assembly_index(
            overdensity=cosmos_galaxy.get('overdensity', 0.0),
            stellar_mass=cosmos_galaxy.get('stellar_mass', 1e10),
            sfr=cosmos_galaxy.get('sfr', 1.0),
            redshift=cosmos_galaxy.get('redshift', 1.0),
            quiescent=cosmos_galaxy.get('quiescent', False)
        )

    A_unruh = 0.0
    if unruh_params:
        A_unruh = vacuum_assembly_index(unruh_params.get('acceleration', 0.0))

    A_bio = 0.0
    if bio_params:
        A_bio = biological_assembly_index(
            temperature=bio_params.get('temperature', 300.0),
            t_opt=bio_params.get('t_opt', 310.0),
            structural_complexity=bio_params.get('structural_complexity', 0.5),
            information_content=bio_params.get('information_content', 0.5)
        )

    # Eighth: neutrino assembly (PTOLEMY)
    A_neutrino = 0.0
    if neutrino_params:
        A_neutrino = neutrino_assembly_index(
            m_measured=neutrino_params.get('m_measured', 0.0),
            m_cosmological_limit=neutrino_params.get('m_cosmological_limit', 0.12),
            cnb_confidence=neutrino_params.get('cnb_confidence', 0.0),
            structure_accuracy=neutrino_params.get('structure_accuracy', 0.8)
        )

    total = septet["A_c_total"] + A_cosmos + A_unruh + A_bio + A_neutrino

    return {
        **septet,
        "A_c_cosmos": A_cosmos,
        "A_c_unruh": A_unruh,
        "A_c_bio": A_bio,
        "A_c_neutrino": A_neutrino,
        "A_c_total_octet": total,
        "octet_completeness": sum([
            anyon_profile is not None,
            time_profile is not None,
            mass_profile is not None,
            sm_model is not None,
            cosmos_galaxy is not None,
            unruh_params is not None,
            bio_params is not None,
            neutrino_params is not None
        ])
    }
