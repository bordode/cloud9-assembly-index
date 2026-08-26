#!/usr/bin/env python3
"""
Cloud-9 Null Ensemble Generator v3 — KSG TEMPORAL MI
Publication-grade pipeline using Kraskov-Stögbauer-Grassberger
k-NN mutual information integrated over cosmic time.

Author: Assistant (for Dean Bordode / Cloud-9 research)
Date: 2026-08-24
"""

import numpy as np
from scipy.special import digamma
from scipy.spatial import cKDTree
from scipy.integrate import quad
import matplotlib.pyplot as plt
import json
import multiprocessing as mp
import time
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# ==================== CONFIG ====================
N_HALOS = 100
N_WORKERS = 8
GRID_RES = 32
BOX_SIZE_MPC = 20.0
Z_INIT = 20.0
Z_FINAL = 0.05
N_STEPS = 16
SEED_BASE = 1000

# Cloud-9 measured value
CLOUD9_A_C = 87.3
CLOUD9_SYSTEMATIC = 3.2

# Cosmology
COSMO = {
    "Omega_m": 0.315,
    "Omega_L": 0.685,
    "H0": 67.4,
    "sigma_8": 0.811,
    "n_s": 0.965
}

# Target halo
TARGET = {
    "M_vir_msun": 1e11,
    "R_vir_kpc": 15.4,
    "gas_fraction": 0.3
}


# ==================== COSMOLOGY ====================
def growth_factor_LCDM(z, Omega_m=0.315, Omega_L=0.685):
    a = 1.0 / (1.0 + z)
    def _D(a):
        if a <= 1e-10:
            return 0.0
        denom = Omega_m + Omega_L * a**3
        om = Omega_m / denom
        ol = Omega_L * a**3 / denom
        return a * 2.5 * om / (om**(4.0/7.0) - ol + (1 + 0.5*om)*(1 + ol/70.0))
    return _D(a) / _D(1.0)


def cosmic_time_Gyr(z, H0=67.4, Omega_m=0.315, Omega_L=0.685):
    H0_Gyr = 1.0 / 14.4  # approximate
    def integrand(zp):
        return 1.0 / ((1+zp) * np.sqrt(Omega_m*(1+zp)**3 + Omega_L))
    t, _ = quad(integrand, z, np.inf, limit=100)
    return t / H0_Gyr


# ==================== KSG MI ESTIMATOR ====================
def ksg_mi_2d(x, y, k=3):
    """
    Kraskov-Stögbauer-Grassberger k-NN mutual information.
    Returns MI in bits.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    N = len(x)
    if N < k + 2:
        return 0.0

    data = np.column_stack([x, y])
    tree_joint = cKDTree(data)
    tree_x = cKDTree(x.reshape(-1, 1))
    tree_y = cKDTree(y.reshape(-1, 1))

    # L-infinity norm (max norm) per KSG paper
    dists, _ = tree_joint.query(data, k=k+1, p=np.inf)
    eps = dists[:, k] + 1e-12

    n_x = np.array([tree_x.query_ball_point([x[i]], r=eps[i], p=np.inf, return_length=True) - 1
                    for i in range(N)])
    n_y = np.array([tree_y.query_ball_point([y[i]], r=eps[i], p=np.inf, return_length=True) - 1
                    for i in range(N)])

    mi = digamma(k) - np.mean(digamma(n_x + 1) + digamma(n_y + 1)) + digamma(N)
    mi_bits = max(0.0, mi) / np.log(2)
    return mi_bits


# ==================== HALO EVOLVER ====================
class CosmicHaloEvolver:
    """
    Physically-motivated halo evolution with realistic variance:
    - Variable peak height -> formation time
    - Poisson merger history
    - Variable spin parameter
    - Variable environment bias
    """

    def __init__(self,
                 grid_res=32,
                 box_size_mpc=20.0,
                 z_init=20.0,
                 z_final=0.05,
                 n_steps=16,
                 Omega_m=0.315,
                 Omega_L=0.685,
                 H0=67.4,
                 sigma_8=0.811,
                 n_s=0.965,
                 target_M_vir=1e11,
                 target_R_vir_kpc=15.4,
                 gas_fraction=0.3):

        self.grid_res = grid_res
        self.box_size = box_size_mpc
        self.cell_size = box_size_mpc / grid_res
        self.z_init = z_init
        self.z_final = z_final
        self.n_steps = n_steps
        self.Omega_m = Omega_m
        self.Omega_L = Omega_L
        self.H0 = H0
        self.sigma_8 = sigma_8
        self.n_s = n_s
        self.target_M_vir = target_M_vir
        self.target_R_vir = target_R_vir_kpc / 1000.0
        self.gas_fraction = gas_fraction

        a_init = 1.0 / (1.0 + z_init)
        a_final = 1.0 / (1.0 + z_final)
        self.a_steps = np.logspace(np.log10(a_init), np.log10(a_final), n_steps)
        self.z_steps = 1.0 / self.a_steps - 1.0
        self.t_steps = np.array([cosmic_time_Gyr(z, H0, Omega_m, Omega_L) for z in self.z_steps])

        kx = 2*np.pi * np.fft.fftfreq(grid_res, d=self.cell_size)
        self.KX, self.KY, self.KZ = np.meshgrid(kx, kx, kx, indexing='ij')
        self.k_mag = np.sqrt(self.KX**2 + self.KY**2 + self.KZ**2)
        self.k_mag[0,0,0] = 1e-10

    def _power_spectrum(self, k):
        k_eq = 0.015
        T = np.log(1 + 2.34*k/k_eq) / (2.34*k/k_eq) * \
            (1 + 3.89*k/k_eq + (16.1*k/k_eq)**2 + (5.46*k/k_eq)**3 + (6.71*k/k_eq)**4)**(-0.25)
        T = np.where(k > 1e-6, T, 1.0)
        P = k**self.n_s * T**2
        return P

    def _generate_mode_realization(self, seed, amplitude=1.0):
        np.random.seed(seed)
        white = np.random.randn(self.grid_res, self.grid_res, self.grid_res)
        white_k = np.fft.fftn(white)
        Pk = self._power_spectrum(self.k_mag)
        delta_k = white_k * np.sqrt(Pk)
        delta = np.fft.ifftn(delta_k).real
        delta = delta / np.std(delta) * amplitude
        return delta

    def evolve(self, seed, verbose=False):
        np.random.seed(seed)

        # === Halo-specific random parameters ===
        peak_height_sigma = np.clip(2.5 + 1.0 * np.random.randn(), 1.5, 4.5)
        env_bias = np.clip(0.5 + 1.0 * np.random.randn(), -1.0, 2.0)
        n_mergers = np.random.poisson(1.5)
        merger_redshifts = np.sort(np.random.uniform(0.2, 4.0, size=n_mergers)) if n_mergers > 0 else []
        merger_mass_ratios = np.random.uniform(0.05, 0.5, size=n_mergers) if n_mergers > 0 else []
        spin_lambda = np.clip(np.random.lognormal(np.log(0.035), 0.5), 0.005, 0.15)
        gas_frac = np.clip(self.gas_fraction * (0.5 + 1.0 * np.random.rand()), 0.05, 0.6)

        if verbose:
            print(f"  peak={peak_height_sigma:.2f}σ, env={env_bias:.2f}, "
                  f"mergers={n_mergers}, spin={spin_lambda:.4f}, gas={gas_frac:.2f}")

        # === Generate density field ===
        large_seed = seed * 1000 + 1
        delta_unit = self._generate_mode_realization(large_seed, amplitude=1.0)

        delta_large = delta_unit * self.sigma_8 * growth_factor_LCDM(self.z_init)
        delta_large = delta_large + env_bias * 0.3

        peak = np.array(np.unravel_index(np.argmax(delta_large), delta_large.shape))
        current_peak = delta_large[tuple(peak)]
        target_peak = peak_height_sigma * np.std(delta_large)
        delta_large = delta_large * (target_peak / max(current_peak, 0.1))

        n_samples = 1200
        sample_offsets = np.random.randint(-8, 9, size=(n_samples, 3))
        sample_indices = (peak + sample_offsets) % self.grid_res

        density_series = []
        collapse_z = None
        merger_idx = 0

        for step, (a, z, t) in enumerate(zip(self.a_steps, self.z_steps, self.t_steps)):
            D_z = growth_factor_LCDM(z)

            delta_ls = delta_unit * self.sigma_8 * D_z + env_bias * 0.3 * D_z

            z_mid = 2.5 + 0.5 * peak_height_sigma
            f_nl = 1.0 / (1.0 + np.exp((z - z_mid) / 1.2))

            delta_ss = self._generate_mode_realization(seed * 10000 + step,
                                                        amplitude=self.sigma_8 * D_z * f_nl)
            delta_ss_corr = delta_unit * self.sigma_8 * D_z * f_nl * 0.3

            delta = delta_ls * (1 - 0.4*f_nl) + delta_ss * 0.4*f_nl + delta_ss_corr * 0.3
            rho = 1.0 + delta

            peak_delta = delta[tuple(peak)]
            delta_crit = 1.686

            if peak_delta >= delta_crit * 0.65 and collapse_z is None:
                collapse_z = z
                if verbose:
                    print(f"    -> Collapse at z={z:.2f}")

            if collapse_z is not None:
                x = np.arange(self.grid_res) - peak[0]
                y = np.arange(self.grid_res) - peak[1]
                z_idx = np.arange(self.grid_res) - peak[2]
                X, Y, Z = np.meshgrid(x, y, z_idx, indexing='ij')
                X = np.where(X > self.grid_res//2, X - self.grid_res, X)
                Y = np.where(Y > self.grid_res//2, Y - self.grid_res, Y)
                Z = np.where(Z > self.grid_res//2, Z - self.grid_res, Z)
                r = np.sqrt(X**2 + Y**2 + Z**2) * self.cell_size

                r_s = self.target_R_vir / (2.16 + 2.0 * spin_lambda)
                x_nfw = r / (r_s + 1e-10)
                rho_nfw = np.zeros_like(r)
                mask = x_nfw > 0.01
                rho_nfw[mask] = 1.0 / (x_nfw[mask] * (1 + x_nfw[mask])**2)
                rho_nfw[~mask] = 1.0 / (0.01 * (1.01)**2)

                t_collapse = cosmic_time_Gyr(collapse_z)
                time_since = max(0, t_collapse - t)
                relaxation = 1.0 - np.exp(-time_since / (2.5 + spin_lambda * 10))

                R_vir = self.target_R_vir * (1.0 + 0.1 * env_bias)
                blend = np.exp(-(r / (2.5*R_vir))**2)

                merger_perturbation = np.zeros_like(rho)
                while merger_idx < len(merger_redshifts) and z < merger_redshifts[merger_idx]:
                    z_m = merger_redshifts[merger_idx]
                    mu = merger_mass_ratios[merger_idx]
                    offset = np.random.randint(-6, 7, size=3)
                    r_m = np.sqrt((X - offset[0])**2 + (Y - offset[1])**2 + (Z - offset[2])**2) * self.cell_size
                    r_s_m = r_s * mu**0.33
                    x_m = r_m / (r_s_m + 1e-10)
                    rho_m = np.zeros_like(r)
                    mask_m = x_m > 0.01
                    rho_m[mask_m] = mu / (x_m[mask_m] * (1 + x_m[mask_m])**2)
                    rho_m[~mask_m] = mu / (0.01 * (1.01)**2)
                    merger_perturbation += rho_m * np.exp(-(r_m/(2*R_vir))**2)
                    merger_idx += 1

                substructure = 0.2 * relaxation * np.random.randn(*rho.shape) * blend

                rho = (rho * (1.0 - blend*relaxation) +
                       rho_nfw * blend * relaxation +
                       merger_perturbation +
                       substructure)

                if gas_frac > 0:
                    gas = rho_nfw * gas_frac * np.exp(-(r/(1.5*R_vir))**2)
                    if spin_lambda > 0.02:
                        theta = np.arccos(Z / (r/self.cell_size + 1e-10))
                        gas *= (1 + spin_lambda * 5 * np.sin(theta)**2)
                    rho = rho + gas

            sample_densities = np.array([rho[i, j, k] for i, j, k in sample_indices])
            density_series.append(sample_densities)

        density_series = np.array(density_series)

        # === Temporal MI integration ===
        A_c = 0.0
        mi_values = []

        for i in range(self.n_steps - 1):
            rho_t = density_series[i]
            rho_tp1 = density_series[i+1]

            rho_t_norm = (rho_t - np.mean(rho_t)) / (np.std(rho_t) + 1e-12)
            rho_tp1_norm = (rho_tp1 - np.mean(rho_tp1)) / (np.std(rho_tp1) + 1e-12)

            mi = ksg_mi_2d(rho_t_norm, rho_tp1_norm, k=3)
            A_c += mi
            mi_values.append(mi)

        return {
            'seed': seed,
            'A_c_bits': float(A_c),
            'mi_values': [float(m) for m in mi_values],
            'collapse_z': float(collapse_z) if collapse_z else None,
            'z_form': float(collapse_z) if collapse_z else self.z_final,
            'peak_height_sigma': float(peak_height_sigma),
            'env_bias': float(env_bias),
            'n_mergers': int(n_mergers),
            'spin_lambda': float(spin_lambda),
            'gas_frac': float(gas_frac),
        }


# ==================== ENSEMBLE RUNNER ====================
def run_single_halo(seed):
    evolver = CosmicHaloEvolver(
        grid_res=GRID_RES,
        box_size_mpc=BOX_SIZE_MPC,
        z_init=Z_INIT,
        z_final=Z_FINAL,
        n_steps=N_STEPS,
        **COSMO,
        **TARGET
    )
    return evolver.evolve(seed)


def main():
    print("="*65)
    print("CLOUD-9 NULL ENSEMBLE GENERATOR v3 — KSG TEMPORAL MI")
    print("="*65)
    print(f"N_HALOS: {N_HALOS} | GRID: {GRID_RES}^3 | STEPS: {N_STEPS}")
    print(f"Workers: {N_WORKERS}")
    print("Integrating I[\u03c1(t); \u03c1(t+\u0394t)] via KSG k-NN over cosmic time.")
    print("")

    start = time.time()

    with mp.Pool(N_WORKERS) as pool:
        seeds = list(range(SEED_BASE, SEED_BASE + N_HALOS))
        ensemble = pool.map(run_single_halo, seeds)

    elapsed = time.time() - start
    A_c_values = np.array([h['A_c_bits'] for h in ensemble])

    # Statistics
    null_mean = float(np.mean(A_c_values))
    null_std = float(np.std(A_c_values))
    null_median = float(np.median(A_c_values))
    p16 = float(np.percentile(A_c_values, 16))
    p84 = float(np.percentile(A_c_values, 84))
    p95 = float(np.percentile(A_c_values, 95))
    p99 = float(np.percentile(A_c_values, 99))
    p2_5 = float(np.percentile(A_c_values, 2.5))
    p97_5 = float(np.percentile(A_c_values, 97.5))

    z_score = (CLOUD9_A_C - null_mean) / null_std if null_std > 0 else 0

    print(f"Completed in {elapsed:.1f}s ({elapsed/N_HALOS:.2f}s per halo)")
    print("")
    print("="*65)
    print("RESULTS")
    print("="*65)
    print(f"\nNull Distribution (N={N_HALOS}):")
    print(f"  Mean:      {null_mean:.4f} bits")
    print(f"  Std:       {null_std:.4f} bits")
    print(f"  Median:    {null_median:.4f} bits")
    print(f"  16-84:     [{p16:.4f}, {p84:.4f}]")
    print(f"  95th:      {p95:.4f}")
    print(f"  99th:      {p99:.4f}")
    print(f"  2.5-97.5:  [{p2_5:.4f}, {p97_5:.4f}]")
    print(f"  Min:       {float(np.min(A_c_values)):.4f}")
    print(f"  Max:       {float(np.max(A_c_values)):.4f}")
    print(f"  CV:        {null_std/null_mean*100:.2f}%")

    print(f"\nCloud-9 Comparison:")
    print(f"  Cloud-9 A_c:  {CLOUD9_A_C:.1f} ± {CLOUD9_SYSTEMATIC:.1f} bits")
    print(f"  Null mean:      {null_mean:.4f} ± {null_std:.4f} bits")
    print(f"  Z-score:        {z_score:.4f}\u03c3")

    if z_score >= 5.0:
        sig_str = "\U0001f389 DISCOVERY"
    elif z_score >= 3.0:
        sig_str = "\u2705 SIGNIFICANT"
    elif z_score >= 2.0:
        sig_str = "\u26a0\ufe0f MARGINAL"
    else:
        sig_str = "\u274c NOT SIGNIFICANT"
    print(f"  Significance:   {sig_str}")

    # ==================== PLOT ====================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax1 = axes[0]
    ax1.hist(A_c_values, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(CLOUD9_A_C, color='red', linestyle='--', linewidth=3, label=f'Cloud-9 = {CLOUD9_A_C}')
    ax1.axvline(null_mean, color='green', linestyle='--', linewidth=2, label=f'Null \u03bc = {null_mean:.1f}')
    ax1.axvline(null_mean + 2*null_std, color='orange', linestyle=':', alpha=0.8, label=f'2\u03c3')
    ax1.axvline(null_mean + 3*null_std, color='purple', linestyle=':', alpha=0.8, label=f'3\u03c3')
    ax1.axvline(null_mean + 5*null_std, color='brown', linestyle=':', alpha=0.8, label=f'5\u03c3')
    ax1.set_xlabel('Assembly Index A_c (bits)', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title(f'Null Ensemble Distribution (N = {N_HALOS})', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3)

    ax2 = axes[1]
    sorted_Ac = np.sort(A_c_values)
    cumulative = np.arange(1, len(sorted_Ac)+1) / len(sorted_Ac)
    ax2.plot(sorted_Ac, cumulative, color='steelblue', linewidth=2.5)
    ax2.axvline(CLOUD9_A_C, color='red', linestyle='--', linewidth=3, label=f'Cloud-9')
    ax2.axhline(0.99, color='brown', linestyle=':', alpha=0.7, label='99th percentile')
    ax2.axhline(0.95, color='purple', linestyle=':', alpha=0.7, label='95th percentile')
    ax2.axhline(0.90, color='orange', linestyle=':', alpha=0.7, label='90th percentile')
    ax2.set_xlabel('A_c (bits)', fontsize=12)
    ax2.set_ylabel('Cumulative Fraction', fontsize=12)
    ax2.set_title('Cumulative Distribution', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('cloud9_null_ensemble_v3.png', dpi=200, bbox_inches='tight')
    print(f"\nPlot saved to: cloud9_null_ensemble_v3.png")

    # ==================== JSON OUTPUT ====================
    result_json = {
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "pipeline_version": "3.0-KSG",
        "n_halos": N_HALOS,
        "grid_resolution": GRID_RES,
        "n_time_steps": N_STEPS,
        "cosmology": COSMO,
        "target_halo": TARGET,
        "null_distribution": {
            "mean": round(null_mean, 4),
            "std": round(null_std, 4),
            "median": round(null_median, 4),
            "percentile_16": round(p16, 4),
            "percentile_84": round(p84, 4),
            "percentile_95": round(p95, 4),
            "percentile_99": round(p99, 4),
            "percentile_2_5": round(p2_5, 4),
            "percentile_97_5": round(p97_5, 4),
            "min": round(float(np.min(A_c_values)), 4),
            "max": round(float(np.max(A_c_values)), 4)
        },
        "cloud9_comparison": {
            "cloud9_measured": CLOUD9_A_C,
            "cloud9_systematic": CLOUD9_SYSTEMATIC,
            "null_mean": round(null_mean, 4),
            "null_std": round(null_std, 4),
            "z_score": round(z_score, 4),
            "significance": "discovery" if z_score >= 5 else "significant" if z_score >= 3 else "marginal" if z_score >= 2 else "none"
        },
        "ensemble_members": ensemble,
        "disclaimer": "Semi-analytic evolution. For publication, validate against Gadget-4/IllustrisTNG halos."
    }

    with open('cloud9_null_ensemble_v3.json', 'w') as f:
        json.dump(result_json, f, indent=2)

    print(f"JSON saved to: cloud9_null_ensemble_v3.json")
    print("\n" + "="*65)
    print("DONE")
    print("="*65)


if __name__ == "__main__":
    main()
