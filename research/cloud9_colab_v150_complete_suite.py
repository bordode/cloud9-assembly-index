# ============================================================
#  CLOUD-9 ASSEMBLY INDEX — Complete Simulation Suite v1.5.0
#  Designed for Google Colab
#  Run each section top to bottom, or Runtime > Run All
# ============================================================

# ────────────────────────────────────────────────────────────
# CELL 1 — Install dependencies
# ────────────────────────────────────────────────────────────
# !pip install numpy matplotlib requests -q

# ────────────────────────────────────────────────────────────
# CELL 2 — Imports & Colab setup
# ────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json, os, warnings

# Mount Google Drive (optional — comment out if not needed)
# from google.colab import drive
# drive.mount('/content/drive')

OUTPUT_DIR = "/content/"   # change to /content/drive/MyDrive/Cloud_9/ if using Drive

plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor':   '#16213e',
    'axes.edgecolor':   '#e0e0e0',
    'axes.labelcolor':  '#e0e0e0',
    'xtick.color':      '#e0e0e0',
    'ytick.color':      '#e0e0e0',
    'text.color':       '#e0e0e0',
    'grid.color':       '#2a2a4a',
    'legend.facecolor': '#1a1a2e',
    'legend.edgecolor': '#444466',
})

print("✓ Imports ready")


# ────────────────────────────────────────────────────────────
# CELL 3 — TNG API (uses Colab Secrets)
# ────────────────────────────────────────────────────────────
def fetch_tng_metallicity(api_key, n_halos=50):
    """
    Fetch real metallicity data from IllustrisTNG TNG100-1 (z=0).
    Returns array in solar units (Z/Z_sun). Returns None on failure.
    Set TNG_API_KEY in Colab Secrets (key icon in left panel).
    """
    try:
        import requests
    except ImportError:
        print("pip install requests")
        return None

    BASE    = "https://www.tng-project.org/api/"
    headers = {"api-key": api_key}

    r = requests.get(BASE, headers=headers, timeout=10)
    if r.status_code != 200:
        print(f"✗ TNG auth failed: HTTP {r.status_code}")
        return None

    url    = f"{BASE}TNG100-1/snapshots/99/subhalos/"
    params = {"limit": n_halos, "stellar_metallicity__gt": 0.001,
              "order_by": "-mass_stars"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        return None

    print(f"Fetching detailed data for {n_halos} subhalos...")
    metallicities = []
    for halo in r.json().get("results", []):
        d = requests.get(halo["url"], headers=headers, timeout=10)
        if d.status_code == 200:
            z = d.json().get("stellar_metallicity")
            if z is not None:
                metallicities.append(z)

    if not metallicities:
        return None

    z = np.array(metallicities) / 0.0127
    print(f"✓ TNG data: {len(z)} halos | Z={z.min():.3f}–{z.max():.3f} Z☉ | mean={z.mean():.3f} Z☉")
    return z


# Try to load from Colab Secrets
try:
    from google.colab import userdata
    TNG_KEY = userdata.get('TNG_API_KEY')
    print("✓ TNG_API_KEY found in Colab Secrets")
except Exception:
    TNG_KEY = os.environ.get("TNG_API_KEY", None)
    if TNG_KEY:
        print("✓ TNG_API_KEY found in environment")
    else:
        print("ℹ TNG_API_KEY not set — Exp 5 will use analytic fallback")
        print("  To connect: add TNG_API_KEY to Colab Secrets (🔑 icon, left panel)")

tng_z_array = None
if TNG_KEY:
    tng_z_array = fetch_tng_metallicity(TNG_KEY, n_halos=50)


# ────────────────────────────────────────────────────────────
# CELL 4 — Physics models
# ────────────────────────────────────────────────────────────

def uv_flare_denom_vec(star_types, ages, atm_depth_bar=1.0):
    """
    Vectorized per-star effective flare_denom using M-dwarf UV decay law.
    L_UV ~ t^(-0.5) after 1 Gyr saturation.
    K=8.0 fixed, F/G=12.0 fixed (not flare-dominated).
    """
    n      = len(star_types)
    result = np.full(n, 12.0)
    is_K   = star_types == 'K'
    is_M   = star_types == 'M'
    result[is_K] = 8.0
    t_c          = np.maximum(ages[is_M], 1.0)
    result[is_M] = np.clip(2.0 / (t_c ** -0.5) * atm_depth_bar, 0.5, 50.0)
    return result


def _draw_ages(star_types, rng):
    n    = len(star_types)
    ages = np.zeros(n)
    is_FG = star_types == 'F/G'
    is_K  = star_types == 'K'
    is_M  = star_types == 'M'
    ages[is_FG] = rng.uniform(1.0,  10.0, int(is_FG.sum()))
    ages[is_K]  = rng.uniform(2.0,  20.0, int(is_K.sum()))
    ages[is_M]  = rng.uniform(1.0, 100.0, int(is_M.sum()))
    return ages


def compute_habitability(star_types, p_planet, ages, cfg, rng):
    """
    Fully vectorized habitability scores.

    Key design decisions:
      - F/G base [0.50,1.00] > K [0.30,0.80]: F/G has most stable HZ
      - M base [0.05,0.95]: wide range, but flare-gated
      - flare_denom penalty ONLY applies to M dwarfs
      - Shifted tanh midpoint=2.0, slope=1.2: sharp crossover at fd≈2.5
    """
    n     = len(star_types)
    is_FG = star_types == 'F/G'
    is_K  = star_types == 'K'
    is_M  = star_types == 'M'

    base = np.zeros(n)
    base[is_FG] = rng.uniform(0.50, 1.00, int(is_FG.sum()))
    base[is_K]  = rng.uniform(0.30, 0.80, int(is_K.sum()))
    base[is_M]  = rng.uniform(0.05, 0.95, int(is_M.sum()))

    if cfg.get("use_uv_decay", False):
        fd_vec = uv_flare_denom_vec(star_types, ages,
                                    atm_depth_bar=cfg.get("atm_depth", 1.0))
    else:
        fd_vec = np.full(n, float(cfg.get("flare_denom", 1.0)))

    m_pen     = cfg.get("m_penalty", 1.0)
    flare_pen = np.ones(n)
    flare_pen[is_M] = (np.tanh((fd_vec[is_M] - 2.0) / 1.2) * 0.5 + 0.5) * m_pen

    hab = base * p_planet * flare_pen

    k_sig = cfg.get("sigmoid_k", None)
    if k_sig is not None:
        mid = cfg.get("sigmoid_mid", 0.4)
        hab = hab * (1.0 / (1.0 + np.exp(-k_sig * (hab - mid))))

    return hab


print("✓ Physics models ready")


# ────────────────────────────────────────────────────────────
# CELL 5 — Core simulation engine
# ────────────────────────────────────────────────────────────

def simulate(cfg):
    """
    Run one experiment. Per-experiment seed offset prevents collisions.
    Returns dict of raw arrays.
    """
    seed = cfg["seed"] + cfg.get("exp", 0) * 7919
    rng  = np.random.default_rng(seed)
    n    = cfg["N"]

    star_types = rng.choice(['F/G', 'K', 'M'], size=n, p=[0.15, 0.20, 0.65])
    ages       = _draw_ages(star_types, rng)

    tng_z    = cfg.get("tng_z_array", None)
    z_sample = (rng.choice(tng_z, size=n, replace=True)
                if tng_z is not None
                else np.clip(rng.lognormal(0.0, 0.3, n), 0.05, 5.0))

    p_planet = np.clip(cfg.get("pg_base", 0.5) * z_sample, 0.05, 1.0)
    hab      = compute_habitability(star_types, p_planet, ages, cfg, rng)
    observers = hab > cfg.get("hab_threshold", 0.5)

    phi_thresh = cfg.get("phi_threshold", None)
    if phi_thresh is not None:
        is_K  = star_types == 'K'
        is_FG = star_types == 'F/G'
        phi   = np.where(is_K,  rng.uniform(0.6, 1.0, n),
                np.where(is_FG, rng.uniform(0.3, 0.8, n),
                                rng.uniform(0.05, 0.5, n)))
        conscious = observers & (phi > phi_thresh)
    else:
        conscious = observers

    return {
        "star_types": star_types, "ages": ages,
        "z_sample": z_sample, "hab": hab,
        "observers": observers, "conscious": conscious,
        "cosmic_ages": ages[conscious],
        "p_planet": p_planet, "cfg": cfg,
    }


def analyze(R, cfg, show=True):
    """Print summary, plot, save PNG. Returns stats dict."""
    st, obs, con = R["star_types"], R["observers"], R["conscious"]
    ages  = R["cosmic_ages"]
    n     = cfg["N"]
    label = cfg["label"]
    exp   = cfg.get("exp", "?")

    print(f"\n{'='*50}")
    print(f"EXPERIMENT {exp}: {label}")
    print(f"{'='*50}")
    print(f"Samples: {n} | Observers: {obs.sum()} ({obs.mean()*100:.2f}%)")

    phi_on = cfg.get("phi_threshold") is not None
    if phi_on:
        print(f"Conscious: {con.sum()} ({con.mean()*100:.2f}%)")

    active      = con if phi_on else obs
    type_counts = {t: int((st[active] == t).sum()) for t in ['F/G', 'K', 'M']}
    total       = active.sum()

    print("Stellar type distribution:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = 100 * c / total if total > 0 else 0
        print(f"  {t:<4}: {c:5d} ({pct:.1f}%)")

    if len(ages) > 0:
        print(f"Cosmic age: mean={ages.mean():.1f}, "
              f"median={np.median(ages):.1f}, std={ages.std():.1f}")

    mean_z = float(R["z_sample"][active].mean()) if total > 0 else float('nan')

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(f"Exp {exp}: {label}", fontsize=13, color='#e0e0e0')

    axes[0].hist(R["hab"], bins=50, color='steelblue', alpha=0.8)
    axes[0].axvline(cfg.get("hab_threshold", 0.5), color='red',
                    linestyle='--', label='threshold')
    axes[0].set_xlabel("Habitability Score")
    axes[0].set_title("Habitability Distribution")
    axes[0].legend()

    labels_pie = [t for t in ['F/G', 'K', 'M'] if type_counts.get(t, 0) > 0]
    sizes_pie  = [type_counts[t] for t in labels_pie]
    cp = {'F/G': '#FFD700', 'K': '#FFA500', 'M': '#CC3333'}
    if sizes_pie:
        axes[1].pie(sizes_pie, labels=labels_pie,
                    colors=[cp[t] for t in labels_pie],
                    autopct='%1.1f%%', startangle=140)
    axes[1].set_title("Observer Stellar Types")

    if len(ages) > 0:
        axes[2].hist(ages, bins=30, color='#9b59b6', alpha=0.8)
        axes[2].axvline(ages.mean(), color='white', linestyle='--',
                        label=f'mean={ages.mean():.1f} Gyr')
        axes[2].set_xlabel("Stellar Age (Gyr)")
        axes[2].set_title("Cosmic Age Distribution")
        axes[2].legend()

    plt.tight_layout()
    fname = os.path.join(OUTPUT_DIR, f"exp_{exp}.png")
    plt.savefig(fname, dpi=120, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()
    print(f"Saved: {fname}")

    stats = {
        "exp": exp, "label": label,
        "n_samples": n, "n_observers": int(obs.sum()),
        "yield_pct": round(obs.mean() * 100, 2),
        "n_conscious": int(con.sum()),
        "conscious_pct": round(con.mean() * 100, 2),
        "FG_pct":  round(100*type_counts['F/G']/total, 1) if total else 0,
        "K_pct":   round(100*type_counts['K']  /total, 1) if total else 0,
        "M_pct":   round(100*type_counts['M']  /total, 1) if total else 0,
        "mean_age_gyr": round(float(ages.mean()), 2) if len(ages) else None,
        "mean_z_solar": round(mean_z, 3),
    }
    with open(os.path.join(OUTPUT_DIR, f"exp_{exp}_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    return stats


print("✓ Simulation engine ready")


# ────────────────────────────────────────────────────────────
# CELL 6 — Experiment presets
# ────────────────────────────────────────────────────────────

PRESETS = [
    {"exp": 0, "label": "Baseline Strict (Loeb)",
     "flare_denom": 1.0, "m_penalty": 0.3,
     "pg_base": 0.5, "hab_threshold": 0.5},

    {"exp": 1, "label": "Relaxed (IMF Dominance)",
     "flare_denom": 5.0,
     "pg_base": 0.5, "hab_threshold": 0.5},

    {"exp": 2, "label": "M-dwarf Stress (Null Hypothesis)",
     "flare_denom": 20.0,
     "pg_base": 0.5, "hab_threshold": 0.3},

    {"exp": 3, "label": "Sigmoidal Criticality",
     "flare_denom": 5.0, "sigmoid_k": 10.0, "sigmoid_mid": 0.45,
     "pg_base": 0.5, "hab_threshold": 0.5},

    {"exp": 4, "label": "Consciousness / Phi (IIT Proxy)",
     "flare_denom": 5.0, "phi_threshold": 0.55,
     "pg_base": 0.5, "hab_threshold": 0.5},

    {"exp": 5, "label": "TNG100-1 Metallicity (Real Data)",
     "flare_denom": 5.0,
     "pg_base": 0.5, "hab_threshold": 0.5},

    {"exp": 7, "label": "UV Decay Physics",
     "use_uv_decay": True, "atm_depth": 1.0,
     "pg_base": 0.5, "hab_threshold": 0.5},
]

BASE_CFG = {"N": 20000, "seed": 42}
print("✓ Presets ready")


# ────────────────────────────────────────────────────────────
# CELL 7 — Run all experiments
# ────────────────────────────────────────────────────────────

all_stats = []

for preset in PRESETS:
    cfg = {**BASE_CFG, **preset}
    if cfg["exp"] == 5 and tng_z_array is not None:
        cfg["tng_z_array"] = tng_z_array
    R     = simulate(cfg)
    stats = analyze(R, cfg)
    all_stats.append(stats)

with open(os.path.join(OUTPUT_DIR, "all_experiments_summary.json"), "w") as f:
    json.dump(all_stats, f, indent=2)
print("\n✓ All experiments complete — summary saved")


# ────────────────────────────────────────────────────────────
# CELL 8 — Flare_denom sweep (Exp 6 / Phase transition)
# ────────────────────────────────────────────────────────────

def run_sweep(n=20000, seed=42, show=True):
    print("\n>>> EXPERIMENT 6: Flare-denom phase transition sweep <<<")
    denoms = np.logspace(0, 2, 25)   # 1.0 → 100.0
    fg_list, k_list, m_list = [], [], []

    for fd in denoms:
        cfg = {**BASE_CFG, "exp": 6, "label": "sweep",
               "flare_denom": float(fd), "pg_base": 0.5, "hab_threshold": 0.5}
        R     = simulate(cfg)
        obs   = R["observers"]
        st    = R["star_types"]
        total = obs.sum()
        if total == 0:
            fg_list.append(0); k_list.append(0); m_list.append(0)
            continue
        fg_list.append(100 * (st[obs] == 'F/G').mean())
        k_list.append( 100 * (st[obs] == 'K').mean())
        m_list.append( 100 * (st[obs] == 'M').mean())
        print(f"  fd={fd:6.1f} → F/G={fg_list[-1]:.1f}%  "
              f"K={k_list[-1]:.1f}%  M={m_list[-1]:.1f}%")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.semilogx(denoms, fg_list, 'o-', color='#FFD700', lw=2, label='F/G (Sun-like)')
    ax.semilogx(denoms, k_list,  's-', color='#FFA500', lw=2, label='K (Orange dwarf)')
    ax.semilogx(denoms, m_list,  '^-', color='#CC3333', lw=2, label='M (Red dwarf)')
    ax.axvline(2.5, color='white', linestyle='--', alpha=0.7,
               label='Critical transition ≈ 2.5')
    ax.fill_betweenx([0,100], 1.0, 2.5, alpha=0.07, color='#FFD700',
                     label='F/G Empire')
    ax.fill_betweenx([0,100], 2.5, 100, alpha=0.05, color='#CC3333',
                     label='M-dwarf Flood zone')
    ax.set_xlabel("flare_denom  (atmospheric recovery / flare damage rate)")
    ax.set_ylabel("% of Observers")
    ax.set_title("Phase Transition of Habitability — Cloud-9 v1.5.0\n"
                 "The history of life in the universe hinges on this single parameter",
                 fontsize=11)
    ax.legend(loc='center right'); ax.grid(True, alpha=0.25)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    fname = os.path.join(OUTPUT_DIR, "exp_6_sweep.png")
    plt.savefig(fname, dpi=120, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()
    print(f"Saved: {fname}")

run_sweep()


# ────────────────────────────────────────────────────────────
# CELL 9 — Nearest star systems habitability analysis
# ────────────────────────────────────────────────────────────

NEAREST_STARS = [
    # (name, dist_ly, type, age_gyr, has_known_planet, notes)
    ("Proxima Centauri",  4.24,  'M',   4.85, True,
     "Proxima b in HZ; intense flares; tidal locking risk"),
    ("Alpha Centauri A",  4.37,  'F/G', 6.5,  False,
     "G2V Sun analog; stable; binary may disrupt inner planets"),
    ("Alpha Centauri B",  4.37,  'K',   6.5,  False,
     "K1V; excellent stability; sweet-spot age; binary companion"),
    ("Barnard's Star",    5.96,  'M',   10.0, False,
     "Old M dwarf; flares much reduced by age; no confirmed planets"),
    ("Wolf 359",          7.79,  'M',   1.0,  False,
     "Young, highly active; among most hostile nearby M dwarfs"),
    ("Lalande 21185",     8.29,  'M',   7.5,  False,
     "Quiet older M dwarf; one of calmer M candidates"),
    ("Sirius A",          8.60,  'F/G', 0.24, False,
     "A-type; too hot, too short-lived — excluded from HZ"),
    ("Epsilon Eridani",  10.50,  'K',   0.8,  True,
     "K2V; young and active but excellent long-term potential"),
    ("Lacaille 9352",    10.68,  'M',   6.0,  False,
     "Moderately quiet M dwarf; sub-solar metallicity likely"),
    ("Ross 128",         11.03,  'M',   9.0,  True,
     "Old quiet M dwarf; Ross 128b in HZ — best M candidate nearby"),
    ("Tau Ceti",         11.91,  'F/G', 5.8,  True,
     "G8V; multiple planet candidates; moderate metallicity"),
    ("Epsilon Indi A",   11.83,  'K',   3.7,  False,
     "K5V; quiet and stable; excellent HZ candidate"),
]


def score_star(star):
    name, dist, stype, age, has_planet, _ = star

    # Stellar type base
    type_base = {'F/G': 0.78, 'K': 0.82, 'M': 0.55}[stype]

    # Age factor — sweet spot 3–8 Gyr
    if   age < 1.0:  age_f = 0.25
    elif age < 3.0:  age_f = 0.25 + 0.40 * (age - 1.0) / 2.0
    elif age <= 8.0: age_f = 0.65 + 0.25 * (age - 3.0) / 5.0
    else:            age_f = max(0.50, 0.90 - 0.02 * (age - 8.0))

    # M-dwarf UV decay flare penalty
    if stype == 'M':
        t_c   = max(age, 1.0)
        fd    = np.clip(2.0 * (t_c ** 0.5), 0.5, 50.0)
        f_pen = float(np.tanh((fd - 2.0) / 1.2) * 0.5 + 0.5)
    else:
        f_pen = 1.0

    # Sirius override
    if "Sirius" in name:
        return 0.04, {"override": "A-type excluded"}

    planet_bonus = 0.10 if has_planet else 0.0
    score = float(np.clip(type_base * age_f * f_pen + planet_bonus, 0.0, 1.0))
    return score, {"type_base": round(type_base,3), "age_f": round(age_f,3),
                   "flare_pen": round(f_pen,3), "planet_bonus": planet_bonus}


def run_nearest_stars(show=True):
    print("\n" + "="*65)
    print("NEAREST STAR SYSTEMS — HABITABILITY ANALYSIS  (Cloud-9 v1.5.0)")
    print("="*65)
    print(f"{'Star':<22} {'ly':>5} {'Type':>5} {'Age':>6} {'Score':>7}  Notes")
    print("-"*90)

    results = []
    for star in NEAREST_STARS:
        name, dist, stype, age, planet, notes = star
        score, breakdown = score_star(star)
        flag = "★" if planet else " "
        print(f"{name:<22} {dist:>5.2f} {stype:>5}  {age:>5.1f}G "
              f"{score:>7.3f} {flag}  {notes[:52]}")
        results.append({"name": name, "dist_ly": dist, "type": stype,
                         "age_gyr": age, "has_planet": planet,
                         "hab_score": round(score, 3), "breakdown": breakdown})

    ranked = sorted(results, key=lambda x: -x["hab_score"])
    print("\n★ = confirmed planet in or near habitable zone")
    print("\n─── FINAL RANKING ───────────────────────────────────────────")
    for i, r in enumerate(ranked, 1):
        bar = "█" * int(r["hab_score"] * 20)
        print(f"  {i:>2}. {r['name']:<22} {bar:<20} {r['hab_score']:.3f}  "
              f"({r['type']}, {r['age_gyr']} Gyr)")

    # Plot
    cp = {'F/G': '#FFD700', 'K': '#FFA500', 'M': '#CC3333'}
    names  = [r["name"] for r in ranked]
    scores = [r["hab_score"] for r in ranked]
    colors = [cp[r["type"]] for r in ranked]

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.barh(names[::-1], scores[::-1], color=colors[::-1],
                   alpha=0.85, edgecolor='#333355', height=0.65)

    # Planet markers
    for bar, r in zip(bars, ranked[::-1]):
        if r["has_planet"]:
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    "★", va='center', fontsize=13, color='cyan')
        ax.text(0.01, bar.get_y() + bar.get_height()/2,
                f"{r['type']}  {r['age_gyr']} Gyr",
                va='center', fontsize=7.5, color='white', alpha=0.8)

    ax.axvline(0.5, color='white', linestyle='--', alpha=0.5, label='hab threshold 0.5')
    ax.set_xlabel("Habitability Score  [0 = sterile → 1 = optimal]")
    ax.set_title("Nearest Star Systems — Cloud-9 Habitability Model v1.5.0\n"
                 "★ = confirmed planet in/near HZ   |   UV decay + age + metallicity weighting",
                 fontsize=11)

    legend_patches = [
        mpatches.Patch(color='#FFD700', label='F/G  Sun-like'),
        mpatches.Patch(color='#FFA500', label='K    Orange dwarf'),
        mpatches.Patch(color='#CC3333', label='M    Red dwarf'),
    ]
    ax.legend(handles=legend_patches, loc='lower right')
    ax.set_xlim(0, 1.05)
    ax.grid(axis='x', alpha=0.25)
    plt.tight_layout()
    fname = os.path.join(OUTPUT_DIR, "nearest_stars_hab.png")
    plt.savefig(fname, dpi=120, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()
    print(f"\nSaved: {fname}")

    with open(os.path.join(OUTPUT_DIR, "nearest_stars_results.json"), "w") as f:
        json.dump(ranked, f, indent=2)
    print("Saved: nearest_stars_results.json")
    return ranked

nearest_ranked = run_nearest_stars()


# ────────────────────────────────────────────────────────────
# CELL 10 — Consolidated results table
# ────────────────────────────────────────────────────────────

print("\n" + "="*80)
print("CONSOLIDATED RESULTS — Cloud-9 Anthropic Selection Suite v1.5.0")
print("="*80)
print(f"{'Exp':<4} {'Label':<35} {'Yield%':>7} {'F/G%':>6} {'K%':>6} "
      f"{'M%':>6} {'MeanAge':>8}")
print("-"*80)
for s in all_stats:
    age = f"{s['mean_age_gyr']:.1f}" if s['mean_age_gyr'] else "  —  "
    print(f"{s['exp']:<4} {s['label']:<35} {s['yield_pct']:>7.2f} "
          f"{s['FG_pct']:>6.1f} {s['K_pct']:>6.1f} {s['M_pct']:>6.1f} {age:>8}")

print("\nTop 3 nearest habitable star systems:")
for i, r in enumerate(nearest_ranked[:3], 1):
    print(f"  {i}. {r['name']} — score {r['hab_score']:.3f} "
          f"({'planet confirmed ★' if r['has_planet'] else 'no confirmed planet'})")

print("\n>>> ALL COMPLETE <<<")
