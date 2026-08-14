"""
Cloud-9 Null Model: Koushiappas vs ÎCDM Ensemble
=================================================

Design philosophy:
-----------------
The Koushiappas deformation modifies the BACKGROUND expansion only.
It preserves the scale-invariant primordial power spectrum (paper, Sec. IV).
Therefore, the proper null model is:
  - IDENTICAL initial Gaussian density field
  - IDENTICAL halo selection criteria (final mass, formation redshift)
  - DIFFERENT background cosmology (ÎCDM vs deformed)

This isolates the pure geometric effect on A_c.

Statistical protocol:
--------------------
1. Generate N_sims realizations of initial conditions.
2. Evolve each through:
   a) Standard ÎCDM background
   b) Koushiappas background (same n, Îµ for all ensemble members)
3. Identify halos at z=0 with M â [M_min, M_max].
4. For each halo, compute A_c from z_ini to z=0.
5. Build null distribution from (a), test (b) against it.

Caveats enforced:
-----------------
- Paper states model does NOT resolve H0 tension (Sec. VIII).
  Do NOT claim Hubble-tension relief from A_c alone.
- For n>0, w_eff > -1 (quintessence-like). This is the ONLY 
  regime directly comparable to late-universe Cloud-9 targets.
- For n<-2 (bounce regime), initial conditions are fundamentally
  different; CANNOT use ÎCDM null ensemble. Requires separate bounce sims.
"""

import numpy as np
from scipy import stats
from cloud9_koushiappas_adapter import KoushiappasHaloEvolution, run_cloud9_comparison
import c9_bus_client  # C9 bus injection

class KoushiappasNullEnsemble:
    """
    Generates and compares matched ensembles of halo assembly histories.
    """

    def __init__(self, n=0.5, epsilon=0.05, N_ensemble=1000,
                 M_min=1e11, M_max=1e13, z_ini=6.0, dtau_Gyr=0.05,
                 seed=42):
        """
        Parameters
        ----------
        n, epsilon : float
            Koushiappas deformation parameters.
        N_ensemble : int
            Number of halos in null ensemble.
        M_min, M_max : float
            Halo mass range today [M_sun].
        z_ini : float
            Formation redshift for A_c integral.
        dtau_Gyr : float
            Time step for A_c integration.
        seed : int
            Random seed for reproducibility.
        """
        self.n = n
        self.epsilon = epsilon
        self.N_ensemble = N_ensemble
        self.M_min = M_min
        self.M_max = M_max
        self.z_ini = z_ini
        self.dtau_Gyr = dtau_Gyr
        self.rng = np.random.RandomState(seed)

    def _draw_halo_mass(self):
        """Draw halo mass from a power-law distribution dN/dM ~ M^-1.9."""
        # Cumulative: N(>M) ~ M^(-1.9+1) = M^(-0.9)
        # Draw uniform in CDF space
        u = self.rng.uniform(0, 1, size=self.N_ensemble)
        alpha = 0.9  # from power-law index -1.9
        M = (self.M_min**(-alpha) + u * (self.M_max**(-alpha) - self.M_min**(-alpha)))**(-1.0/alpha)
        return M

    def generate_null_distribution(self):
        """
        Generate ÎCDM null ensemble.
        Returns array of A_c values.
        """
        masses = self._draw_halo_mass()
        Ac_null = np.zeros(self.N_ensemble)

        print(f"Generating ÎCDM null ensemble (N={self.N_ensemble})...")
        for i, M in enumerate(masses):
            if i % 100 == 0:
                print(f"  ... {i}/{self.N_ensemble}")
            result = run_cloud9_comparison(n=0.0, epsilon=0.0, 
                                          M_halo=M, z_ini=self.z_ini)
            Ac_null[i] = result['Ac_lcdm']

        return Ac_null

    def generate_test_distribution(self):
        """
        Generate Koushiappas test ensemble with SAME mass draws.
        Returns array of A_c values.
        """
        masses = self._draw_halo_mass()
        Ac_test = np.zeros(self.N_ensemble)

        print(f"Generating Koushiappas test ensemble (n={self.n}, Îµ={self.epsilon})...")
        for i, M in enumerate(masses):
            if i % 100 == 0:
                print(f"  ... {i}/{self.N_ensemble}")
            result = run_cloud9_comparison(n=self.n, epsilon=self.epsilon,
                                          M_halo=M, z_ini=self.z_ini)
            Ac_test[i] = result['Ac_koushiappas']

        return Ac_test

    def statistical_test(self, Ac_null=None, Ac_test=None, 
                        sigma_threshold=3.0):
        """
        Perform two-sample statistical test.

        Returns dict with z-score, p-value, and significance.
        """
        if Ac_null is None:
            Ac_null = self.generate_null_distribution()
        if Ac_test is None:
            Ac_test = self.generate_test_distribution()

        # Null statistics
        mu_null = np.mean(Ac_null)
        sigma_null = np.std(Ac_null)

        # Test statistics
        mu_test = np.mean(Ac_test)
        sigma_test = np.std(Ac_test)

        # Standardized mean difference
        # If test mean > null mean:
        z_score = (mu_test - mu_null) / (sigma_null / np.sqrt(self.N_ensemble))

        # Two-sample t-test
        t_stat, p_value = stats.ttest_ind(Ac_test, Ac_null, equal_var=False)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((sigma_null**2 + sigma_test**2) / 2.0)
        cohens_d = (mu_test - mu_null) / pooled_std if pooled_std > 0 else 0.0

        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.ks_2samp(Ac_test, Ac_null)

        return {
            'mu_null': mu_null,
            'sigma_null': sigma_null,
            'mu_test': mu_test,
            'sigma_test': sigma_test,
            'z_score': z_score,
            'p_value_ttest': p_value,
            'cohens_d': cohens_d,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_p,
            'significant_3sigma': abs(z_score) > sigma_threshold,
            'N_ensemble': self.N_ensemble,
            'n': self.n,
            'epsilon': self.epsilon
        }

    def sensitivity_forecast(self, epsilon_grid=None, n_grid=None):
        """
        Forecast: what Îµ and N are needed for 3Ï detection?
        """
        if epsilon_grid is None:
            epsilon_grid = np.linspace(0.01, 0.15, 10)
        if n_grid is None:
            n_grid = [0.3, 0.5, 0.7, 1.0]

        results = []
        for n in n_grid:
            for eps in epsilon_grid:
                # Quick estimate: run small ensemble
                quick = KoushiappasNullEnsemble(n=n, epsilon=eps, 
                                                 N_ensemble=200,
                                                 M_min=self.M_min,
                                                 M_max=self.M_max,
                                                 z_ini=self.z_ini,
                                                 seed=self.rng.randint(0, 1e6))
                Ac_n = quick.generate_null_distribution()
                Ac_t = quick.generate_test_distribution()
                stats = quick.statistical_test(Ac_n, Ac_t)

                # Extrapolate to full N
                z_pred = stats['z_score'] * np.sqrt(self.N_ensemble / 200.0)

                results.append({
                    'n': n,
                    'epsilon': eps,
                    'z_score_200': stats['z_score'],
                    'z_score_predicted': z_pred,
                    'detectable_3sigma': abs(z_pred) > 3.0
                })

        return results


def print_null_model_protocol():
    """
    Print the formal null-model protocol as a checklist.
    """
    protocol = """
    ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    â     CLOUD-9 / KOUSHIAPPAS NULL-MODEL PROTOCOL v1.0                  â
    â âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ£
    â                                                                      â
    â  STEP 1: INITIAL CONDITIONS                                          â
    â  â Generate Gaussian random field with Planck 2018 power spectrum.    â
    â  â Same seed / same phases for ÎCDM and Koushiappas realizations.    â
    â  â Paper confirms scale-invariant spectrum is preserved (Sec. IV).    â
    â                                                                      â
    â  STEP 2: BACKGROUND EVOLUTION                                        â
    â  â ÎCDM: Standard E^2(z) = Î©_m(1+z)^3 + Î©_Î                        â
    â  â Koushiappas: E^2(z) = std - Îµ^2[2(1+z)^{-n} + (1+z)^{-2n}]      â
    â  â Use identical cosmological parameters except deformation.         â
    â                                                                      â
    â  STEP 3: HALO IDENTIFICATION                                         â
    â  â Match final mass M_200c within Â±5%.                               â
    â  â Match formation redshift z_form (when M > 0.5 M_final).         â
    â  â Same environment (isolation criterion).                           â
    â                                                                      â
    â  STEP 4: ASSEMBLY INDEX COMPUTATION                                  â
    â  â Same z_ini (e.g., z=6 or when halo first exceeds 10^11 M_sun).    â
    â  â Same ÎÏ = 50 Myr cadence.                                         â
    â  â Same k-NN estimator (KSG, k=2,6,10 cross-validation).            â
    â  â Same grid resolution (128^3 or higher).                          â
    â                                                                      â
    â  STEP 5: STATISTICAL COMPARISON                                      â
    â  â Two-sample t-test or KS test.                                     â
    â  â Report z-score, p-value, Cohen's d, and confidence interval.      â
    â  â Require z > 3.0 for "non-stochastic assembly" claim.             â
    â                                                                      â
    â  FORBIDDEN CLAIMS (Paper Caveats):                                   â
    â  â Do NOT claim Hubble tension is resolved (paper says it isn't).   â
    â  â Do NOT claim dark matter is explained (this is dark energy).     â
    â  â Do NOT use bounce regime (n<-2) with ÎCDM null ensemble.         â
    â  â Do NOT extrapolate to consciousness/Schumann without evidence.    â
    â                                                                      â
    ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    """
    print(protocol)


if __name__ == '__main__':
    print_null_model_protocol()

    # Example run with small ensemble
    print("\n=== Example Run (N=50, quick demo) ===")
    ensemble = KoushiappasNullEnsemble(n=0.5, epsilon=0.05, N_ensemble=50,
                                        M_min=1e11, M_max=1e13, z_ini=6.0)
    Ac_null = ensemble.generate_null_distribution()
    Ac_test = ensemble.generate_test_distribution()
    stats = ensemble.statistical_test(Ac_null, Ac_test)

    print(f"\nNull:  Î¼={stats['mu_null']:.2f}, Ï={stats['sigma_null']:.2f} bits")
    print(f"Test:  Î¼={stats['mu_test']:.2f}, Ï={stats['sigma_test']:.2f} bits")
    print(f"z-score: {stats['z_score']:.2f}")
    print(f"Cohen's d: {stats['cohens_d']:.3f}")
    print(f"3Ï detection? {stats['significant_3sigma']}")
