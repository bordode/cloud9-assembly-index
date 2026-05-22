"""
QBox Hyperdecoherence Bound from Cavendish Material Cross-Check
===============================================================

Module: c9_qbox_decoherence_bound.py
Entry ID: C9-2026-QBOX-001
Version: 1.0.0
Date: 2026-05-18

Computes constraints on QBox (Hefford & Wilson 2025) hyperdecoherence
models from the NIST copper/sapphire null result in the Schlamminger
et al. (2026) big G measurement.

Theoretical Framework:
----------------------
QBox postulates that quantum gravitational decoherence induces stochastic
phase fluctuations in macroscopic superpositions. For Cavendish-type
torsion balances, this could manifest as:

1. Composition-dependent decoherence: Different materials (Cu vs. Al2O3)
   have different nuclear/electron configurations -> different coupling
   to hypothetical quantum gravity degrees of freedom.

2. Mass-dependent decoherence: Heavier test masses couple more strongly
   to spacetime geometry fluctuations.

The NIST experiment used both copper and sapphire masses and found
identical G values to within the measurement precision. This places
an upper bound on any composition-dependent QBox effect.

References:
-----------
- Hefford & Wilson (2025), QBox Framework
- Schlamminger et al. (2026), Metrologia 63, 025012
- Cloud-9 Assembly Project: Layer 1/2/3 epistemological framework

"""

import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import warnings


# ============================================================
# PHYSICAL CONSTANTS
# ============================================================

MATERIAL_PROPERTIES = {
    "copper": {
        "density": 8960,
        "molar_mass": 63.546e-3,
        "atomic_number": 29,
        "neutrons_per_atom": 34,
        "protons_per_atom": 29,
        "electrons_per_atom": 29,
        "crystal_structure": "fcc",
        "debye_temperature": 315,
        "nuclear_spin": 1.5,
        "magnetic_moment": 2.227,
    },
    "sapphire": {
        "density": 3980,
        "molar_mass": 101.96e-3,
        "formula_units": {"Al": 2, "O": 3},
        "atomic_numbers": {"Al": 13, "O": 8},
        "neutrons_per_formula": {"Al": 14, "O": 8},
        "protons_per_formula": {"Al": 13, "O": 8},
        "electrons_per_formula": {"Al": 13, "O": 8},
        "crystal_structure": "corundum",
        "debye_temperature": 1047,
        "nuclear_spins": {"Al": 2.5, "O": 0},
    }
}

NIST_EXPERIMENT = {
    "mass_cylinders": 1.0,
    "torsion_ribbon_length": 0.3,
    "torsion_ribbon_thickness": 20e-6,
    "torsion_constant": 1e-9,
    "measurement_duration": 10 * 365.25 * 24 * 3600,
    "angular_resolution": 1e-9,
    "temperature": 293,
    "pressure": 1e5,
    "G_uncertainty": 0.00016e-11,
    "G_value": 6.67387e-11,
    "null_result_precision": 0.00016e-11,
}


# ============================================================
# QBOX DECOHERENCE MODELS
# ============================================================

@dataclass
class QBoxModel:
    """Base class for QBox hyperdecoherence models."""

    name: str
    description: str
    parameters: Dict[str, float]
    layer: int = 2

    def differential_g(self, mat1: str, mat2: str) -> float:
        raise NotImplementedError

    def constrain_from_null(self, mat1: str, mat2: str, 
                           null_precision: float, confidence_level: float = 0.95) -> Dict:
        raise NotImplementedError


class NuclearSpinDecoherence(QBoxModel):
    """Decoherence rate depends on nuclear spin configuration."""

    def __init__(self, gamma_spin: float = 1.0):
        super().__init__(
            name="NuclearSpinDecoherence",
            description="QBox decoherence proportional to nuclear spin density",
            parameters={"gamma_spin": gamma_spin},
        )

    def _spin_density(self, material: str) -> float:
        props = MATERIAL_PROPERTIES[material]

        if material == "copper":
            n_atoms = props["density"] / props["molar_mass"] * 6.022e23
            spin_per_atom = props["nuclear_spin"]
            return n_atoms * spin_per_atom

        elif material == "sapphire":
            n_formula = props["density"] / props["molar_mass"] * 6.022e23
            spin_per_formula = (2 * 2.5 + 3 * 0) / 5
            return n_formula * spin_per_formula

        else:
            raise ValueError(f"Unknown material: {material}")

    def differential_g(self, mat1: str, mat2: str) -> float:
        rho1 = self._spin_density(mat1)
        rho2 = self._spin_density(mat2)
        rho_mean = (rho1 + rho2) / 2
        gamma = self.parameters["gamma_spin"]
        return gamma * (rho1 - rho2) / rho_mean

    def constrain_from_null(self, mat1: str = "copper", mat2: str = "sapphire",
                           null_precision: float = 2.4e-5, confidence_level: float = 0.95) -> Dict:
        z_score = norm.ppf((1 + confidence_level) / 2)
        max_delta_g = z_score * null_precision

        rho1 = self._spin_density(mat1)
        rho2 = self._spin_density(mat2)
        rho_mean = (rho1 + rho2) / 2
        spin_asymmetry = abs(rho1 - rho2) / rho_mean

        gamma_max = max_delta_g / spin_asymmetry
        gamma_max_1sigma = null_precision / spin_asymmetry

        return {
            "gamma_spin_max": gamma_max,
            "gamma_spin_max_1sigma": gamma_max_1sigma,
            "spin_density_1": rho1,
            "spin_density_2": rho2,
            "spin_asymmetry": spin_asymmetry,
            "max_allowed_delta_g": max_delta_g,
            "confidence_level": confidence_level,
            "z_score": z_score,
        }


class BaryonNumberDecoherence(QBoxModel):
    """Decoherence rate depends on baryon number density."""

    def __init__(self, gamma_baryon: float = 1.0):
        super().__init__(
            name="BaryonNumberDecoherence",
            description="QBox decoherence proportional to baryon number density",
            parameters={"gamma_baryon": gamma_baryon},
        )

    def _baryon_density(self, material: str) -> float:
        props = MATERIAL_PROPERTIES[material]

        if material == "copper":
            n_atoms = props["density"] / props["molar_mass"] * 6.022e23
            baryons_per_atom = props["atomic_number"] + props["neutrons_per_atom"]
            return n_atoms * baryons_per_atom

        elif material == "sapphire":
            n_formula = props["density"] / props["molar_mass"] * 6.022e23
            baryons_per_formula = (2 * (13 + 14) + 3 * (8 + 8))
            return n_formula * baryons_per_formula

        else:
            raise ValueError(f"Unknown material: {material}")

    def differential_g(self, mat1: str, mat2: str) -> float:
        rho1 = self._baryon_density(mat1)
        rho2 = self._baryon_density(mat2)
        rho_mean = (rho1 + rho2) / 2
        gamma = self.parameters["gamma_baryon"]
        return gamma * (rho1 - rho2) / rho_mean

    def constrain_from_null(self, mat1: str = "copper", mat2: str = "sapphire",
                           null_precision: float = 2.4e-5, confidence_level: float = 0.95) -> Dict:
        z_score = norm.ppf((1 + confidence_level) / 2)
        max_delta_g = z_score * null_precision

        rho1 = self._baryon_density(mat1)
        rho2 = self._baryon_density(mat2)
        rho_mean = (rho1 + rho2) / 2
        baryon_asymmetry = abs(rho1 - rho2) / rho_mean

        gamma_max = max_delta_g / baryon_asymmetry

        return {
            "gamma_baryon_max": gamma_max,
            "baryon_density_1": rho1,
            "baryon_density_2": rho2,
            "baryon_asymmetry": baryon_asymmetry,
            "max_allowed_delta_g": max_delta_g,
            "confidence_level": confidence_level,
            "z_score": z_score,
        }


class GravitationalBindingDecoherence(QBoxModel):
    """Decoherence rate depends on gravitational self-binding energy."""

    def __init__(self, gamma_bind: float = 1.0):
        super().__init__(
            name="GravitationalBindingDecoherence",
            description="QBox decoherence proportional to gravitational self-energy",
            parameters={"gamma_bind": gamma_bind},
        )

    def _binding_parameter(self, material: str) -> float:
        props = MATERIAL_PROPERTIES[material]
        rho = props["density"]
        return rho ** (5.0/3.0)

    def differential_g(self, mat1: str, mat2: str) -> float:
        u1 = self._binding_parameter(mat1)
        u2 = self._binding_parameter(mat2)
        u_mean = (u1 + u2) / 2
        gamma = self.parameters["gamma_bind"]
        return gamma * (u1 - u2) / u_mean

    def constrain_from_null(self, mat1: str = "copper", mat2: str = "sapphire",
                           null_precision: float = 2.4e-5, confidence_level: float = 0.95) -> Dict:
        z_score = norm.ppf((1 + confidence_level) / 2)
        max_delta_g = z_score * null_precision

        u1 = self._binding_parameter(mat1)
        u2 = self._binding_parameter(mat2)
        u_mean = (u1 + u2) / 2
        binding_asymmetry = abs(u1 - u2) / u_mean

        gamma_max = max_delta_g / binding_asymmetry

        return {
            "gamma_bind_max": gamma_max,
            "binding_param_1": u1,
            "binding_param_2": u2,
            "binding_asymmetry": binding_asymmetry,
            "max_allowed_delta_g": max_delta_g,
            "confidence_level": confidence_level,
            "z_score": z_score,
        }


# ============================================================
# CONSTRAINT ANALYSIS ENGINE
# ============================================================

class QBoxConstraintEngine:
    """Computes and compares constraints across multiple QBox models."""

    def __init__(self, null_precision: float = 2.4e-5, confidence_level: float = 0.95):
        self.null_precision = null_precision
        self.confidence_level = confidence_level
        self.models: Dict[str, QBoxModel] = {}

    def register_model(self, model: QBoxModel) -> None:
        self.models[model.name] = model

    def compute_all_constraints(self, mat1: str = "copper", mat2: str = "sapphire") -> Dict:
        results = {}
        for name, model in self.models.items():
            constraints = model.constrain_from_null(
                mat1=mat1, mat2=mat2,
                null_precision=self.null_precision,
                confidence_level=self.confidence_level
            )
            results[name] = {
                "model": model,
                "constraints": constraints,
            }
        return results

    def print_constraint_report(self, mat1: str = "copper", mat2: str = "sapphire") -> None:
        results = self.compute_all_constraints(mat1, mat2)

        print("=" * 80)
        print("QBOX HYPERDECOHERENCE CONSTRAINTS FROM NIST Cu/Al2O3 NULL RESULT")
        print("=" * 80)
        print(f"Experimental precision:     {self.null_precision*1e6:.1f} ppm")
        print(f"Confidence level:           {self.confidence_level*100:.0f}%")
        print(f"Materials compared:         {mat1} vs. {mat2}")
        print(f"Cloud-9 Layer:              2 (Speculative Physics)")
        print(f"Entry ID:                   C9-2026-QBOX-001")
        print("=" * 80)

        for name, result in results.items():
            model = result["model"]
            c = result["constraints"]

            print(f"\n{'â' * 80}")
            print(f"MODEL: {model.name}")
            print(f"Description: {model.description}")
            print(f"{'â' * 80}")

            param_key = [k for k in c.keys() if "_max" in k and "_max_1" not in k][0]
            gamma_max = c[param_key]

            print(f"  Constraint parameter:     {param_key}")
            print(f"  Upper bound (95% CL):     {gamma_max:.4e}")
            if "_max_1sigma" in str(c.keys()):
                sigma_key = [k for k in c.keys() if "_max_1sigma" in k]
                if sigma_key:
                    print(f"  Upper bound (1sigma):     {c[sigma_key[0]]:.4e}")

            asym_keys = [k for k in c.keys() if "asymmetry" in k]
            if asym_keys:
                print(f"  Material asymmetry:       {c[asym_keys[0]]:.4f}")

            if gamma_max < 1e-10:
                print(f"  STATUS: STRONGLY CONSTRAINED (gamma < 10^-10)")
                print(f"  Interpretation: Model effectively ruled out at this precision")
            elif gamma_max < 1e-6:
                print(f"  STATUS: TIGHT CONSTRAINT (gamma < 10^-6)")
                print(f"  Interpretation: Requires extreme fine-tuning")
            elif gamma_max < 1e-3:
                print(f"  STATUS: MODERATE CONSTRAINT (gamma < 10^-3)")
                print(f"  Interpretation: Interesting but not decisive")
            else:
                print(f"  STATUS: WEAK CONSTRAINT (gamma > 10^-3)")
                print(f"  Interpretation: Null result not sensitive to this model")

        print("\n" + "=" * 80)
        print("EPISTEMOLOGICAL NOTE (Layer 2 Guardrails)")
        print("=" * 80)
        print("These constraints apply ONLY within the QBox framework.")
        print("They do NOT constitute evidence for or against quantum gravity effects.")
        print("")
        print("The null result is consistent with:")
        print("  (a) No composition-dependent quantum gravity effects at this precision")
        print("  (b) QBox models with coupling constants below the computed bounds")
        print("  (c) Alternative quantum gravity frameworks not captured by QBox")
        print("")
        print("Per Expanded Grand Sandbox v2.0 Layer 2 protocol:")
        print("  - These bounds are mathematical constraints on a speculative model")
        print("  - They do not claim physical reality of the underlying mechanism")
        print("  - They provide a quantitative bridge between metrology and theory")
        print("  - They are subject to revision if QBox framework is updated")

    def generate_cloud9_entry(self) -> str:
        """Generate a formal Cloud-9 repository entry."""
        results = self.compute_all_constraints()

        lines = [
            "# Cloud-9 Assembly Project Entry",
            "# ID: C9-2026-QBOX-001",
            "# Date: 2026-05-18",
            "# Layer: 2 (Speculative Physics)",
            "# Status: ACTIVE CONSTRAINT",
            "",
            "## QBox Hyperdecoherence Bounds from Cavendish Material Cross-Check",
            "",
            "### Source Experiment",
            "- **Reference**: Schlamminger et al. (2026), Metrologia 63, 025012",
            "- **Technique**: BIPM torsion balance replica with blinded analysis",
            "- **Materials**: Copper (Cu) and sapphire (Al2O3) test masses",
            "- **Null Result**: G_Cu = G_sapphire to within 24 ppm (95% CL)",
            "",
            "### QBox Model Constraints",
        ]

        for name, result in results.items():
            c = result["constraints"]
            param_key = [k for k in c.keys() if "_max" in k and "_max_1" not in k][0]
            lines.append(f"#### {name}")
            lines.append(f"- **Parameter**: {param_key}")
            lines.append(f"- **95% CL Upper Bound**: {c[param_key]:.4e}")
            asym_keys = [k for k in c.keys() if "asymmetry" in k]
            if asym_keys:
                lines.append(f"- **Material Asymmetry**: {c[asym_keys[0]]}")
            lines.append("")

        lines.extend([
            "### Implications for Cloud-9 Assembly Index",
            "- A_c calculations assume G is material-independent (verified at 24 ppm)",
            "- No composition-dependent correction needed for metallicity filters",
            "- Cu/Al2O3 null result validates standard gravitational mass equivalence",
            "",
            "### Cross-References",
            "- C9-2026-GRAVITY-001 (G-Reference System)",
            "- C9-2026-LEGACY-001 (Fujitsu Kozuchi metrological protocols)",
            "- EGS-v2.0 Layer 2 Framework (Hefford & Wilson 2025 QBox)",
            "",
            "### Open Questions",
            "1. Can QBox be extended to predict G(z) redshift dependence?",
            "2. Would Brans-Dicke scalar field show material-dependent G?",
            "3. How do these bounds compare to atom interferometry tests?",
        ])

        return "\n".join(lines)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    engine = QBoxConstraintEngine(null_precision=2.4e-5, confidence_level=0.95)
    engine.register_model(NuclearSpinDecoherence())
    engine.register_model(BaryonNumberDecoherence())
    engine.register_model(GravitationalBindingDecoherence())
    engine.print_constraint_report()
    print("\n" + "=" * 80)
    print("CLOUD-9 REPOSITORY ENTRY")
    print("=" * 80)
    print(engine.generate_cloud9_entry())
