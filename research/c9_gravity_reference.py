"""
G-Reference System for Cloud-9 TNG Validation Suite
=====================================================

Module: c9_gravity_reference.py
Entry ID: C9-2026-GRAVITY-001
Version: 1.0.0
Date: 2026-05-18

Provides gravitational constant reference management for cosmological
simulation validation, enabling systematic uncertainty propagation from
metrological discrepancies into halo mass function analyses.

References:
-----------
- Schlamminger et al. (2026), Metrologia 63, 025012. DOI: 10.1088/1681-7575/ae570f
- CODATA 2018 recommended values (Rev. Mod. Phys. 93, 025010)
- BIPM 2007 measurement (Phys. Rev. Lett. 102, 240801)
- Cloud-9 Assembly Project: Expanded Grand Sandbox v2.0 (Layer 1/2/3 framework)

"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Union
from enum import Enum
import warnings


class GReference(Enum):
    """Enumeration of supported gravitational constant references."""
    CODATA_2018 = "codata_2018"
    BIPM_2007 = "bipm_2007"
    NIST_2026 = "nist_2026"
    JILA_2010 = "jila_2010"
    UWash_2000 = "uwash_2000"
    HUST_2018 = "hust_2018"


@dataclass
class GMeasurement:
    """Container for a gravitational constant measurement with metadata."""

    value: float  # m^3 kg^-1 s^-2
    uncertainty: float  # absolute uncertainty
    reference: GReference
    year: int
    institution: str
    technique: str
    material: Optional[str] = None
    blinded: bool = False
    doi: Optional[str] = None

    @property
    def relative_uncertainty(self) -> float:
        """Return relative uncertainty (fractional)."""
        return self.uncertainty / self.value

    @property
    def ppm_uncertainty(self) -> float:
        """Return relative uncertainty in parts per million."""
        return self.relative_uncertainty * 1e6

    def __repr__(self) -> str:
        return (f"GMeasurement({self.reference.value}, "
                f"G={self.value:.5e} Â± {self.uncertainty:.2e}, "
                f"{self.ppm_uncertainty:.1f} ppm, {self.institution} {self.year})")


# ============================================================
# MEASUREMENT DATABASE (Schlamminger et al. 2026 + historical)
# ============================================================

G_DATABASE: Dict[GReference, GMeasurement] = {
    GReference.CODATA_2018: GMeasurement(
        value=6.67430e-11,
        uncertainty=0.00015e-11,
        reference=GReference.CODATA_2018,
        year=2018,
        institution="CODATA",
        technique="Weighted average of all available measurements",
        blinded=False,
        doi="10.1103/RevModPhys.93.025010"
    ),

    GReference.BIPM_2007: GMeasurement(
        value=6.67425e-11,
        uncertainty=0.00012e-11,
        reference=GReference.BIPM_2007,
        year=2007,
        institution="Bureau International des Poids et Mesures (SÃ¨vres, France)",
        technique="Torsion balance with electrostatic compensation",
        material="Cu-Be ribbon, stainless steel masses",
        blinded=False,
        doi="10.1103/PhysRevLett.102.240801"
    ),

    GReference.NIST_2026: GMeasurement(
        value=6.67387e-11,
        uncertainty=0.00016e-11,
        reference=GReference.NIST_2026,
        year=2026,
        institution="National Institute of Standards and Technology (Gaithersburg, USA)",
        technique="BIPM torsion balance replica with blinded analysis",
        material="Cu-Be ribbon, Cu and sapphire masses (cross-check)",
        blinded=True,
        doi="10.1088/1681-7575/ae570f"
    ),

    GReference.JILA_2010: GMeasurement(
        value=6.67260e-11,
        uncertainty=0.00050e-11,
        reference=GReference.JILA_2010,
        year=2010,
        institution="JILA (University of Colorado / NIST)",
        technique="Atom interferometry",
        material="Rubidium atoms",
        blinded=False,
        doi="10.1103/PhysRevLett.105.110801"
    ),

    GReference.UWash_2000: GMeasurement(
        value=6.67422e-11,
        uncertainty=0.00098e-11,
        reference=GReference.UWash_2000,
        year=2000,
        institution="University of Washington",
        technique="Torsion pendulum with fiber suspension",
        material="Tungsten masses",
        blinded=False,
        doi="10.1103/PhysRevD.62.101101"
    ),

    GReference.HUST_2018: GMeasurement(
        value=6.67435e-11,
        uncertainty=0.00013e-11,
        reference=GReference.HUST_2018,
        year=2018,
        institution="Huazhong University of Science and Technology (Wuhan, China)",
        technique="Torsion balance with angular acceleration feedback",
        material="Glass fiber, stainless steel masses",
        blinded=False,
        doi="10.1038/s41586-018-0431-5"
    ),
}


# ============================================================
# CORE CLASS: GReferenceManager
# ============================================================

class GReferenceManager:
    """
    Manages gravitational constant references for cosmological simulations.

    Provides mass renormalization, uncertainty propagation, and consistency
    checks for TNG validation suite integration.

    Attributes:
        active_reference: Currently selected G reference (default: CODATA_2018)
        sim_reference: G value used in the simulation (typically CODATA_2018)
    """

    def __init__(self, 
                 active_reference: GReference = GReference.CODATA_2018,
                 sim_reference: GReference = GReference.CODATA_2018):
        """
        Initialize the G-reference manager.

        Args:
            active_reference: The reference to use for observational comparisons
            sim_reference: The reference assumed in the simulation data
        """
        self.active_reference = active_reference
        self.sim_reference = sim_reference
        self._validate_references()

    def _validate_references(self) -> None:
        """Ensure both references exist in the database."""
        for ref in [self.active_reference, self.sim_reference]:
            if ref not in G_DATABASE:
                raise ValueError(f"Reference {ref} not found in G_DATABASE")

    @property
    def G_active(self) -> float:
        """Return the active G value."""
        return G_DATABASE[self.active_reference].value

    @property
    def G_sim(self) -> float:
        """Return the simulation G value."""
        return G_DATABASE[self.sim_reference].value

    @property
    def G_ratio(self) -> float:
        """Return the ratio G_active / G_sim for mass renormalization."""
        return self.G_active / self.G_sim

    @property
    def mass_correction_factor(self) -> float:
        """
        Return the mass correction factor.

        For fixed dynamical observables (velocity dispersion, lensing signal),
        M_true = M_sim * (G_sim / G_active)

        If active G < sim G (e.g., NIST < CODATA), masses are OVERESTIMATED
        in the simulation and must be REDUCED.
        """
        return self.G_sim / self.G_active

    def renormalize_mass(self, mass_sim: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Renormalize simulation mass to active reference frame.

        Args:
            mass_sim: Mass(es) in simulation units [Msun]

        Returns:
            Renormalized mass(es) [Msun]
        """
        return mass_sim * self.mass_correction_factor

    def renormalize_mass_array(self, masses: np.ndarray) -> np.ndarray:
        """Vectorized version of renormalize_mass."""
        return self.renormalize_mass(masses)

    def get_uncertainty_budget(self, n_halos: int = 2000) -> Dict[str, float]:
        """
        Compute the G-related uncertainty budget.

        Args:
            n_halos: Number of halos in the sample (for bootstrap estimate)

        Returns:
            Dictionary of uncertainty components in fractional form
        """
        active = G_DATABASE[self.active_reference]
        sim = G_DATABASE[self.sim_reference]

        # Statistical uncertainty from measurement
        stat_unc = active.relative_uncertainty

        # Systematic: difference between active and sim references
        sys_unc = abs(active.value - sim.value) / sim.value

        # Bootstrap uncertainty (assuming Poisson)
        bootstrap_unc = 1.0 / np.sqrt(n_halos)

        # Combined in quadrature (statistical + systematic, bootstrap separate)
        combined_unc = np.sqrt(stat_unc**2 + sys_unc**2)

        return {
            "G_statistical": stat_unc,
            "G_systematic_sim_mismatch": sys_unc,
            "G_combined": combined_unc,
            "bootstrap_1sigma": bootstrap_unc,
            "bootstrap_2sigma": 2.0 * bootstrap_unc,
            "G_to_bootstrap_ratio": combined_unc / bootstrap_unc,
            "n_halos": n_halos,
        }

    def print_uncertainty_budget(self, n_halos: int = 2000) -> None:
        """Pretty-print the uncertainty budget."""
        budget = self.get_uncertainty_budget(n_halos)

        print("=" * 60)
        print(f"G-UNCERTAINTY BUDGET (n_halos={n_halos})")
        print("=" * 60)
        print(f"Active reference:  {self.active_reference.value}")
        print(f"Simulation reference: {self.sim_reference.value}")
        print(f"G_active = {self.G_active:.5e}")
        print(f"G_sim    = {self.G_sim:.5e}")
        print(f"Mass correction: M_true = M_sim * {self.mass_correction_factor:.6f}")
        print("-" * 60)
        for key, val in budget.items():
            if isinstance(val, float):
                print(f"  {key:<35}: {val*100:>10.6f}% ({val*1e6:>8.2f} ppm)")
            else:
                print(f"  {key:<35}: {val}")
        print("=" * 60)

        ratio = budget["G_to_bootstrap_ratio"]
        if ratio < 0.01:
            print(f"VERDICT: G-uncertainty is {1/ratio:.0f}* SMALLER than bootstrap.")
            print("         Safe to ignore for current sample size.")
        elif ratio < 0.1:
            print(f"VERDICT: G-uncertainty is {1/ratio:.0f}* smaller than bootstrap.")
            print("         Negligible but track for future scaling.")
        else:
            print(f"WARNING: G-uncertainty is {ratio:.1f}* the bootstrap!")
            print("         Include in formal error budget.")

    def compare_all_references(self) -> Tuple[np.ndarray, list]:
        """
        Generate comparison matrix of all references in database.

        Returns:
            (n_refs, n_refs) array of fractional differences, list of refs
        """
        refs = list(G_DATABASE.keys())
        n = len(refs)
        diff_matrix = np.zeros((n, n))

        for i, ref_i in enumerate(refs):
            for j, ref_j in enumerate(refs):
                Gi = G_DATABASE[ref_i].value
                Gj = G_DATABASE[ref_j].value
                diff_matrix[i, j] = (Gi - Gj) / Gj

        return diff_matrix, refs

    def print_comparison_table(self) -> None:
        """Print formatted comparison of all G measurements."""
        diff_matrix, refs = self.compare_all_references()

        print("\n" + "=" * 80)
        print("GRAVITATIONAL CONSTANT COMPARISON MATRIX")
        print("=" * 80)
        print(f"{'Reference':<15}", end="")
        for ref in refs:
            print(f"{ref.value:<12}", end="")
        print()
        print("-" * 80)

        for i, ref_i in enumerate(refs):
            print(f"{ref_i.value:<15}", end="")
            for j, ref_j in enumerate(refs):
                val = diff_matrix[i, j]
                if i == j:
                    print(f"{'---':<12}", end="")
                else:
                    print(f"{val*1e6:>+10.1f}  ", end="")
            print()
        print("=" * 80)
        print("Values in ppm (parts per million). Row minus column, relative to column.")

        # Print measurement details
        print("\n" + "=" * 80)
        print("MEASUREMENT DETAILS")
        print("=" * 80)
        for ref in refs:
            m = G_DATABASE[ref]
            print(f"\n{m.reference.value}:")
            print(f"  Value:       {m.value:.5e} Â± {m.uncertainty:.2e}")
            print(f"  Institution: {m.institution}")
            print(f"  Year:        {m.year}")
            print(f"  Technique:   {m.technique}")
            print(f"  Material:    {m.material or 'N/A'}")
            print(f"  Blinded:     {'YES' if m.blinded else 'No'}")
            print(f"  DOI:         {m.doi or 'N/A'}")


# ============================================================
# INTEGRATION: TNG Halo Mass Renormalization
# ============================================================

def renormalize_tng_halos(halo_masses: np.ndarray,
                          halo_redshifts: Optional[np.ndarray] = None,
                          g_manager: Optional[GReferenceManager] = None,
                          return_correction_only: bool = False) -> Union[float, np.ndarray, Tuple]:
    """
    Apply G-reference renormalization to TNG halo masses.

    This is the primary integration point with tng_validation_suite.py.

    Args:
        halo_masses: Array of halo masses from TNG [Msun]
        halo_redshifts: Optional redshifts for time-dependent corrections
        g_manager: GReferenceManager instance (default: CODATA_2018)
        return_correction_only: If True, return only the correction factor

    Returns:
        Renormalized masses, or (masses, correction_factor) tuple, or float
    """
    if g_manager is None:
        g_manager = GReferenceManager()

    correction = g_manager.mass_correction_factor

    if return_correction_only:
        return correction

    renormalized = halo_masses * correction

    # Optional: redshift-dependent correction for evolving G theories
    # (Placeholder for beyond-LCDM models where G(z) is non-constant)
    if halo_redshifts is not None:
        # Currently no redshift dependence in standard models
        # This hook exists for Brans-Dicke, f(R), or QBox modifications
        pass

    return renormalized, correction
