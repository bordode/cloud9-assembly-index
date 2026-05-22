"""
Cloud-9 Domain 4 Extension â Biological Longevity Escape Velocity
=================================================================
Maps the universal Îº-phase transition onto medical life-extension dynamics.
Uses the same sigmoidal yield template as the stellar/quantum/detector domains.

    Îº_longevity(t) = Î(t) / Î(t)
    Î(t) = rate of life-expectancy extension (yr gained / calendar yr)
    Î(t) = 1.0  (biological aging rate)

    Escape velocity: Îº > 1.0

Run: python domain_4_longevity.py
Output: domain_4_yield.png, domain_4_sweep.png, domain_4_stats.json
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# ============================================================
# 1. LONGEVITY PHYSICS MODEL
# ============================================================

def lambda_medical(t_years, lambda_0=0.02, r=0.15, t_inflect=2045):
    """
    Logistic model for life-extension technology pace.

    Parameters
    ----------
    t_years : float or ndarray
        Calendar year (e.g., 2026, 2035, ...)
    lambda_0 : float
        Baseline extension rate in 2020 (yr/yr). ~0.02 = 2 months/decade.
    r : float
        Growth rate of biomedical capability (analogous to Moore's Law slope).
    t_inflect : float
        Inflection year where acceleration peaks.

    Returns
    -------
    Lambda(t) : float or ndarray
        Life expectancy extension rate in years gained per calendar year.
    """
    return lambda_0 * np.exp(r * (t_years - 2020)) / (
        1.0 + (lambda_0 / 0.5) * (np.exp(r * (t_years - 2020)) - 1.0)
    )


def kappa_longevity(t_years, gamma=1.0, **lambda_kw):
    """
    Compute Îº = Î(t) / Î for biological longevity.

    Gamma is fixed at 1.0 yr/yr (we age one year per year).
    """
    return lambda_medical(t_years, **lambda_kw) / gamma


# ============================================================
# 2. YIELD MODEL (Universal Sigmoidal Template)
# ============================================================

def yield_complexity(kappa, kappa_c=1.0, steepness=8.0):
    """
    Sigmoidal yield curve â identical functional form across all Cloud-9 domains.

    Yield(kappa) = 1 / (1 + exp(-k * (kappa - kappa_c)))

    For longevity, yield represents the fraction of a cohort whose biological
    assembly paths remain open (i.e., do not terminate from aging) given
    medical intervention at rate kappa.
    """
    return 1.0 / (1.0 + np.exp(-steepness * (kappa - kappa_c)))


# ============================================================
# 3. SIMULATION SWEEP
# ============================================================

def run_longevity_sweep(years=None, n_samples=100000, seed=42):
    """
    Monte Carlo sweep over calendar years, computing Îº and yield distributions.

    Returns dict with statistics compatible with Cloud-9 experiment format.
    """
    rng = np.random.default_rng(seed)

    if years is None:
        years = np.arange(2020, 2061, 1)

    # Ensemble: each sample represents a different biomedical trajectory
    # (different r, lambda_0 drawn from plausible ranges)
    r_draws = rng.normal(0.15, 0.04, n_samples)
    lambda0_draws = rng.lognormal(np.log(0.025), 0.3, n_samples)
    t_inflect_draws = rng.normal(2045, 5, n_samples)

    results = {
        "years": [],
        "kappa_mean": [],
        "kappa_std": [],
        "yield_mean": [],
        "yield_std": [],
        "escape_fraction": [],  # fraction of ensemble with Îº > 1.0
    }

    for yr in years:
        # Vectorized Îº computation over entire ensemble
        lam = lambda0_draws * np.exp(r_draws * (yr - 2020)) / (
            1.0 + (lambda0_draws / 0.5) * (np.exp(r_draws * (yr - 2020)) - 1.0)
        )
        kappa = lam / 1.0
        y = yield_complexity(kappa)

        results["years"].append(int(yr))
        results["kappa_mean"].append(float(np.mean(kappa)))
        results["kappa_std"].append(float(np.std(kappa)))
        results["yield_mean"].append(float(np.mean(y)))
        results["yield_std"].append(float(np.std(y)))
        results["escape_fraction"].append(float(np.mean(kappa > 1.0)))

    return results


# ============================================================
# 4. PLOTTING
# ============================================================

def plot_longevity_phase_transition(results, fname="domain_4_sweep.png"):
    """
    Dual-panel plot: (a) Îº trajectory, (b) yield curve.
    Matches Cloud-9 dark-theme styling from cloud9_colab.py.
    """
    plt.rcParams.update({
        'figure.facecolor': '#1a1a2e',
        'axes.facecolor': '#16213e',
        'axes.edgecolor': '#e0e0e0',
        'axes.labelcolor': '#e0e0e0',
        'xtick.color': '#e0e0e0',
        'ytick.color': '#e0e0e0',
        'text.color': '#e0e0e0',
        'grid.color': '#2a2a4a',
    })

    years = np.array(results["years"])
    kappa = np.array(results["kappa_mean"])
    kappa_std = np.array(results["kappa_std"])
    yld = np.array(results["yield_mean"])
    yld_std = np.array(results["yield_std"])
    esc_frac = np.array(results["escape_fraction"])

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    fig.suptitle("Domain 4: Biological Longevity â Îº-Phase Transition", 
                 fontsize=14, color='#e0e0e0')

    # Panel 1: Îº(t)
    ax = axes[0]
    ax.fill_between(years, kappa - kappa_std, kappa + kappa_std, 
                    alpha=0.2, color='#00d4aa')
    ax.plot(years, kappa, '-', color='#00d4aa', lw=2, label='Îº(t) = Î/Î')
    ax.axhline(1.0, color='white', linestyle='--', alpha=0.7, label='Îº_c = 1.0')
    ax.axvline(2029, color='#ff6b6b', linestyle=':', alpha=0.6, label='Kurzweil 2029')
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Îº_longevity")
    ax.set_title("Medical Advance vs. Aging Rate")
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.25)
    ax.set_ylim(0, max(2.0, np.max(kappa + kappa_std) * 1.1))

    # Panel 2: Yield curve
    ax = axes[1]
    ax.fill_between(years, np.clip(yld - yld_std, 0, 1), 
                    np.clip(yld + yld_std, 0, 1), alpha=0.2, color='#ffd700')
    ax.plot(years, yld, '-', color='#ffd700', lw=2, label='Yield(Îº)')
    ax.axhline(0.5, color='white', linestyle='--', alpha=0.4)
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Complexity Yield")
    ax.set_title("Fraction of Open Assembly Paths")
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.25)
    ax.set_ylim(0, 1.05)

    # Panel 3: Escape-velocity probability
    ax = axes[2]
    ax.bar(years[::2], esc_frac[::2], width=1.5, color='#9b59b6', alpha=0.8, 
           edgecolor='#333355')
    ax.axhline(0.5, color='white', linestyle='--', alpha=0.5, label='50% threshold')
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("P(Îº > 1.0)")
    ax.set_title("Escape Velocity Probability")
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.25)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {fname}")


def plot_kappa_yield_relation(fname="domain_4_yield.png"):
    """
    Direct plot of Yield vs. Îº showing the universal sigmoidal template.
    """
    plt.rcParams.update({
        'figure.facecolor': '#1a1a2e',
        'axes.facecolor': '#16213e',
        'axes.edgecolor': '#e0e0e0',
        'axes.labelcolor': '#e0e0e0',
        'xtick.color': '#e0e0e0',
        'ytick.color': '#e0e0e0',
        'text.color': '#e0e0e0',
        'grid.color': '#2a2a4a',
    })

    kappa_range = np.linspace(0, 3, 300)
    y1 = yield_complexity(kappa_range, steepness=4.0)
    y2 = yield_complexity(kappa_range, steepness=8.0)
    y3 = yield_complexity(kappa_range, steepness=16.0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(kappa_range, y1, '--', color='#00d4aa', lw=1.5, alpha=0.6, label='k=4.0 (gradual)')
    ax.plot(kappa_range, y2, '-', color='#ffd700', lw=2.5, label='k=8.0 (moderate)')
    ax.plot(kappa_range, y3, ':', color='#ff6b6b', lw=1.5, alpha=0.6, label='k=16.0 (sharp)')
    ax.axvline(1.0, color='white', linestyle='--', alpha=0.7, label='Îº_c = 1.0')
    ax.axhline(0.5, color='white', linestyle=':', alpha=0.3)

    # Annotate domains
    ax.annotate('Sub-critical\n(aging wins)', xy=(0.5, 0.1), fontsize=9, 
                color='#e0e0e0', ha='center')
    ax.annotate('Super-critical\n(medicine wins)', xy=(2.0, 0.9), fontsize=9, 
                color='#e0e0e0', ha='center')

    ax.set_xlabel("Îº = Î(t) / Î")
    ax.set_ylabel("Yield = Open Assembly Paths")
    ax.set_title("Universal Phase Transition: Biological Longevity")
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.25)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {fname}")


# ============================================================
# 5. STATS EXPORT (Cloud-9 compatible format)
# ============================================================

def export_stats(results, fname="domain_4_stats.json"):
    """
    Write statistics in the same schema as exp_N_stats.json files.
    """
    years = np.array(results["years"])
    kappa = np.array(results["kappa_mean"])
    esc = np.array(results["escape_fraction"])

    # Find crossover year (where Îº_mean first exceeds 1.0)
    crossover_idx = np.where(kappa >= 1.0)[0]
    crossover_year = int(years[crossover_idx[0]]) if len(crossover_idx) > 0 else None

    # Find year where P(Îº>1) exceeds 50%
    prob50_idx = np.where(esc >= 0.5)[0]
    prob50_year = int(years[prob50_idx[0]]) if len(prob50_idx) > 0 else None

    stats = {
        "exp": 8,
        "label": "Biological Longevity (Domain 4)",
        "domain": "longevity",
        "n_samples": 100000,
        "kappa_critical": 1.0,
        "gamma": 1.0,
        "crossover_year_mean_kappa": crossover_year,
        "crossover_year_prob_50pct": prob50_year,
        "kappa_2026": round(float(kappa[years == 2026][0]), 4) if 2026 in years else None,
        "kappa_2040": round(float(kappa[years == 2040][0]), 4) if 2040 in years else None,
        "kappa_2050": round(float(kappa[years == 2050][0]), 4) if 2050 in years else None,
        "escape_fraction_2026": round(float(esc[years == 2026][0]), 4) if 2026 in years else None,
        "steepness_k": 8.0,
        "yield_function": "sigmoidal",
        "status": "SUGGESTIVE â parameter uncertainty in Î(t) model",
        "timestamp": "2026-04-29",
        "framework_version": "1.5.0+"
    }

    with open(fname, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved: {fname}")
    return stats


# ============================================================
# 6. MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CLOUD-9 DOMAIN 4: Biological Longevity Escape Velocity")
    print("=" * 60)
    print("Running Monte Carlo sweep over 2020â2060...")

    results = run_longevity_sweep(years=np.arange(2020, 2061, 1), n_samples=100000)

    # Print key years
    years = np.array(results["years"])
    kappa = np.array(results["kappa_mean"])
    esc = np.array(results["escape_fraction"])

    print("\nKey projections:")
    for yr in [2026, 2030, 2035, 2040, 2050]:
        idx = np.where(years == yr)[0]
        if len(idx) > 0:
            i = idx[0]
            print(f"  {yr}: Îº = {kappa[i]:.3f} | P(escape) = {esc[i]:.1%}")

    print("\nGenerating plots...")
    plot_kappa_yield_relation()
    plot_longevity_phase_transition(results)

    print("\nExporting stats...")
    stats = export_stats(results)

    print("\n" + "=" * 60)
    print("COMPLETE â Domain 4 integrated into Cloud-9 framework.")
    print("=" * 60)
