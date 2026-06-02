"""
Koushiappas Modified Friedmann Solver
=====================================
Implements the deformed commutator cosmology from:
    S. M. Koushiappas, "A Cosmological Uncertainty Relation and 
    Late-Universe Acceleration", arXiv:2604.27771 (2026).

Core equation (Eq. 23 of paper):
    H^2 + Î²^2 [1 + (a/a_0)^n]^2 = (8ÏG/3)Ï + Îc^2/3

Late-universe dimensionless form (Eq. 48):
    E^2(z) = Î©_r(1+z)^4 + Î©_m(1+z)^3 + Î©_Î 
             - Îµ^2 [ 2(1+z)^{-n} + (1+z)^{-2n} ]
where Î² = Îµ H_0 and a_0 = a_today = 1.

Effective equation of state (Eq. 30):
    w_1 = -1 - n/3
    w_2 = -1 - 2n/3

Caveat: Paper explicitly states this model does NOT resolve 
the Hubble tension; in fact it slightly worsens it for n>0.
"""

import numpy as np
from scipy.integrate import odeint, quad
from scipy.interpolate import CubicSpline
import warnings

class KoushiappasCosmology:
    """
    Background cosmology with deformed [a, a_dot] commutator.

    Parameters
    ----------
    n : float
        Deformation exponent. 
        n > 0  â late-time acceleration with w_eff > -1 (quintessence-like)
        n < -2 â classical bounce regime
    epsilon : float
        Dimensionless deformation strength, Î² = Îµ H_0.
        Paper uses cosmological regime: Îµ âª 1 (e.g., 0.01â0.1).
    Omega_m : float
        Matter density parameter today.
    Omega_Lambda : float
        Bare cosmological constant density parameter.
    Omega_r : float
        Radiation density parameter today.
    h : float
        Hubble parameter today in units of 100 km/s/Mpc.
    a0 : float
        Crossover scale factor (paper sets a0 = a_today = 1 for late universe).
    """

    def __init__(self, n=0.5, epsilon=0.05, Omega_m=0.315, 
                 Omega_Lambda=0.685, Omega_r=9.2e-5, h=0.674, a0=1.0):
        self.n = float(n)
        self.epsilon = float(epsilon)
        self.Omega_m = float(Omega_m)
        self.Omega_Lambda = float(Omega_Lambda)
        self.Omega_r = float(Omega_r)
        self.h = float(h)
        self.a0 = float(a0)
        self.H0 = 100.0 * h  # km/s/Mpc

        # Effective Lambda after constant shift (Eq. 29)
        self.Omega_Lambda_eff = self.Omega_Lambda - self.epsilon**2

        if self.n > 0 and self.epsilon > 0.3:
            warnings.warn("epsilon=%.2f may violate cosmological regime (epsilon<<1)" % self.epsilon)
        if self.Omega_Lambda_eff < 0:
            raise ValueError("Omega_Lambda_eff = %.4f < 0. epsilon too large." % self.Omega_Lambda_eff)

    def E2(self, z):
        """
        Dimensionless Hubble parameter squared, E^2(z) = H^2(z)/H_0^2.
        Eq. 48 of Koushiappas (2026).
        """
        zp1 = 1.0 + z
        std = (self.Omega_r * zp1**4 + 
               self.Omega_m * zp1**3 + 
               self.Omega_Lambda_eff)
        nc = self.epsilon**2 * (2.0 * zp1**(-self.n) + zp1**(-2.0*self.n))
        return std - nc

    def H(self, z):
        """Hubble parameter in km/s/Mpc."""
        e2 = self.E2(z)
        if np.any(e2 < 0):
            return np.nan
        return self.H0 * np.sqrt(e2)

    def H_a(self, a):
        """Hubble parameter as function of scale factor."""
        z = 1.0/a - 1.0
        return self.H(z)

    def w_eff(self, z):
        """
        Effective equation of state parameter of the NC fluid.
        """
        zp1 = 1.0 + z
        rho1 = 2.0 * self.epsilon**2 * zp1**(-self.n)
        rho2 = self.epsilon**2 * zp1**(-2.0*self.n)
        total = rho1 + rho2
        if total == 0:
            return -1.0
        w1 = -1.0 - self.n / 3.0
        w2 = -1.0 - 2.0 * self.n / 3.0
        return (w1 * rho1 + w2 * rho2) / total

    def comoving_distance(self, z):
        """Line-of-sight comoving distance in Mpc."""
        c = 299792.458  # km/s
        integrand = lambda zz: c / self.H(zz)
        dist, _ = quad(integrand, 0, z, limit=100)
        return dist

    def _growth_ode(self, D, lna, params):
        """
        Linear growth factor ODE in ln(a).
        """
        a = np.exp(lna)
        z = 1.0/a - 1.0

        h_val = self.H(z)
        if not np.isfinite(h_val) or h_val <= 0:
            return [0.0, 0.0]

        dz = 1e-4
        hp = (self.H(z+dz) - self.H(z-dz)) / (2*dz)
        dH_dlna = - (1.0 + z) * hp

        rho_m_z = self.Omega_m * (1.0+z)**3
        e2 = self.E2(z)
        if e2 <= 0:
            return [0.0, 0.0]
        Omega_m_z = rho_m_z / e2

        D_val, dD_dlna = D
        d2D_dlna2 = -(2.0 + dH_dlna/h_val) * dD_dlna + 1.5 * Omega_m_z * D_val

        return [dD_dlna, d2D_dlna2]

    def growth_factor(self, z_array):
        """
        Compute linear growth factor D(z) normalized to D(z=0)=1.
        """
        z_array = np.atleast_1d(z_array)
        a_early = 1e-8
        lna_grid = np.linspace(np.log(a_early), 0.0, 1000)
        D_init = [a_early, a_early]

        sol = odeint(self._growth_ode, D_init, lna_grid, args=(None,))
        D_grid = sol[:, 0]
        a_grid = np.exp(lna_grid)
        z_grid = 1.0/a_grid - 1.0

        D_grid /= D_grid[-1]

        cs = CubicSpline(z_grid[::-1], D_grid[::-1])
        return cs(z_array)

    def sigma8_ratio(self, z):
        """
        Ratio of sigma8(z) in Koushiappas model vs ÎCDM.
        """
        D_k = self.growth_factor(z)
        lcdm = KoushiappasCosmology(n=0, epsilon=0, 
                                     Omega_m=self.Omega_m,
                                     Omega_Lambda=self.Omega_Lambda,
                                     Omega_r=self.Omega_r,
                                     h=self.h)
        D_lcdm = lcdm.growth_factor(z)
        return D_k / D_lcdm


def generate_koushiappas_background(n=0.5, epsilon=0.05, z_max=10.0, nz=200):
    """
    Generate background cosmology arrays for use in N-body or semi-analytic pipelines.
    """
    cosmo = KoushiappasCosmology(n=n, epsilon=epsilon)
    z = np.linspace(0, z_max, nz)

    H = np.array([cosmo.H(zi) for zi in z])
    w = np.array([cosmo.w_eff(zi) for zi in z])
    D = cosmo.growth_factor(z)

    dc = np.zeros_like(z)
    c = 299792.458
    for i in range(1, len(z)):
        dc[i] = dc[i-1] + c * (z[i]-z[i-1]) / (0.5*(H[i]+H[i-1]))

    return {
        'z': z,
        'a': 1.0/(1.0+z),
        'H': H,
        'E2': cosmo.E2(z),
        'w_eff': w,
        'D': D,
        'Dc': dc,
        'n': n,
        'epsilon': epsilon,
        'params': {
            'Omega_m': cosmo.Omega_m,
            'Omega_Lambda_eff': cosmo.Omega_Lambda_eff,
            'h': cosmo.h
        }
    }


if __name__ == '__main__':
    print("=== Koushiappas Cosmology Validation ===")

    k = KoushiappasCosmology(n=0.5, epsilon=0.05)
    print("Late-time regime (n=%.1f, epsilon=%.2f):" % (k.n, k.epsilon))
    print("  w_eff at z=0: %.4f (paper: w > -1)" % k.w_eff(0))
    print("  w_eff at z=1: %.4f" % k.w_eff(1))
    print("  H(z=0): %.2f km/s/Mpc" % k.H(0))
    print("  Omega_Lambda_eff: %.4f" % k.Omega_Lambda_eff)
    print("  Growth factor D(z=1): %.4f" % k.growth_factor(1.0))

    lcdm = KoushiappasCosmology(n=0, epsilon=0)
    print("LambdaCDM comparison:")
    print("  D(z=1): %.4f" % lcdm.growth_factor(1.0))
    print("  sigma8 ratio Koushiappas/LCDM at z=0: %.4f" % k.sigma8_ratio(0.0))
    print("  sigma8 ratio at z=1: %.4f" % k.sigma8_ratio(1.0))
