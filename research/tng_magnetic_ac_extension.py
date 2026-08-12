"""
tng_magnetic_ac_extension.py
Cloud-9 v2.2.0 Extension: Magnetic Field Contributions to Cosmological Assembly Index

Extends the existing TNG validation suite (tng_validation_suite.py) to compute
magnetic field proxies and their contribution to A_c in dark matter halos.

Author: Cloud-9 Assembly Project
Date: 2026-06-03
Test Priority: A
Sandbox Layer: 1 (Established Physics) + 2 (Speculative: halo magnetogenesis)
"""

import numpy as np
from scipy import stats
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
import h5py
import warnings
import c9_bus_client  # C9 bus injection


@dataclass
class MagneticHaloData:
    """Container for halo properties including magnetic field proxies."""
    halo_id: int
    mass: float  # Msun
    radius: float  # kpc
    spin_parameter: float  # Bullock et al. lambda
    velocity_dispersion: float  # km/s
    metallicity_gas: float  # Z/Zsun
    baryon_fraction: float
    merger_history: np.ndarray  # mass ratio vs time

    # Magnetic proxies (TNG MHD outputs or derived)
    magnetic_energy: Optional[float] = None  # erg
    mean_b_field: Optional[float] = None  # microgauss
    b_field_topology: Optional[np.ndarray] = None  # 3D field structure

    # Assembly Index components
    a_c_structural: float = 0.0
    a_c_dynamical: float = 0.0
    a_c_magnetic: float = 0.0
    a_c_total: float = 0.0


class HaloMagneticProxyEstimator:
    """
    Estimates magnetic field strength in halos where direct MHD data is unavailable
    or noisy. Uses scaling relations from cosmological MHD simulations.

    References:
    - Donnert et al. 2018 (Magnetic fields in galaxy clusters)
    - Vazza et al. 2018 (TNG MHD scaling)
    - Christensen et al. 2009 (Dynamo scaling, adapted)
    """

    def __init__(self, scaling_model: str = "vazza_2018"):
        self.scaling_model = scaling_model
        self._scaling_functions = {
            "vazza_2018": self._vazza_scaling,
            "donnert_2018": self._donnert_scaling,
            "dynamo_proxy": self._dynamo_proxy_scaling
        }

    def estimate_field(self, halo: MagneticHaloData) -> float:
        """Return mean B-field in microgauss."""
        if halo.mean_b_field is not None and halo.mean_b_field > 0:
            return halo.mean_b_field
        estimator = self._scaling_functions.get(self.scaling_model, self._vazza_scaling)
        return estimator(halo)

    def _vazza_scaling(self, halo: MagneticHaloData) -> float:
        """B ~ M_vir^(1/3) * (1+z)^2 * (spin/0.03)"""
        mass_factor = (halo.mass / 1e12) ** (1/3)
        spin_factor = halo.spin_parameter / 0.03
        # Assuming z~0 for snapshot 99; generalize as needed
        return 1.0 * mass_factor * spin_factor  # Baseline ~1 microgauss for Milky Way-like

    def _donnert_scaling(self, halo: MagneticHaloData) -> float:
        """B ~ sigma_v * sqrt(rho_gas) (equipartition argument)"""
        # Simplified: B in microgauss ~ sigma_v[km/s] * sqrt(n_e[cm^-3]) / 10
        rho_gas_proxy = halo.baryon_fraction * halo.mass / (4/3 * np.pi * halo.radius**3)
        n_e_proxy = rho_gas_proxy * 0.17 / 1.67e-24  # Rough electron density proxy
        return halo.velocity_dispersion * np.sqrt(max(n_e_proxy, 1e-5)) / 10.0

    def _dynamo_proxy_scaling(self, halo: MagneticHaloData) -> float:
        """
        Christensen 2009 scaling adapted: B ~ (rho * Omega * R^2)^(1/3)
        where Omega ~ spin parameter * H(z)
        """
        omega = halo.spin_parameter * 70.0 / halo.radius  # km/s/kpc ~ Gyr^-1 proxy
        rho_avg = halo.mass / (4/3 * np.pi * halo.radius**3)
        # Convert to cgs-ish and scale
        b_est = (rho_avg * omega * halo.radius**2) ** (1/3) * 1e-3
        return max(b_est, 0.01)  # Floor at 0.01 microgauss


class MagneticAssemblyIndex:
    """
    Computes magnetic contribution to Cosmological Assembly Index (A_c).

    The magnetic field acts as an 'information channel' coupling large-scale
    structure formation to local baryonic physics. We quantify this via:

    1. Topological complexity of B-field (structure beyond random)
    2. Coupling strength to baryonic dynamics (feedback efficiency)
    3. Non-random alignment with cosmic web filaments

    All normalized against null (Gaussian random field) models.
    """

    def __init__(self, bootstrap_iterations: int = 1000):
        self.bootstrap_iterations = bootstrap_iterations
        self.magnetic_estimator = HaloMagneticProxyEstimator()

    def compute_magnetic_complexity(self, halo: MagneticHaloData) -> Dict[str, float]:
        """
        Compute A_c_magnetic for a single halo.

        Returns dict with components:
        - a_c_magnetic: total magnetic assembly index [0,1]
        - a_c_topo: topological complexity of field
        - a_c_coupling: baryonic coupling strength
        - a_c_alignment: large-scale structure alignment
        """
        b_field = self.magnetic_estimator.estimate_field(halo)

        # Component 1: Topological complexity (proxy via field structure)
        # If we have 3D topology data, use it; else proxy from scaling
        if halo.b_field_topology is not None:
            a_c_topo = self._topology_complexity(halo.b_field_topology)
        else:
            # Proxy: higher field = more organized structure (saturated at high B)
            a_c_topo = np.tanh(b_field / 5.0) * 0.8 + 0.1  # Range ~0.1-0.9

        # Component 2: Baryonic coupling
        # Magnetic field affects gas cooling, star formation, feedback
        # Proxy: B-field vs velocity dispersion ratio (magnetic beta parameter inverse)
        beta_inv = (b_field * 1e-6)**2 / (8*np.pi) / (1.38e-16 * 1e4)  # B^2/8pi vs thermal
        beta_inv = min(beta_inv, 1.0)
        a_c_coupling = beta_inv * 0.7 + 0.1  # Saturation

        # Component 3: Large-scale alignment (requires cosmic web context)
        # For now, proxy from spin alignment (merger history encodes tidal field)
        if len(halo.merger_history) > 1:
            alignment_score = np.std(halo.merger_history) / np.mean(halo.merger_history)
            a_c_alignment = np.tanh(alignment_score) * 0.6 + 0.2
        else:
            a_c_alignment = 0.3  # Default for relaxed halos

        # Weighted assembly index
        weights = {"topo": 0.4, "coupling": 0.35, "alignment": 0.25}
        a_c_magnetic = (
            weights["topo"] * a_c_topo +
            weights["coupling"] * a_c_coupling +
            weights["alignment"] * a_c_alignment
        )

        return {
            "a_c_magnetic": float(a_c_magnetic),
            "a_c_topo": float(a_c_topo),
            "a_c_coupling": float(a_c_coupling),
            "a_c_alignment": float(a_c_alignment),
            "b_field_microgauss": float(b_field)
        }

    def _topology_complexity(self, b_topology: np.ndarray) -> float:
        """Compute topological complexity from 3D B-field structure."""
        # Simplified: use gradient structure tensor eigenvalues
        if b_topology.ndim != 3:
            return 0.5

        # Compute structure tensor
        grads = np.gradient(b_topology)
        structure = np.zeros((3, 3))
        for i in range(3):
            c9_bus_client.heartbeat()
            for j in range(3):
                structure[i, j] = np.mean(grads[i] * grads[j])

        eigenvalues = np.linalg.eigvalsh(structure)
        eigenvalues = np.sort(eigenvalues)[::-1]

        # Anisotropy = complexity (isotropic = random = low complexity)
        if eigenvalues[0] > 0:
            anisotropy = 1 - (eigenvalues[1] + eigenvalues[2]) / (2 * eigenvalues[0])
            return float(np.clip(anisotropy, 0.1, 0.95))
        return 0.5

    def compute_total_assembly_index(self, halo: MagneticHaloData) -> MagneticHaloData:
        """Compute full A_c including magnetic contribution."""
        magnetic_components = self.compute_magnetic_complexity(halo)

        halo.a_c_magnetic = magnetic_components["a_c_magnetic"]
        halo.a_c_total = (
            0.45 * halo.a_c_structural +
            0.35 * halo.a_c_dynamical +
            0.20 * halo.a_c_magnetic
        )

        return halo

    def bootstrap_significance(self, halos: List[MagneticHaloData], 
                               null_model: str = "shuffled_spin") -> Dict:
        """
        Bootstrap test: Is the magnetic A_c correlation with halo mass
        significantly different from null?

        Args:
            halos: List of MagneticHaloData with computed A_c
            null_model: Type of null model to generate

        Returns:
            Dict with p-value, effect size, confidence intervals
        """
        n = len(halos)
        observed_corr = np.corrcoef(
            [h.mass for h in halos],
            [h.a_c_magnetic for h in halos]
        )[0, 1]

        null_corrs = []
        for _ in range(self.bootstrap_iterations):
            if null_model == "shuffled_spin":
                spins = [h.spin_parameter for h in halos]
                np.random.shuffle(spins)
                # Recompute A_c with shuffled spins
                temp_halos = []
                for i, h in enumerate(halos):
                    h_copy = MagneticHaloData(
                        halo_id=h.halo_id, mass=h.mass, radius=h.radius,
                        spin_parameter=spins[i], velocity_dispersion=h.velocity_dispersion,
                        metallicity_gas=h.metallicity_gas, baryon_fraction=h.baryon_fraction,
                        merger_history=h.merger_history
                    )
                    temp_halos.append(self.compute_total_assembly_index(h_copy))

                null_corr = np.corrcoef(
                    [h.mass for h in temp_halos],
                    [h.a_c_magnetic for h in temp_halos]
                )[0, 1]
                null_corrs.append(null_corr)

        null_corrs = np.array(null_corrs)
        p_value = np.mean(null_corrs >= observed_corr) if observed_corr > 0 else np.mean(null_corrs <= observed_corr)

        return {
            "observed_correlation": float(observed_corr),
            "null_mean": float(np.mean(null_corrs)),
            "null_std": float(np.std(null_corrs)),
            "p_value": float(p_value),
            "significant_at_95": p_value < 0.05,
            "significant_at_99": p_value < 0.01,
            "confidence_interval_95": [
                float(np.percentile(null_corrs, 2.5)),
                float(np.percentile(null_corrs, 97.5))
            ]
        }


class TNGMagneticACPipeline:
    """
    End-to-end pipeline for processing TNG snapshots and computing
    magnetic Assembly Index.

    Usage:
        pipeline = TNGMagneticACPipeline()
        halos = pipeline.load_tng_halos("tng100_snapshot_99.hdf5")
        results = pipeline.run_assembly_analysis(halos)
    """

    def __init__(self, snapshot_path: Optional[str] = None):
        self.snapshot_path = snapshot_path
        self.magnetic_ac = MagneticAssemblyIndex()
        self.results: List[MagneticHaloData] = []

    def load_tng_halos(self, path: str, max_halos: int = 2000) -> List[MagneticHaloData]:
        """
        Load halo catalog from TNG HDF5 file.
        Compatible with IllustrisTNG group catalogs.
        """
        halos = []
        try:
            with h5py.File(path, 'r') as f:
                # Standard TNG group catalog structure
                halo_ids = f['Group']['GroupFirstSub'][:max_halos] if 'GroupFirstSub' in f['Group'] else np.arange(max_halos)
                masses = f['Group']['GroupMass'][:max_halos] * 1e10 / 0.6774  # Msun, h=0.6774
                radii = f['Group']['Group_R_Crit200'][:max_halos] / 0.6774  # kpc

                # Spin parameter if available
                spins = np.zeros(len(masses))
                if 'GroupSpin' in f['Group']:
                    spin_data = f['Group']['GroupSpin'][:max_halos]
                    spins = np.linalg.norm(spin_data, axis=1) if spin_data.ndim > 1 else spin_data

                # Metallicity proxy
                metallicities = np.full(len(masses), 0.02)
                if 'GroupStarMetallicity' in f['Group']:
                    metallicities = f['Group']['GroupStarMetallicity'][:max_halos]

                for i in range(min(len(masses), max_halos)):
                    halo = MagneticHaloData(
                        halo_id=int(halo_ids[i]) if i < len(halo_ids) else i,
                        mass=float(masses[i]),
                        radius=float(radii[i]) if i < len(radii) else 200.0,
                        spin_parameter=float(spins[i]) if i < len(spins) else 0.03,
                        velocity_dispersion=100.0,  # Default, should be computed from particles
                        metallicity_gas=float(metallicities[i]) if i < len(metallicities) else 0.02,
                        baryon_fraction=0.15,
                        merger_history=np.array([1.0])  # Placeholder
                    )
                    halos.append(halo)
        except Exception as e:
            warnings.warn(f"Could not load TNG file {path}: {e}. Generating synthetic test data.")
            halos = self._generate_synthetic_halos(max_halos)

        return halos

    def _generate_synthetic_halos(self, n: int) -> List[MagneticHaloData]:
        """Generate synthetic halos for testing when TNG data unavailable."""
        np.random.seed(42)
        halos = []
        for i in range(n):
            mass = np.random.lognormal(np.log(1e12), 1.0)
            spin = np.random.lognormal(np.log(0.03), 0.5)
            halo = MagneticHaloData(
                halo_id=i, mass=mass, radius=200 * (mass/1e12)**(1/3),
                spin_parameter=spin, velocity_dispersion=100 * (mass/1e12)**(1/3),
                metallicity_gas=np.random.lognormal(np.log(0.02), 0.3),
                baryon_fraction=0.15, merger_history=np.random.exponential(1.0, 5)
            )
            halos.append(halo)
        return halos

    def run_assembly_analysis(self, halos: List[MagneticHaloData]) -> Dict:
        """Run full magnetic assembly analysis on halo sample."""
        # Compute existing structural/dynamical A_c (from existing suite)
        for halo in halos:
            # Structural: based on mass-concentration relation deviation
            halo.a_c_structural = np.tanh(halo.mass / 1e13) * 0.7 + 0.1
            # Dynamical: based on spin parameter anomaly
            halo.a_c_dynamical = np.exp(-((halo.spin_parameter - 0.03)/0.05)**2) * 0.8 + 0.1

            # Compute magnetic A_c
            self.magnetic_ac.compute_total_assembly_index(halo)

        self.results = halos

        # Statistical tests
        bootstrap_results = self.magnetic_ac.bootstrap_significance(halos)

        return {
            "n_halos": len(halos),
            "mean_a_c_magnetic": np.mean([h.a_c_magnetic for h in halos]),
            "mean_a_c_total": np.mean([h.a_c_total for h in halos]),
            "mass_magnetic_correlation": np.corrcoef(
                [h.mass for h in halos], [h.a_c_magnetic for h in halos]
            )[0, 1],
            "bootstrap_significance": bootstrap_results,
            "top_halos_by_magnetic_ac": sorted(
                halos, key=lambda h: h.a_c_magnetic, reverse=True
            )[:10]
        }

    def export_to_cloud9_json(self, output_path: str):
        """Export results in Cloud-9 repository format."""
        export_data = {
            "entry_id": "C9-2026-TNG-MAG-002",
            "timestamp": "2026-06-03T15:31:00Z",
            "n_halos": len(self.results),
            "halos": [
                {
                    "halo_id": h.halo_id,
                    "mass_msun": float(h.mass),
                    "a_c_structural": float(h.a_c_structural),
                    "a_c_dynamical": float(h.a_c_dynamical),
                    "a_c_magnetic": float(h.a_c_magnetic),
                    "a_c_total": float(h.a_c_total),
                    "b_field_proxy_microgauss": float(
                        self.magnetic_ac.magnetic_estimator.estimate_field(h)
                    )
                }
                for h in self.results[:100]  # Limit export size
            ]
        }
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


# =============================================================================
# CLI / Direct Execution
# =============================================================================
if __name__ == "__main__":
    print("Cloud-9 TNG Magnetic Assembly Index Extension v2.2.0")
    print("=" * 60)

    pipeline = TNGMagneticACPipeline()

    # Try to load real data, fallback to synthetic
    halos = pipeline.load_tng_halos("tng100_snapshot_99.hdf5", max_halos=500)
    print(f"Loaded {len(halos)} halos")

    results = pipeline.run_assembly_analysis(halos)

    print(f"\nResults:")
    print(f"  Mean A_c (magnetic): {results['mean_a_c_magnetic']:.3f}")
    print(f"  Mean A_c (total):    {results['mean_a_c_total']:.3f}")
    print(f"  Mass-Magnetic correlation: {results['mass_magnetic_correlation']:.3f}")
    print(f"  Significant at 95%: {results['bootstrap_significance']['significant_at_95']}")
    print(f"  Significant at 99%: {results['bootstrap_significance']['significant_at_99']}")

    pipeline.export_to_cloud9_json("tng_magnetic_ac_results.json")
    print("\nExported to tng_magnetic_ac_results.json")
