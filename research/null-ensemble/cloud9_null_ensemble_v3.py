#!/usr/bin/env python3
"""
Cloud-9 Null Ensemble Generator v3 — KSG TEMPORAL MI
Experimental pipeline using Kraskov-Stögbauer-Grassberger
k-NN mutual information integrated over cosmic time.

This is a synthetic/prototype null-model implementation for methodological
study. It is not a like-for-like reproduction of an IllustrisTNG halo
catalogue and its output should not be described as an observational
discovery significance without independent validation.

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
    print(f"N_HALOS: {N_HALOS}")
    print(f"Workers: {N_WORKERS}")
    print(f"Grid: {GRID_RES}^3, {N_STEPS} time steps, {1200} samples/step")
    print(f"Target A_c: {CLOUD9_A_C} ± {CLOUD9_SYSTEMATIC} bits")
    print("NOTE: synthetic/prototype null model; not direct IllustrisTNG data")

    t0 = time.time()
    seeds = [SEED_BASE + i for i in range(N_HALOS)]

    if N_WORKERS > 1:
        with mp.Pool(N_WORKERS) as pool:
            results = pool.map(run_single_halo, seeds)
    else:
        results = [run_single_halo(s) for s in seeds]

    A_values = np.array([r['A_c_bits'] for r in results])
    mean = float(np.mean(A_values))
    std = float(np.std(A_values, ddof=1))
    median = float(np.median(A_values))
    z = (CLOUD9_A_C - mean) / std if std > 0 else float('nan')

    output = {
        'run_timestamp': datetime.utcnow().isoformat() + 'Z',
        'pipeline_version': '3.0-KSG-fast',
        'status': 'experimental synthetic null model',
        'n_halos': N_HALOS,
        'grid_resolution': GRID_RES,
        'n_time_steps': N_STEPS,
        'n_samples_per_step': 1200,
        'cosmology': COSMO,
        'target_halo': TARGET,
        'null_distribution': {
            'mean': mean,
            'std': std,
            'median': median,
            'percentile_16': float(np.percentile(A_values, 16)),
            'percentile_84': float(np.percentile(A_values, 84)),
            'percentile_95': float(np.percentile(A_values, 95)),
            'percentile_99': float(np.percentile(A_values, 99)),
            'percentile_2_5': float(np.percentile(A_values, 2.5)),
            'percentile_97_5': float(np.percentile(A_values, 97.5)),
            'min': float(np.min(A_values)),
            'max': float(np.max(A_values))
        },
        'cloud9_comparison': {
            'cloud9_measured': CLOUD9_A_C,
            'cloud9_systematic': CLOUD9_SYSTEMATIC,
            'null_mean': mean,
            'null_std': std,
            'z_score': float(z),
            'significance': 'exploratory; not a discovery claim'
        },
        'ensemble_members': results,
        'runtime_seconds': time.time() - t0,
        'reproducibility': {
            'seed_base': SEED_BASE,
            'seeds': seeds,
            'data_source': 'synthetic model; no IllustrisTNG catalogue fetched'
        }
    }

    with open('cloud9_null_ensemble_v3.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nCompleted in {time.time()-t0:.1f}s")
    print(f"Null mean: {mean:.4f} bits")
    print(f"Null std:  {std:.4f} bits")
    print(f"Cloud-9 A_c: {CLOUD9_A_C:.4f} bits")
    print(f"Exploratory z-score: {z:.4f}σ")
    print("Saved: cloud9_null_ensemble_v3.json")


if __name__ == '__main__':
    main()
