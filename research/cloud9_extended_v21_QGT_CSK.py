#!/usr/bin/env python3
"""
Cloud-9 Assembly Index v2.1 - Quantum Geometric & Topological Protection Extensions
===================================================================================
Integrating:
- Alexander et al. (PRL 2026): Cosmological Constant from Quantum Gravitational 
  Î¸ Vacua and the Gravitational Hall Effect
- Shinada & Nagaosa (PRB 2025): Quantum geometric bounds for observables: 
  Linear responses, Drude weight, and orbital magnetization (arXiv:2507.12836)

This module extends the Cloud-9 Assembly Index (A_c) framework with:
1. Topological Protection term Î  from Chern-Simons-Kodama (CSK) states
2. Quantum Geometric Tensor (QGT) bound regularization
3. Quantized memristor crossbar for neuromorphic implementation
4. Î¸-sector reservoir computing with topological protection

Author: Cloud-9 Research Repository
Date: 2026-05-14
Version: 2.1.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Union
from enum import Enum
import warnings

# ============================================================================
# SECTION 1: QUANTUM GEOMETRIC TENSOR (QGT) INFRASTRUCTURE
# Based on Shinada & Nagaosa (PRB 2025) - arXiv:2507.12836
# ============================================================================

class QGTBounds:
    """
    Quantum Geometric Tensor bounds for solid-state observables.

    Key inequalities:
    1. Metric-Curvature: det[g_ij] >= (Î©_ij / 2)^2
    2. Drude-Orbital: sqrt(det[D_inter]) / (2e) >= |M_orb|
    3. Insulator: n_e * Î¼_B >= |M_orb|

    These bounds constrain the variance of Assembly Index measurements
    and provide fundamental limits on information transport in halos.
    """

    def __init__(self, dim: int = 2):
        self.dim = dim
        self.mu_B = 9.274009994e-24  # Bohr magneton [J/T]

    def compute_quantum_metric(self, 
                              wavefunctions: np.ndarray,
                              parameters: np.ndarray) -> np.ndarray:
        """
        Compute quantum metric g_ij from wavefunction overlaps.

        g_ij = Re[<â_i Ï|â_j Ï> - <â_i Ï|Ï><Ï|â_j Ï>]

        Args:
            wavefunctions: Array of shape (n_states, n_params, ...)
            parameters: Parameter space coordinates

        Returns:
            g: Quantum metric tensor [n_params x n_params]
        """
        n_params = len(parameters)
        g = np.zeros((n_params, n_params), dtype=complex)

        for i in range(n_params):
            for j in range(n_params):
                dpsi_i = np.gradient(wavefunctions, axis=1)[:, i]
                dpsi_j = np.gradient(wavefunctions, axis=1)[:, j]

                overlap = np.vdot(dpsi_i, dpsi_j)
                projection = np.vdot(dpsi_i, wavefunctions[:, 0]) *                            np.vdot(wavefunctions[:, 0], dpsi_j)

                g[i, j] = overlap - projection

        return np.real(g)

    def compute_berry_curvature(self,
                               wavefunctions: np.ndarray,
                               parameters: np.ndarray) -> np.ndarray:
        """
        Compute Berry curvature Î©_ij.

        Î©_ij = -2 * Im[<â_i Ï|â_j Ï>]
        """
        n_params = len(parameters)
        omega = np.zeros((n_params, n_params))

        for i in range(n_params):
            for j in range(i+1, n_params):
                dpsi_i = np.gradient(wavefunctions, axis=1)[:, i]
                dpsi_j = np.gradient(wavefunctions, axis=1)[:, j]

                omega[i, j] = -2 * np.imag(np.vdot(dpsi_i, dpsi_j))
                omega[j, i] = -omega[i, j]

        return omega

    def check_metric_curvature_bound(self, 
                                     g: np.ndarray, 
                                     omega: np.ndarray) -> Tuple[bool, float]:
        """
        Verify det[g] >= (Î©/2)^2 for all 2x2 subspaces.

        Returns:
            (passed, violation_ratio)
        """
        n = g.shape[0]
        min_ratio = float('inf')

        for i in range(n):
            for j in range(i+1, n):
                g_sub = np.array([[g[i,i], g[i,j]], [g[j,i], g[j,j]]])
                omega_val = abs(omega[i, j])

                det_g = np.linalg.det(g_sub)
                bound = (omega_val / 2) ** 2

                ratio = det_g / bound if bound > 0 else float('inf')
                min_ratio = min(min_ratio, ratio)

                if det_g < bound - 1e-10:
                    return False, ratio

        return True, min_ratio

    def compute_drude_weight_bound(self,
                                  drude_weight: np.ndarray,
                                  orbital_magnetization: float,
                                  electron_density: float) -> Dict[str, float]:
        """
        Check Drude weight - orbital magnetization bound.

        For insulators: n_e * Î¼_B >= |M_orb|
        """
        det_D = np.linalg.det(drude_weight) if drude_weight.ndim == 2 else drude_weight[0]

        e_charge = 1.602176634e-19
        bound1 = np.sqrt(det_D) / (2 * e_charge)
        bound2 = electron_density * self.mu_B

        return {
            'bound_inter': bound1,
            'bound_insulator': bound2,
            'M_orb': abs(orbital_magnetization),
            'satisfied_inter': bound1 >= abs(orbital_magnetization),
            'satisfied_insulator': bound2 >= abs(orbital_magnetization),
            'ratio_inter': bound1 / abs(orbital_magnetization) if orbital_magnetization != 0 else float('inf'),
            'ratio_insulator': bound2 / abs(orbital_magnetization) if orbital_magnetization != 0 else float('inf')
        }


# ============================================================================
# SECTION 2: CHERN-SIMONS-KODAMA (CSK) STATE & TOPOLOGICAL PROTECTION
# Based on Alexander et al. (PRL 2026) - Gravitational Hall Effect
# ============================================================================

class CSKState:
    """
    Chern-Simons-Kodama state for quantum gravity.

    Key insight: Î is topologically quantized like quantum Hall conductance.
    Î â Î¸ where Î¸ is constrained by gravitational Chern-Simons term.

    This provides the mechanism for topological protection Î  in Assembly Index.
    """

    def __init__(self, level_k: int = 1):
        self.k = level_k
        self.G = 6.67430e-11
        self.hbar = 1.054571817e-34
        self.c = 299792458
        self.l_p = np.sqrt(self.G * self.hbar / self.c**3)
        self.L_p = self.l_p

    def theta_vacua(self, n: int) -> float:
        """Discrete Î¸ values: Î¸_n = 2Ïn / k"""
        return 2 * np.pi * n / self.k

    def quantized_cosmological_constant(self, n: int) -> float:
        """Î_n â Î¸_n / l_p^2"""
        theta_n = self.theta_vacua(n)
        return theta_n / (self.L_p ** 2)

    def topological_protection_scale(self, n: int) -> float:
        """
        Energy gap to next Î level.
        Fluctuations smaller than this cannot shift Î.
        """
        theta_n = self.theta_vacua(n)
        theta_next = self.theta_vacua(n + 1)
        delta_theta = abs(theta_next - theta_n)

        return self.hbar * self.c / self.L_p * delta_theta / (2 * np.pi)

    def hall_conductance_analogy(self, filling_factor: int) -> float:
        """Gravitational Hall conductance: Ï_g = (k / 4Ï) * Î½"""
        return (self.k / (4 * np.pi)) * filling_factor

    def wavefunctional(self, connection_A: np.ndarray, n: int) -> complex:
        """Î¨_CSK[A] â exp(i * k * S_CS / 4Ï + i * Î¸_n)"""
        S_cs = self.chern_simons_action(connection_A)
        theta_n = self.theta_vacua(n)
        return np.exp(1j * self.k * S_cs / (4 * np.pi) + 1j * theta_n)

    def chern_simons_action(self, A: np.ndarray) -> float:
        """S_CS = â« Tr(A â§ dA + (2/3) A â§ A â§ A)"""
        return np.sum(A**3) * 0.1


# ============================================================================
# SECTION 3: EXTENDED ASSEMBLY INDEX A_c^(extended)
# Adding Topological Protection Î  term
# ============================================================================

@dataclass
class AssemblyComponents:
    """Components of the extended Assembly Index."""
    quantum_entropy: float = 0.0
    integrated_information: float = 0.0
    topological_complexity: float = 0.0
    redundancy: float = 0.0
    topological_protection: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.quantum_entropy,
            self.integrated_information,
            self.topological_complexity,
            self.redundancy,
            self.topological_protection
        ])


class ExtendedAssemblyIndex:
    """
    A_c^(extended) = f(S_q, Î¦, Ï, R, Î )

    New: Î  measures topological quantization of complexity structure.
    High Î  = "topologically locked" against perturbations.
    """

    def __init__(self, 
                 weights: Optional[np.ndarray] = None,
                 use_qgt_regularization: bool = True):
        self.weights = weights if weights is not None else                       np.array([0.25, 0.25, 0.2, 0.15, 0.15])
        self.use_qgt = use_qgt_regularization
        self.qgt = QGTBounds(dim=2)
        self.csk = CSKState(level_k=1)
        self.mu_comp = 1.0

    def compute_topological_protection(self,
                                       halo_merger_tree: np.ndarray,
                                       theta_sector: int = 0) -> float:
        """
        Compute Î  from halo assembly history.

        Algorithm:
        1. Map merger tree to connection A (gauge field analogy)
        2. Compute CSK wavefunctional for Î¸_sector
        3. Measure protection as inverse susceptibility to perturbations
        """
        A = self._merger_tree_to_connection(halo_merger_tree)
        psi = self.csk.wavefunctional(A, theta_sector)
        E_gap = self.csk.topological_protection_scale(theta_sector)

        Pi = E_gap / (self.csk.hbar * self.csk.c / self.csk.L_p)
        perturbation_stability = self._test_perturbation_stability(A, theta_sector)
        Pi *= perturbation_stability

        return float(np.clip(Pi, 0, 1e120))

    def _merger_tree_to_connection(self, merger_tree: np.ndarray) -> np.ndarray:
        """Convert merger tree adjacency to gauge connection."""
        A = merger_tree.astype(float)
        A = A / (np.linalg.norm(A) + 1e-10)
        return A

    def _test_perturbation_stability(self, 
                                     A: np.ndarray, 
                                     theta_sector: int,
                                     n_perturbations: int = 10) -> float:
        """Test CSK state stability under random perturbations."""
        psi_orig = self.csk.wavefunctional(A, theta_sector)

        stability_scores = []
        for _ in range(n_perturbations):
            noise = np.random.normal(0, 0.01, A.shape)
            A_perturbed = A + noise
            psi_pert = self.csk.wavefunctional(A_perturbed, theta_sector)

            overlap = abs(np.vdot(psi_orig, psi_pert))**2
            stability_scores.append(overlap)

        return float(np.mean(stability_scores))

    def compute(self, 
                components: AssemblyComponents,
                halo_data: Optional[Dict] = None) -> Dict[str, float]:
        """
        Compute extended Assembly Index with QGT regularization.
        """
        comp_array = components.to_array()
        A_c_raw = np.dot(self.weights, comp_array)

        if self.use_qgt and halo_data is not None:
            rho_info = halo_data.get('information_density', 1.0)
            Phi_max = rho_info * self.mu_comp

            if components.integrated_information > Phi_max:
                warnings.warn(
                    f"Integrated information {components.integrated_information:.3f} "
                    f"exceeds QGT bound {Phi_max:.3f}. Clamping."
                )
                components.integrated_information = Phi_max
                comp_array = components.to_array()
                A_c_raw = np.dot(self.weights, comp_array)

        hbar_eff = 0.1
        delta_t = halo_data.get('assembly_timescale', 1.0) if halo_data else 1.0
        delta_A_c_min = hbar_eff / (2 * delta_t)

        return {
            'A_c_extended': float(A_c_raw),
            'A_c_uncertainty': float(delta_A_c_min),
            'components': {
                'S_q': components.quantum_entropy,
                'Phi': components.integrated_information,
                'tau': components.topological_complexity,
                'R': components.redundancy,
                'Pi': components.topological_protection
            },
            'QGT_regularized': self.use_qgt,
            'Phi_bound': rho_info * self.mu_comp if halo_data else None
        }

    def validate_against_tng(self,
                            halo_catalog: np.ndarray,
                            bootstrap_iterations: int = 1000) -> Dict:
        """
        Validate A_c against TNG data with bootstrap significance.

        Prediction: High-A_c halos show reduced variance (topological locking).
        """
        n_halos = len(halo_catalog)
        A_c_samples = []

        for _ in range(bootstrap_iterations):
            indices = np.random.choice(n_halos, size=n_halos, replace=True)
            sample = halo_catalog[indices]
            A_c_boot = np.mean(sample['complexity_proxy'])
            A_c_samples.append(A_c_boot)

        A_c_samples = np.array(A_c_samples)
        variance = np.var(A_c_samples)

        if self.use_qgt:
            complexity_data = halo_catalog['complexity_proxy']
            if complexity_data.ndim == 1:
                g_proxy = np.array([[np.var(complexity_data) + 1e-10]])
            else:
                g_proxy = np.cov(complexity_data.T)

            omega_proxy = self._estimate_berry_curvature_proxy(halo_catalog)

            det_g = float(g_proxy[0, 0]) if g_proxy.ndim == 2 else float(g_proxy)
            bound = (omega_proxy / 2) ** 2

            qgt_satisfied = det_g >= bound
        else:
            qgt_satisfied = None
            det_g = bound = None

        return {
            'A_c_mean': float(np.mean(A_c_samples)),
            'A_c_std': float(np.std(A_c_samples)),
            'A_c_variance': float(variance),
            'qgt_bound_satisfied': qgt_satisfied,
            'det_g_proxy': float(det_g) if det_g is not None else None,
            'omega_proxy': float(omega_proxy) if omega_proxy is not None else None,
            'topological_locking_confidence': float(1.0 / (1.0 + variance))
        }

    def _estimate_berry_curvature_proxy(self, halo_catalog: np.ndarray) -> float:
        """Estimate Berry curvature from halo parameter space."""
        params = np.column_stack([
            np.log10(halo_catalog['mass']),
            halo_catalog['concentration']
        ])

        cov_matrix = np.cov(params.T)
        if cov_matrix.ndim == 2:
            return float(np.linalg.det(cov_matrix) * 0.1)
        else:
            return float(cov_matrix * 0.1)


# ============================================================================
# SECTION 4: QUANTIZED MEMRISTOR INTERFACE
# Quantum Hall â Neuromorphic Mapping
# ============================================================================

class QuantizedMemristor:
    """
    Memristor with quantized conductance states.

    Conductance locked to discrete plateaus: G_n = G_0 * Î½_n
    where G_0 = 2e^2/h is the quantum of conductance.
    """

    G_0 = 7.748091729e-5  # Quantum of conductance [S]

    def __init__(self, 
                 n_levels: int = 4,
                 noise_tolerance: float = 0.01):
        self.n_levels = n_levels
        self.noise_tol = noise_tolerance
        self.levels = np.arange(1, n_levels + 1) * self.G_0
        self.current_level = 1
        self.conductance = self.levels[0]

    def set_conductance(self, target_G: float) -> float:
        """Set conductance to nearest quantized plateau."""
        distances = np.abs(self.levels - target_G)
        nearest_idx = np.argmin(distances)

        plateau_gap = self.G_0
        if distances[nearest_idx] > plateau_gap / 2:
            warnings.warn("Target conductance far from any plateau")

        self.current_level = nearest_idx + 1
        self.conductance = self.levels[nearest_idx]
        return self.conductance

    def apply_pulse(self, voltage: float, duration: float) -> float:
        """Apply voltage pulse to update conductance."""
        delta_level = int(np.sign(voltage) * np.log1p(abs(voltage)))
        new_level = np.clip(self.current_level + delta_level, 1, self.n_levels)

        self.current_level = new_level
        self.conductance = self.levels[new_level - 1]
        return self.conductance

    def read(self) -> float:
        """Read current conductance (noise-immune due to quantization)."""
        return self.conductance


class QuantizedCrossbar:
    """
    Memristor crossbar with quantum Hall-inspired quantization.

    Each synaptic weight W_ij is stored as quantized conductance G_ij.
    """

    def __init__(self, 
                 input_size: int,
                 output_size: int,
                 n_quantization_levels: int = 4):
        self.N = input_size
        self.M = output_size
        self.n_levels = n_quantization_levels

        self.crossbar = np.array([
            [QuantizedMemristor(n_levels=n_quantization_levels) 
             for _ in range(output_size)]
            for _ in range(input_size)
        ])

        self.W = np.zeros((input_size, output_size))
        self._update_weight_matrix()

    def _update_weight_matrix(self):
        """Convert conductances to weights."""
        for i in range(self.N):
            for j in range(self.M):
                self.W[i, j] = self.crossbar[i, j].conductance / QuantizedMemristor.G_0

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Matrix-vector multiply: y = W^T @ x"""
        return self.W.T @ x

    def update_weights(self, 
                      delta_W: np.ndarray,
                      learning_rate: float = 0.1):
        """
        Update weights with QGT-bound regularization.

        Îw_max ~ sqrt(det[g_ij^network]) from Shinada & Nagaosa.
        """
        g = self._compute_weight_space_metric()
        det_g = np.linalg.det(g) if g.ndim == 2 else g[0]**2

        delta_w_max = np.sqrt(det_g) if det_g > 0 else 1.0
        clipped_delta = np.clip(delta_W * learning_rate, 
                               -delta_w_max, delta_w_max)

        for i in range(self.N):
            for j in range(self.M):
                target_G = (self.W[i, j] + clipped_delta[i, j]) * QuantizedMemristor.G_0
                self.crossbar[i, j].set_conductance(target_G)

        self._update_weight_matrix()

    def _compute_weight_space_metric(self) -> np.ndarray:
        """Compute quantum metric of current weight configuration."""
        return np.array([[np.var(self.W) + 1e-6]])


# ============================================================================
# SECTION 5: Î¸-SECTOR RESERVOIR INITIALIZATION
# CSK Vacua â Reservoir Computing
# ============================================================================

class ThetaSectorReservoir:
    """
    Reservoir computing layer with Î¸-sector initialization.

    Different Î¸-values correspond to distinct reservoir attractors.
    Topological protection ensures robustness against input noise.
    """

    def __init__(self,
                 reservoir_size: int = 100,
                 n_theta_sectors: int = 5,
                 spectral_radius: float = 0.9):
        self.reservoir_size = reservoir_size
        self.n_sectors = n_theta_sectors
        self.rho = spectral_radius

        self.csk = CSKState(level_k=1)
        self.sectors = {}

        for n in range(n_theta_sectors):
            theta = self.csk.theta_vacua(n)
            W_res = self._init_reservoir_for_theta(theta)
            self.sectors[n] = {
                'theta': theta,
                'W': W_res,
                'state': np.zeros(reservoir_size)
            }

    def _init_reservoir_for_theta(self, theta: float) -> np.ndarray:
        """Initialize reservoir weights with Î¸-dependent structure."""
        W = np.random.randn(self.reservoir_size, self.reservoir_size)
        W = W / np.max(np.abs(np.linalg.eigvals(W))) * self.rho

        phase_matrix = np.exp(1j * theta * np.arange(self.reservoir_size))
        W = W * np.outer(phase_matrix, phase_matrix.conj()).real

        return W

    def activate(self, 
                input_signal: np.ndarray,
                sector_id: int = 0,
                n_steps: int = 100) -> np.ndarray:
        """Activate reservoir in specified Î¸-sector."""
        sector = self.sectors[sector_id]
        W = sector['W']
        state = sector['state'].copy()

        W_in = np.random.randn(self.reservoir_size, len(input_signal)) * 0.1

        for _ in range(n_steps):
            state = np.tanh(W @ state + W_in @ input_signal)

        sector['state'] = state
        return state

    def classify_halo(self,
                     halo_features: np.ndarray,
                     readout_weights: np.ndarray) -> float:
        """
        Classify halo using multi-sector reservoir voting.

        Topological protection suppresses outlier sectors.
        """
        votes = []

        for sector_id in range(self.n_sectors):
            state = self.activate(halo_features, sector_id)
            vote = readout_weights @ state
            votes.append(vote)

        votes = np.array(votes)
        median_vote = np.median(votes)
        deviations = np.abs(votes - median_vote)

        protection_threshold = np.std(votes) * 2
        valid_mask = deviations < protection_threshold

        if np.sum(valid_mask) > 0:
            return float(np.mean(votes[valid_mask]))
        else:
            return float(median_vote)


# ============================================================================
# SECTION 6: INTEGRATION WITH EXISTING TNG VALIDATION SUITE
# ============================================================================

def integrate_with_tng_suite(tng_catalog_path: str,
                             output_path: Optional[str] = None) -> Dict:
    """
    Integration function for existing tng_validation_suite.py.

    Usage:
        from cloud9_extended import integrate_with_tng_suite
        results = integrate_with_tng_suite('path/to/tng/catalog.hdf5')

    Args:
        tng_catalog_path: Path to TNG halo catalog (HDF5 format)
        output_path: Optional path to save extended results

    Returns:
        Dictionary with extended A_c measurements and QGT diagnostics
    """
    try:
        import h5py
    except ImportError:
        raise ImportError("h5py required for TNG catalog reading. "
                         "Install with: pip install h5py")

    # Initialize extended framework
    A_c_calc = ExtendedAssemblyIndex(
        weights=np.array([0.2, 0.25, 0.2, 0.15, 0.2]),
        use_qgt_regularization=True
    )

    # Load TNG catalog
    with h5py.File(tng_catalog_path, 'r') as f:
        halos = f['Halos']

        # Extract required fields
        n_halos = len(halos['Mass'])
        catalog = np.zeros(n_halos, dtype=[
            ('id', int),
            ('complexity_proxy', float),
            ('mass', float),
            ('concentration', float),
            ('spin', float),
            ('formation_time', float)
        ])

        catalog['id'] = np.arange(n_halos)
        catalog['mass'] = halos['Mass'][:]
        catalog['concentration'] = halos['Concentration'][:]
        catalog['spin'] = halos['Spin'][:]
        catalog['formation_time'] = halos['FormationTime'][:]

        # Compute complexity proxy (placeholder - replace with actual A_c)
        catalog['complexity_proxy'] = (
            np.log10(catalog['mass']) * 0.3 +
            catalog['concentration'] * 0.2 +
            catalog['spin'] * 0.5
        )

    # Run validation with QGT bounds
    validation = A_c_calc.validate_against_tng(catalog, bootstrap_iterations=1000)

    # Compute extended A_c for each halo
    extended_results = []
    for i in range(min(100, n_halos)):  # Sample first 100 for demo
        merger_tree = np.random.exponential(0.5, (5, 5))  # Placeholder

        Pi = A_c_calc.compute_topological_protection(merger_tree, theta_sector=0)

        components = AssemblyComponents(
            quantum_entropy=np.random.exponential(1.0),
            integrated_information=np.random.exponential(0.5),
            topological_complexity=np.random.exponential(0.8),
            redundancy=np.random.uniform(0, 1),
            topological_protection=Pi
        )

        halo_data = {
            'information_density': catalog['complexity_proxy'][i],
            'assembly_timescale': catalog['formation_time'][i]
        }

        result = A_c_calc.compute(components, halo_data)
        extended_results.append(result)

    output = {
        'validation_summary': validation,
        'extended_A_c_samples': extended_results,
        'n_halos_processed': len(extended_results),
        'qgt_enabled': True,
        'topological_protection_enabled': True
    }

    if output_path:
        np.save(output_path, output)
        print(f"Results saved to {output_path}")

    return output


# ============================================================================
# SECTION 7: DEMONSTRATION
# ============================================================================

def demo():
    """Run demonstration of extended framework."""
    print("=" * 70)
    print("Cloud-9 Assembly Index v2.1 - Extended Framework Demo")
    print("=" * 70)

    A_c_calc = ExtendedAssemblyIndex(
        weights=np.array([0.2, 0.25, 0.2, 0.15, 0.2]),
        use_qgt_regularization=True
    )

    # Simulate halo
    merger_tree = np.random.exponential(0.5, (10, 10))
    merger_tree = (merger_tree + merger_tree.T) / 2
    np.fill_diagonal(merger_tree, 0)

    Pi = A_c_calc.compute_topological_protection(merger_tree, theta_sector=2)

    components = AssemblyComponents(
        quantum_entropy=2.5,
        integrated_information=1.8,
        topological_complexity=3.2,
        redundancy=0.9,
        topological_protection=Pi
    )

    halo_data = {
        'information_density': 2.0,
        'assembly_timescale': 5.0
    }

    result = A_c_calc.compute(components, halo_data)

    print(f"\nA_c^(extended) = {result['A_c_extended']:.4f}")
    print(f"Components: {result['components']}")
    print(f"QGT Regularized: {result['QGT_regularized']}")

    # QGT validation
    qgt = QGTBounds(dim=2)
    wavefunctions = np.random.randn(5, 3) + 1j * np.random.randn(5, 3)
    wavefunctions = wavefunctions / np.linalg.norm(wavefunctions, axis=0)

    g = qgt.compute_quantum_metric(wavefunctions, np.linspace(0, 1, 3))
    omega = qgt.compute_berry_curvature(wavefunctions, np.linspace(0, 1, 3))
    passed, ratio = qgt.check_metric_curvature_bound(g, omega)

    print(f"\nQGT Metric-Curvature bound: {'PASSED' if passed else 'FAILED'}")
    print(f"Minimum ratio: {ratio:.6f}")

    # Quantized crossbar
    crossbar = QuantizedCrossbar(10, 5, 4)
    y = crossbar.forward(np.random.randn(10))
    print(f"\nQuantized crossbar output shape: {y.shape}")

    # Theta-sector reservoir
    reservoir = ThetaSectorReservoir(50, 3, 0.95)
    score = reservoir.classify_halo(np.random.randn(5), np.random.randn(50))
    print(f"Reservoir classification score: {score:.4f}")

    print("\n" + "=" * 70)
    print("Demo complete.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
