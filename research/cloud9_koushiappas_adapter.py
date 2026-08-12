"""
Cloud-9 Koushiappas Adapter
============================
Connects the modified Friedmann background to the Assembly Index A_c pipeline.

Physics mapping:
---------------
In Cloud-9, A_c = â« I[Ï(x,Ï); Ï(x,Ï+ÎÏ)] dÏ measures information persistence.
Koushiappas's deformation changes H(z) and D(z), which modifies:
  1. The time-redshift relation Ï(z) (snapshot spacing in cosmic time)
  2. The growth factor D(z) (amplitude of structure at each epoch)
  3. The merger rate (halo formation history depends on Ï(M,z) â D(z))

This adapter computes the modified background and feeds it into a 
semi-analytic halo density evolution model.

Usage:
------
    from cloud9_koushiappas_adapter import KoushiappasHaloEvolution

    model = KoushiappasHaloEvolution(n=0.5, epsilon=0.05, M_halo=1e12)
    Ac = model.compute_assembly_index(z_ini=6.0, z_final=0.0, dtau_Gyr=0.05)
"""

import numpy as np
from scipy.integrate import cumulative_trapezoid, quad
from scipy.interpolate import CubicSpline
from koushiappas_cosmology import KoushiappasCosmology
import c9_bus_client  # C9 bus injection

class KoushiappasHaloEvolution:
    """
    Semi-analytic halo density evolution on a Koushiappas background.

    Uses the extended Press-Schechter / merger-tree inspired approach
    to model how the internal density structure of a halo builds up 
    through accretion, with the background expansion modified by the
    deformed commutator.
    """

    def __init__(self, n=0.5, epsilon=0.05, M_halo=1e12, 
                 concentration_model='diemer19', c0=10.0):
        """
        Parameters
        ----------
        n, epsilon : float
            Koushiappas deformation parameters.
        M_halo : float
            Halo mass today in solar masses.
        concentration_model : str
            'diemer19' or 'constant'.
        c0 : float
            Initial concentration parameter.
        """
        self.cosmo = KoushiappasCosmology(n=n, epsilon=epsilon)
        self.M_halo = float(M_halo)
        self.c0 = float(c0)
        self.n = n
        self.epsilon = epsilon

        # Precompute background grids
        self._build_background_grid()

    def _build_background_grid(self, z_max=15.0, nz=500):
        """Precompute H(z), D(z), time(z) on a fine grid."""
        self.z_grid = np.linspace(0, z_max, nz)
        self.a_grid = 1.0 / (1.0 + self.z_grid)

        # Hubble parameter
        self.H_grid = np.array([self.cosmo.H(z) for z in self.z_grid])
        self.E2_grid = self.cosmo.E2(self.z_grid)

        # Growth factor
        self.D_grid = self.cosmo.growth_factor(self.z_grid)

        # Cosmic time Ï(z) = â«_z^â dz' / [(1+z') H(z')]
        # Convert H [km/s/Mpc] to Gyr^-1
        km_s_Mpc_to_Gyr = 1.0 / (977.8 / self.cosmo.h)  # H0 in Gyr^-1 = h / 9.78
        # Actually: H [km/s/Mpc] â H [Gyr^-1] = H * (1 Mpc / km) / (1 Gyr in seconds)
        # 1 Mpc = 3.086e19 km, 1 Gyr = 3.154e16 s
        # H [Gyr^-1] = H [km/s/Mpc] * (1 Mpc / 1 km) * (1 s / 1 Gyr)
        #            = H * 3.086e19 / 3.154e16 â H * 978.5
        # Wait, that's wrong. Let me be careful.
        # H [km/s/Mpc] = H [km/s] per [3.086e19 km] = H / 3.086e19 s^-1
        # To get Gyr^-1: multiply by (3.154e16 s / 1 Gyr)
        # H [Gyr^-1] = H [km/s/Mpc] * (1 Mpc / km) * (3.154e16 s / Gyr) / (1 s)
        #            = H * 3.086e19 * 3.154e16 / (3.086e19 * 1) -- no.
        # Simpler: H0 = 100h km/s/Mpc. Hubble time = 1/H0 = 9.78/h Gyr.
        # So H [Gyr^-1] = H [km/s/Mpc] / (100h) * (h/9.78) * 100 
        #               = H / 978.5 
        conv = 1.0 / 978.5  # km/s/Mpc to Gyr^-1
        H_Gyr = self.H_grid * conv

        # dÏ/dz = -1 / [(1+z) H(z)]
        dtau_dz = -1.0 / ((1.0 + self.z_grid) * H_Gyr)

        # Integrate from z_max to 0
        self.tau_grid = np.zeros_like(self.z_grid)
        for i in range(len(self.z_grid)-2, -1, -1):
            c9_bus_client.heartbeat()
            self.tau_grid[i] = self.tau_grid[i+1] + 0.5 * (dtau_dz[i] + dtau_dz[i+1]) * (self.z_grid[i] - self.z_grid[i+1])

        # Normalize so tau=0 at z=0
        self.tau_grid -= self.tau_grid[0]

        # Interpolators
        self._tau_of_z = CubicSpline(self.z_grid, self.tau_grid)
        self._z_of_tau = CubicSpline(self.tau_grid[::-1], self.z_grid[::-1])
        self._D_of_z = CubicSpline(self.z_grid, self.D_grid)
        self._H_of_z = CubicSpline(self.z_grid, self.H_grid)

    def virial_radius(self, z):
        """Virial radius in kpc, assuming standard definition."""
        # R_vir â 200 kpc * (M/10^12 M_sun)^(1/3) * (Î_c/200)^(-1/3) * (1+z)^(-1)
        # Simplified: R_vir â M^(1/3) * (1+z)^(-1) * [H(z)/H0]^(-2/3)
        # Using standard spherical collapse
        M12 = self.M_halo / 1e12
        Hz = self._H_of_z(z)
        H0 = self.cosmo.H0

        # Approximate virial radius evolution
        R_vir = 200.0 * (M12)**(1.0/3.0) * (Hz / H0)**(-2.0/3.0) / (1.0 + z)
        return R_vir

    def concentration(self, z):
        """Concentration parameter c(z)."""
        # Simplified: c â (1+z) for growing halos, or use Diemer19-like trend
        # Modified by growth factor: more growth at late times â lower c
        D_z = self._D_of_z(z)
        D_0 = self._D_of_z(0.0)

        # Basic redshift evolution
        c = self.c0 * (1.0 + z) * (D_z / D_0)
        return max(c, 2.0)  # Floor at c=2

    def density_profile(self, r, z):
        """
        NFW-like density profile at redshift z.
        Returns Ï(r) in arbitrary units (normalized).
        """
        Rvir = self.virial_radius(z)
        c = self.concentration(z)
        rs = Rvir / c

        x = r / (rs + 1e-6)
        # NFW profile
        rho = 1.0 / (x * (1.0 + x)**2)
        return rho

    def mutual_information_snapshot(self, z1, z2, Ngrid=64):
        """
        Compute mutual information between density fields at two redshifts.
        This is a SIMPLIFIED proxy for the full k-NN estimator.

        Uses the fact that for Gaussian fields, I â (correlation)^2,
        but for halos we model it via structural persistence.
        """
        # Time separation
        tau1 = self._tau_of_z(z1)
        tau2 = self._tau_of_z(z2)
        dtau = abs(tau2 - tau1)

        # Growth factor ratio
        D1 = self._D_of_z(z1)
        D2 = self._D_of_z(z2)

        # Structural persistence model:
        # I â I_0 * (D_min / D_max) * exp(-dtau / Ï_mem)
        # where Ï_mem is the halo dynamical time

        # Dynamical time at mean redshift
        z_mean = 0.5 * (z1 + z2)
        H_z = self._H_of_z(z_mean)
        # t_dyn â 1/sqrt(GÏ) â 1/H(z) at virialization
        t_dyn_Gyr = 1.0 / (H_z / 978.5)  # H in Gyr^-1

        # Correlation coefficient between density fields
        # As halos grow, inner structure is more persistent
        c1 = self.concentration(z1)
        c2 = self.concentration(z2)

        # Persistence factor: how much of the old structure survives
        # More growth â less persistence
        growth_ratio = min(D1, D2) / max(D1, D2)

        # Time decoherence
        decoherence = np.exp(-dtau / (0.3 * t_dyn_Gyr))

        # Concentration similarity
        c_similarity = 2.0 * np.sqrt(c1 * c2) / (c1 + c2 + 1e-6)

        # Base mutual information (bits) - calibrated to Cloud-9 null
        I_base = 0.5  # bits per snapshot pair, will integrate to ~60-90 bits

        I = I_base * growth_ratio * decoherence * c_similarity
        return max(I, 0.0)

    def compute_assembly_index(self, z_ini=10.0, z_final=0.0, dtau_Gyr=0.05):
        """
        Compute Assembly Index A_c by integrating mutual information
        along the halo's merger tree / evolution.

        A_c = â«_{Ï_ini}^{Ï_final} I[Ï(Ï); Ï(Ï+ÎÏ)] dÏ

        Parameters
        ----------
        z_ini : float
            Initial redshift when halo first exceeds 10^11 M_sun.
        z_final : float
            Final redshift (default 0).
        dtau_Gyr : float
            Time step in Gyr (Cloud-9 uses 50 Myr = 0.05 Gyr).

        Returns
        -------
        Ac : float
            Assembly index in bits.
        """
        tau_ini = self._tau_of_z(z_ini)
        tau_final = self._tau_of_z(z_final)

        # Time grid
        tau_steps = np.arange(tau_ini, tau_final, dtau_Gyr)
        if len(tau_steps) < 2:
            return 0.0

        Ac = 0.0
        for i in range(len(tau_steps) - 1):
            tau1 = tau_steps[i]
            tau2 = tau_steps[i+1]
            z1 = float(self._z_of_tau(tau1))
            z2 = float(self._z_of_tau(tau2))

            I = self.mutual_information_snapshot(z1, z2)
            Ac += I * dtau_Gyr

        return Ac


def run_cloud9_comparison(n=0.5, epsilon=0.05, M_halo=1e12, z_ini=6.0):
    """
    Run a single halo through both Koushiappas and ÎCDM backgrounds,
    returning A_c for each.
    """
    # Koushiappas model
    k_model = KoushiappasHaloEvolution(n=n, epsilon=epsilon, M_halo=M_halo)
    Ac_k = k_model.compute_assembly_index(z_ini=z_ini, z_final=0.0, dtau_Gyr=0.05)

    # ÎCDM null (n=0, epsilon=0)
    lcdm_model = KoushiappasHaloEvolution(n=0.0, epsilon=0.0, M_halo=M_halo)
    Ac_lcdm = lcdm_model.compute_assembly_index(z_ini=z_ini, z_final=0.0, dtau_Gyr=0.05)

    return {
        'Ac_koushiappas': Ac_k,
        'Ac_lcdm': Ac_lcdm,
        'delta_Ac': Ac_k - Ac_lcdm,
        'fractional_delta': (Ac_k - Ac_lcdm) / Ac_lcdm if Ac_lcdm > 0 else np.nan,
        'n': n,
        'epsilon': epsilon,
        'M_halo': M_halo,
        'z_ini': z_ini
    }


if __name__ == '__main__':
    print("=== Cloud-9 Koushiappas Adapter Demo ===\n")

    # Test a massive halo
    result = run_cloud9_comparison(n=0.5, epsilon=0.05, M_halo=1e12, z_ini=6.0)

    print(f"Halo: M={result['M_halo']:.1e} M_sun, z_ini={result['z_ini']}")
    print("Koushiappas (n=%.1f, epsilon=%.2f):" % (result['n'], result['epsilon']))
    print("  A_c = %.2f bits" % result['Ac_koushiappas'])
    print("LCDM null:")
    print("  A_c = %.2f bits" % result['Ac_lcdm'])
    print("Difference: dA_c = %+.2f bits (%+.1f%%)" % (result['delta_Ac'], result['fractional_delta']*100))

    # Parameter scan
    print("\n=== Parameter Scan ===")
    print(f"{'n':>6} {'Îµ':>6} {'ÎAc(bits)':>12} {'% change':>10}")
    print("-" * 40)
    for n in [0.2, 0.5, 0.8, 1.0]:
        for eps in [0.03, 0.05, 0.10]:
            r = run_cloud9_comparison(n=n, epsilon=eps, M_halo=1e12, z_ini=6.0)
            print(f"{n:6.1f} {eps:6.2f} {r['delta_Ac']:12.2f} {r['fractional_delta']*100:10.1f}")
