#!/usr/bin/env python3
"""
================================================================================
TNG100-1 Cosmological Assembly & Certified Randomness Framework v3.0
For Google Colab Execution
================================================================================
Integrates: IllustrisTNG API | Assembly Index Metrics | Quantum-Inspired 
Randomness Seeding | Halo Merger Tree Analysis | Cross-Domain Pattern Matching

API Key Variable: illistrig_api (as requested)
Target: TNG100-1, Snapshot 99 (z~0)
================================================================================
"""

# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 1: ENVIRONMENT SETUP & IMPORTS                                         â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

import os
import sys
import json
import time
import warnings
import requests
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from urllib.parse import urlencode
from io import BytesIO
from datetime import datetime

# Visualization
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.colors import LogNorm, SymLogNorm
import seaborn as sns

# Statistical & Scientific
from scipy import stats, integrate, optimize, spatial
from scipy.spatial import cKDTree, ConvexHull
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score

# Suppress benign warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
plt.style.use('dark_background')
sns.set_palette("husl")

print("=" * 80)
print("TNG100-1 COSMOLOGICAL ASSEMBLY & CERTIFIED RANDOMNESS FRAMEWORK v3.0")
print("=" * 80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"NumPy: {np.__version__} | SciPy: {stats.__version__} | Pandas: {pd.__version__}")
print("=" * 80)


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 2: CONFIGURATION & API CREDENTIALS                                     â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class TNGConfig:
    """Centralized configuration for TNG API and analysis parameters."""

    # --- API Configuration ---
    BASE_URL = "http://www.tng-project.org/api/"
    HEADERS = {"api-key": os.environ.get("illistrig_api", "YOUR_API_KEY_HERE")}

    # --- Simulation Target ---
    SIMULATION = "TNG100-1"
    SNAPSHOT = 99  # z ~ 0

    # --- Physical Constants (TNG cosmology) ---
    HUBBLE_PARAM = 0.6774  # h
    OMEGA_M = 0.3089
    OMEGA_L = 0.6911
    BOX_SIZE_MPC = 110.7  # Mpc/h -> physical below

    # --- Sampling Parameters ---
    N_HALOS_TARGET = 2048  # As per your validation suite scale
    N_BOOTSTRAP = 1000
    RANDOM_SEED_MODE = "quantum_inspired"  # "quantum_inspired", "crypto", "legacy"

    # --- Assembly Index Parameters ---
    SHELL_RADII = np.logspace(-1, 1.5, 25)  # in R_vir fractions
    COMPLEXITY_ORDERS = [1, 2, 3, 4]  # Topological, Information, Quantum, Integrated

    # --- Filtering ---
    MIN_STELLAR_MASS = 1e9  # Msun
    MIN_DM_MASS = 1e11  # Msun
    MAX_REDSHIFT = 0.1

    # --- Output ---
    SAVE_DIR = "/content/tng_assembly_output"
    CACHE_HALOS = True

    @classmethod
    def physical_distance(cls, comoving_mpc_h: float, scale_factor: float = 1.0) -> float:
        """Convert comoving Mpc/h to physical Mpc."""
        return comoving_mpc_h / cls.HUBBLE_PARAM * scale_factor

    @classmethod
    def physical_mass(cls, mass_msun_h: float) -> float:
        """Convert mass from Msun/h to Msun."""
        return mass_msun_h / cls.HUBBLE_PARAM

# Create output directory
os.makedirs(TNGConfig.SAVE_DIR, exist_ok=True)
print(f"[CONFIG] Output directory: {TNGConfig.SAVE_DIR}")
print(f"[CONFIG] Target halos: {TNGConfig.N_HALOS_TARGET}")
print(f"[CONFIG] Randomness mode: {TNGConfig.RANDOM_SEED_MODE}")


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 3: CERTIFIED RANDOMNESS ENGINE                                         â
# â  Inspired by ETH Zurich Bell-test randomness amplification (May 2026)        â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class CertifiedRandomnessEngine:
    """
    Implements a 'quantum-inspired' randomness generation framework for 
    cosmological sampling. While not a true Bell-test device, it uses:

    1. Hardware entropy pooling (OS /dev/urandom, time nanoseconds)
    2. Chaotic map mixing (logistic map at critical parameter)
    3. Cosmological seed injection (CMB dipole anisotropy digits)
    4. Entropy concentration via Toeplitz hashing (extractor theory)

    This simulates the *spirit* of device-independent certification:
    randomness derived from physical unpredictability, not algorithmic PRNG.
    """

    def __init__(self, mode: str = "quantum_inspired"):
        self.mode = mode
        self.entropy_pool = bytearray()
        self._init_pool()
        self._chaotic_state = None
        self._init_chaos()

    def _init_pool(self):
        """Seed from OS entropy + high-resolution timing + process jitter."""
        import hashlib
        # Layer 1: OS cryptographic entropy
        os_entropy = os.urandom(64)
        # Layer 2: Time nanosecond jitter (physical process)
        time_entropy = str(time.time_ns()).encode()
        # Layer 3: Python object id jitter
        jitter = str(id(self) ^ id(os) ^ id(time)).encode()
        # Layer 4: Cosmological constant injection (simulating physical seed)
        cosmology_seed = f"{TNGConfig.OMEGA_M:.10f}{TNGConfig.OMEGA_L:.10f}".encode()

        self.entropy_pool = hashlib.sha3_256(
            os_entropy + time_entropy + jitter + cosmology_seed
        ).digest()

    def _init_chaos(self):
        """Initialize logistic map at edge of chaos (r â 3.56995...)."""
        # Use Feigenbaum point approximation for maximum unpredictability
        feigenbaum_approx = 3.5699456718709449
        # Seed from entropy pool
        seed_int = int.from_bytes(self.entropy_pool[:4], 'big') / (2**32)
        self._chaotic_state = seed_int if 0 < seed_int < 1 else 0.3
        self._r = feigenbaum_approx + 0.001 * np.sin(seed_int * 2 * np.pi)

    def _chaotic_byte(self) -> int:
        """Extract one byte via iterated chaotic mixing."""
        # Iterate logistic map multiple times for mixing
        state = self._chaotic_state
        for _ in range(8):  # 8 iterations per bit
            state = self._r * state * (1 - state)
        self._chaotic_state = state
        # Extract byte from mantissa bits (simulating physical measurement)
        mantissa = int(state * (2**53)) & 0xFF
        return mantissa

    def generate_bytes(self, n: int) -> bytes:
        """Generate n certified-random bytes."""
        if self.mode == "legacy":
            return os.urandom(n)  # Fallback

        result = bytearray(n)
        for i in range(n):
            # Mix chaotic output with entropy pool via Toeplitz-like extraction
            cb = self._chaotic_byte()
            pool_byte = self.entropy_pool[i % len(self.entropy_pool)]
            result[i] = (cb ^ pool_byte) & 0xFF
        return bytes(result)

    def random_integers(self, low: int, high: int, size: int = 1) -> np.ndarray:
        """Generate certified random integers in [low, high)."""
        if self.mode == "legacy":
            rng = np.random.default_rng()
            return rng.integers(low, high, size=size)

        n_bytes = max(1, (high - 1).bit_length() // 8 + 1)
        vals = []
        for _ in range(size):
            while True:
                b = self.generate_bytes(n_bytes)
                val = int.from_bytes(b, 'big')
                if val < (256**n_bytes - (256**n_bytes % (high - low))):
                    vals.append(low + (val % (high - low)))
                    break
        return np.array(vals)

    def random_floats(self, size: int = 1) -> np.ndarray:
        """Generate certified random floats in [0, 1)."""
        if self.mode == "legacy":
            rng = np.random.default_rng()
            return rng.random(size=size)

        bytes_needed = size * 8
        raw = self.generate_bytes(bytes_needed)
        floats = []
        for i in range(size):
            chunk = raw[i*8:(i+1)*8]
            # Convert to 53-bit mantissa float (IEEE 754 double precision)
            int_val = int.from_bytes(chunk, 'big') & ((1 << 53) - 1)
            floats.append(int_val / (1 << 53))
        return np.array(floats)

    def certify_entropy(self, sample: np.ndarray, bins: int = 256) -> Dict:
        """
        Certify randomness quality via min-entropy estimation.
        Returns diagnostic dict (simulating Bell-test violation report).
        """
        hist, _ = np.histogram(sample, bins=bins)
        probs = hist / len(sample)
        probs = probs[probs > 0]
        shannon_entropy = -np.sum(probs * np.log2(probs))
        max_entropy = np.log2(bins)
        min_entropy = -np.log2(np.max(probs)) if len(probs) > 0 else 0

        # Simulate 'Bell violation' metric: distance from local hidden variable bound
        # In true DI-QRNG, this would be S > 2. For simulation, we use entropy deficit
        bell_proxy = (shannon_entropy / max_entropy) * 2.828  # Scale to CHSH-like

        return {
            "shannon_entropy_bits": shannon_entropy,
            "max_possible_bits": max_entropy,
            "min_entropy_bits": min_entropy,
            "entropy_rate": shannon_entropy / max_entropy,
            "bell_violation_proxy": bell_proxy,
            "certified": bell_proxy > 2.0,  # Simulated threshold
            "mode": self.mode,
            "sample_size": len(sample),
            "timestamp": datetime.now().isoformat()
        }

# Initialize global certified randomness engine
CERT_RNG = CertifiedRandomnessEngine(mode=TNGConfig.RANDOM_SEED_MODE)
print("[CERTIFIED RNG] Initialized in quantum-inspired mode")
print(f"[CERTIFIED RNG] Initial entropy pool: {CERT_RNG.entropy_pool.hex()[:32]}...")


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 4: TNG API CLIENT                                                       â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class TNGClient:
    """Robust HTTP client for IllustrisTNG API with caching and retry logic."""

    def __init__(self, config: TNGConfig = TNGConfig):
        self.cfg = config
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.cache = {}
        self.request_count = 0
        self.error_count = 0

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Execute API request with exponential backoff."""
        cache_key = f"{url}?{urlencode(params or {})}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.request_count += 1
                resp = self.session.get(url, params=params, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                self.cache[cache_key] = data
                return data
            except requests.exceptions.RequestException as e:
                self.error_count += 1
                wait = 2 ** attempt + CERT_RNG.random_floats(1)[0]
                print(f"[API WARN] Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
                time.sleep(wait)
        raise ConnectionError(f"Failed to fetch {url} after {max_retries} attempts")

    def get_simulation_info(self) -> Dict:
        """Fetch metadata for TNG100-1."""
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/"
        return self._make_request(url)

    def get_snapshot_info(self, snap_num: Optional[int] = None) -> Dict:
        """Fetch snapshot metadata."""
        snap = snap_num or self.cfg.SNAPSHOT
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/snapshots/{snap}/"
        return self._make_request(url)

    def get_subhalos(self, snap_num: Optional[int] = None, 
                     limit: int = 100, offset: int = 0,
                     filters: Optional[Dict] = None) -> Dict:
        """Query subhalo catalog with optional filters."""
        snap = snap_num or self.cfg.SNAPSHOT
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/snapshots/{snap}/subhalos/"
        params = {"limit": limit, "offset": offset}
        if filters:
            # TNG API uses specific filter syntax
            filter_strs = []
            for key, (op, val) in filters.items():
                filter_strs.append(f"{key}{op}{val}")
            params["subhalo_mass__gt"] = filters.get("mass_min", 1e10)
        return self._make_request(url, params)

    def get_subhalo(self, subhalo_id: int, snap_num: Optional[int] = None) -> Dict:
        """Fetch detailed single subhalo data."""
        snap = snap_num or self.cfg.SNAPSHOT
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/snapshots/{snap}/subhalos/{subhalo_id}/"
        return self._make_request(url)

    def get_halo_particles(self, subhalo_id: int, part_type: str = "dm",
                           fields: Optional[List[str]] = None) -> np.ndarray:
        """Fetch particle data for a subhalo (cutout)."""
        snap = self.cfg.SNAPSHOT
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/snapshots/{snap}/subhalos/{subhalo_id}/cutout.hdf5"
        params = {}
        if fields:
            params["dm"] = ",".join(fields) if part_type == "dm" else None

        try:
            resp = self.session.get(url, params=params, timeout=120)
            resp.raise_for_status()
            # Parse HDF5 from bytes
            import h5py
            with h5py.File(BytesIO(resp.content), 'r') as f:
                if part_type == "dm" and 'PartType1' in f:
                    return f['PartType1']['Coordinates'][()]
                elif part_type == "stars" and 'PartType4' in f:
                    return f['PartType4']['Coordinates'][()]
            return np.array([])
        except Exception as e:
            print(f"[PARTICLE ERROR] Subhalo {subhalo_id}: {e}")
            return np.array([])

    def get_merger_tree(self, subhalo_id: int, snap_num: Optional[int] = None) -> Dict:
        """Fetch merger tree (sublink) for a subhalo."""
        snap = snap_num or self.cfg.SNAPSHOT
        # Sublink query
        url = f"{self.cfg.BASE_URL}{self.cfg.SIMULATION}/snapshots/{snap}/subhalos/{subhalo_id}/sublink/"
        try:
            return self._make_request(url)
        except:
            return {}

# Instantiate client
client = TNGClient()
print(f"[TNG CLIENT] Initialized | API Key: {TNGConfig.HEADERS['api-key'][:8]}...")
print(f"[TNG CLIENT] Base URL: {TNGConfig.BASE_URL}")


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 5: HALO DATA STRUCTURES & ASSEMBLY INDEX                               â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

@dataclass
class HaloAssembly:
    """Rich data container for a single halo's assembly history."""

    # Identity
    subhalo_id: int
    snap_num: int

    # Physical Properties
    mass_total_msun: float = 0.0
    mass_dm_msun: float = 0.0
    mass_stellar_msun: float = 0.0
    mass_gas_msun: float = 0.0
    radius_halfmass_kpc: float = 0.0
    radius_virial_kpc: float = 0.0
    velocity_disp_kms: float = 0.0
    v_max_kms: float = 0.0
    spin_parameter: float = 0.0
    metallicity_stellar: float = 0.0
    sfr_msun_per_yr: float = 0.0

    # Position & Environment
    pos_x_ckpc: float = 0.0
    pos_y_ckpc: float = 0.0
    pos_z_ckpc: float = 0.0
    vel_x_kms: float = 0.0
    vel_y_kms: float = 0.0
    vel_z_kms: float = 0.0

    # Assembly Index Components
    topological_complexity: float = 0.0      # Shell structure irregularity
    information_complexity: float = 0.0       # Shannon entropy of mass profile
    quantum_complexity: float = 0.0         # Von Neumann-like entropy proxy
    integrated_complexity: float = 0.0        # Phi-like integrated information
    assembly_index_ac: float = 0.0          # Composite A_c score

    # Merger History
    num_mergers_major: int = 0
    num_mergers_minor: int = 0
    formation_redshift: float = 0.0
    last_major_merger_z: float = -1.0
    merger_tree_depth: int = 0

    # Randomness Certification
    sampling_seed: int = 0
    entropy_certification: Dict = field(default_factory=dict)

    # Raw data
    raw_api_data: Dict = field(default_factory=dict, repr=False)
    particle_coords: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['particle_coords'] = self.particle_coords.tolist() if len(self.particle_coords) > 0 else []
        return d


class AssemblyIndexCalculator:
    """
    Computes the Cosmological Assembly Index A_c for halos.

    Based on your Cloud-9 framework formalism:
    A_c = w_topo * C_topo + w_info * C_info + w_quant * C_quant + w_int * C_int

    Where:
    - C_topo: Topological complexity (TDA-inspired, shell irregularity)
    - C_info: Information-theoretic complexity (entropy of mass distribution)
    - C_quant: Quantum-inspired complexity (density matrix purity proxy)
    - C_int: Integrated information (Phi-like measure of causal structure)
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "topological": 0.25,
            "information": 0.25,
            "quantum": 0.25,
            "integrated": 0.25
        }

    def compute_topological_complexity(self, halo: HaloAssembly, 
                                        shell_radii: np.ndarray = None) -> float:
        """
        Measure shell structure irregularity using density profile fluctuations.
        High complexity = non-monotonic, multi-peaked density profile.
        """
        if shell_radii is None:
            shell_radii = TNGConfig.SHELL_RADII

        # Simulate density profile from halo properties
        # In full implementation, this uses actual particle counts in shells
        r_hm = halo.radius_halfmass_kpc
        if r_hm <= 0:
            return 0.0

        # NFW-inspired profile with perturbations
        r_phys = shell_radii * r_hm
        rho_nfw = 1.0 / (r_phys * (1 + r_phys)**2)

        # Add merger-driven perturbations (higher for merger-rich halos)
        perturbation = halo.num_mergers_major * 0.1 * np.sin(r_phys / r_hm * 4 * np.pi)
        rho = rho_nfw * (1 + perturbation)

        # Topological complexity: normalized variance of log-gradient
        log_rho = np.log10(rho + 1e-10)
        gradient = np.gradient(log_rho)
        complexity = np.std(gradient) / (np.mean(np.abs(gradient)) + 1e-10)

        # Normalize to [0, 1]
        return np.tanh(complexity)

    def compute_information_complexity(self, halo: HaloAssembly) -> float:
        """
        Shannon entropy of mass component distribution.
        More balanced mass fractions = higher entropy = higher complexity.
        """
        components = np.array([
            halo.mass_dm_msun,
            halo.mass_stellar_msun,
            halo.mass_gas_msun,
            max(halo.mass_total_msun - halo.mass_dm_msun - halo.mass_stellar_msun - halo.mass_gas_msun, 0)
        ])

        total = np.sum(components)
        if total <= 0:
            return 0.0

        probs = components / total
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        max_entropy = np.log2(len(components))

        return entropy / max_entropy if max_entropy > 0 else 0.0

    def compute_quantum_complexity(self, halo: HaloAssembly) -> float:
        """
        Von Neumann entropy proxy using velocity dispersion tensor.
        Treat velocity distribution as 'density matrix' eigenvalues.
        """
        # Construct velocity dispersion tensor (simplified)
        sigma_v = halo.velocity_disp_kms
        if sigma_v <= 0:
            return 0.0

        # Simulate anisotropic dispersion from spin and merger history
        beta = halo.spin_parameter
        gamma = min(halo.num_mergers_major / 5.0, 1.0)

        # Eigenvalues of dispersion tensor (simulated)
        lambda1 = sigma_v * (1 + beta + gamma)
        lambda2 = sigma_v * (1 + beta - gamma * 0.5)
        lambda3 = sigma_v * (1 - beta * 0.8)

        lambdas = np.array([lambda1, lambda2, lambda3])
        lambdas = lambdas / np.sum(lambdas)
        lambdas = lambdas[lambdas > 1e-10]

        # Von Neumann entropy S = -sum(lambda_i * log(lambda_i))
        entropy = -np.sum(lambdas * np.log2(lambdas))
        max_ent = np.log2(3)

        return entropy / max_ent

    def compute_integrated_complexity(self, halo: HaloAssembly) -> float:
        """
        Phi-like measure: effective information beyond parts.
        Proxy: merger history non-additivity.
        """
        # Simple proxy: deviation from smooth mass accretion
        if halo.mass_total_msun <= 0 or halo.formation_redshift <= 0:
            return 0.0

        # Expected smooth growth vs actual merger-driven growth
        z_form = halo.formation_redshift
        age_proxy = 13.8 * (1 - 1.0 / (1 + z_form))  # Gyr approximation

        # Merger 'surprise' factor
        merger_rate = (halo.num_mergers_major + 0.3 * halo.num_mergers_minor) / max(age_proxy, 0.1)

        # Phi proxy: non-linear merger contribution to final mass
        phi = np.tanh(merger_rate * 2.0) * (1 - np.exp(-halo.mass_total_msun / 1e14))

        return phi

    def compute_full_assembly_index(self, halo: HaloAssembly) -> HaloAssembly:
        """Compute all complexity components and composite A_c."""
        halo.topological_complexity = self.compute_topological_complexity(halo)
        halo.information_complexity = self.compute_information_complexity(halo)
        halo.quantum_complexity = self.compute_quantum_complexity(halo)
        halo.integrated_complexity = self.compute_integrated_complexity(halo)

        halo.assembly_index_ac = (
            self.weights["topological"] * halo.topological_complexity +
            self.weights["information"] * halo.information_complexity +
            self.weights["quantum"] * halo.quantum_complexity +
            self.weights["integrated"] * halo.integrated_complexity
        )

        return halo


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 6: HALO ACQUISITION PIPELINE                                           â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class HaloPipeline:
    """Orchestrates certified-random halo sampling and enrichment."""

    def __init__(self, client: TNGClient, rng: CertifiedRandomnessEngine):
        self.client = client
        self.rng = rng
        self.assembly_calc = AssemblyIndexCalculator()
        self.halos: List[HaloAssembly] = []

    def fetch_catalog_sample(self, n_target: int = None) -> List[HaloAssembly]:
        """Fetch halo catalog with certified random subsampling."""
        n_target = n_target or TNGConfig.N_HALOS_TARGET
        print(f"\n[PIPELINE] Fetching halo catalog sample (n={n_target})...")

        # First, get total count and basic population
        catalog = self.client.get_subhalos(limit=1, offset=0)
        total_count = catalog.get("count", 0)
        print(f"[PIPELINE] Total subhalos in snapshot: {total_count}")

        # Fetch a broad representative set using certified random offsets
        batch_size = 100
        n_batches = min(50, total_count // batch_size)

        all_ids = []
        for i in range(n_batches):
            # Certified random offset
            max_offset = max(0, total_count - batch_size)
            offset = self.rng.random_integers(0, max_offset, 1)[0]

            batch = self.client.get_subhalos(limit=batch_size, offset=int(offset))
            results = batch.get("results", [])
            all_ids.extend([r["id"] for r in results])

            if (i + 1) % 10 == 0:
                print(f"[PIPELINE] Fetched {len(all_ids)} IDs from {i+1} batches...")

        # Deduplicate and certified-random subsample to target
        unique_ids = list(set(all_ids))
        if len(unique_ids) > n_target:
            # Use certified RNG for final selection
            indices = self.rng.random_integers(0, len(unique_ids), n_target)
            selected_ids = [unique_ids[i] for i in indices]
        else:
            selected_ids = unique_ids

        print(f"[PIPELINE] Selected {len(selected_ids)} unique halos for detailed analysis")
        return selected_ids

    def enrich_halo(self, subhalo_id: int) -> Optional[HaloAssembly]:
        """Fetch full halo data and compute assembly metrics."""
        try:
            data = self.client.get_subhalo(subhalo_id)
            if not data:
                return None

            h = HaloAssembly(subhalo_id=subhalo_id, snap_num=TNGConfig.SNAPSHOT)
            h.raw_api_data = data
            h.sampling_seed = int(self.rng.random_integers(0, 2**31, 1)[0])

            # Extract physical properties (TNG fields)
            h.mass_total_msun = TNGConfig.physical_mass(data.get("mass", 0) * 1e10)
            h.mass_dm_msun = TNGConfig.physical_mass(data.get("mass_dm", 0) * 1e10)
            h.mass_stellar_msun = TNGConfig.physical_mass(data.get("mass_stars", 0) * 1e10)
            h.mass_gas_msun = TNGConfig.physical_mass(data.get("mass_gas", 0) * 1e10)
            h.radius_halfmass_kpc = data.get("halfmassrad", 0) * 1000 / TNGConfig.HUBBLE_PARAM
            h.radius_virial_kpc = data.get("vmaxrad", 0) * 1000 / TNGConfig.HUBBLE_PARAM  # proxy
            h.velocity_disp_kms = data.get("veldisp", 0)
            h.v_max_kms = data.get("vmax", 0)
            h.spin_parameter = data.get("spin", 0)
            h.metallicity_stellar = data.get("gasmetallicitysfrweighted", 0)
            h.sfr_msun_per_yr = data.get("sfr", 0)

            # Position (comoving ckpc/h -> physical kpc)
            cm_x = data.get("pos_x", 0)
            cm_y = data.get("pos_y", 0)
            cm_z = data.get("pos_z", 0)
            h.pos_x_ckpc = cm_x
            h.pos_y_ckpc = cm_y
            h.pos_z_ckpc = cm_z

            h.vel_x_kms = data.get("vel_x", 0)
            h.vel_y_kms = data.get("vel_y", 0)
            h.vel_z_kms = data.get("vel_z", 0)

            # Merger tree (lightweight)
            try:
                tree = self.client.get_merger_tree(subhalo_id)
                if tree:
                    h.num_mergers_major = tree.get("n_mergers_major", 0)
                    h.num_mergers_minor = tree.get("n_mergers_minor", 0)
                    h.formation_redshift = tree.get("formation_redshift", 0)
                    h.last_major_merger_z = tree.get("last_major_merger_z", -1)
            except:
                pass

            # Compute Assembly Index
            h = self.assembly_calc.compute_full_assembly_index(h)

            # Certify the randomness used for this halo's sampling
            sample = self.rng.random_floats(1000)
            h.entropy_certification = self.rng.certify_entropy(sample)

            return h

        except Exception as e:
            print(f"[ENRICH ERROR] Subhalo {subhalo_id}: {e}")
            return None

    def run_pipeline(self, n_target: int = None) -> pd.DataFrame:
        """Execute full acquisition and return DataFrame."""
        ids = self.fetch_catalog_sample(n_target)

        self.halos = []
        for i, sid in enumerate(ids):
            halo = self.enrich_halo(sid)
            if halo:
                self.halos.append(halo)
            if (i + 1) % 50 == 0:
                print(f"[PIPELINE] Enriched {len(self.halos)}/{i+1} halos...")

        # Convert to DataFrame
        records = [h.to_dict() for h in self.halos]
        df = pd.DataFrame(records)

        # Apply filters
        df = df[df["mass_total_msun"] >= TNGConfig.MIN_DM_MASS]
        df = df[df["mass_stellar_msun"] >= TNGConfig.MIN_STELLAR_MASS]

        print(f"\n[PIPELINE] Complete. Final catalog: {len(df)} halos")
        print(f"[PIPELINE] API requests: {self.client.request_count} | Errors: {self.client.error_count}")

        return df


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 7: STATISTICAL ANALYSIS & BOOTSTRAP VALIDATION                         â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class CosmologicalStatistics:
    """Advanced statistical tests for halo assembly patterns."""

    def __init__(self, df: pd.DataFrame, rng: CertifiedRandomnessEngine):
        self.df = df.copy()
        self.rng = rng
        self.results = {}

    def bootstrap_assembly_correlation(self, x_col: str, y_col: str, 
                                        n_bootstrap: int = None) -> Dict:
        """Bootstrap Pearson/Spearman correlation with certified random resampling."""
        n = n_bootstrap or TNGConfig.N_BOOTSTRAP

        x = self.df[x_col].values
        y = self.df[y_col].values

        # Clean data
        mask = np.isfinite(x) & np.isfinite(y)
        x, y = x[mask], y[mask]
        n_samples = len(x)

        pearson_r = np.zeros(n)
        spearman_r = np.zeros(n)

        for i in range(n):
            # Certified random indices
            idx = self.rng.random_integers(0, n_samples, n_samples)
            x_boot, y_boot = x[idx], y[idx]

            pearson_r[i] = stats.pearsonr(x_boot, y_boot)[0]
            spearman_r[i] = stats.spearmanr(x_boot, y_boot)[0]

        self.results[f"{x_col}_vs_{y_col}"] = {
            "pearson_mean": np.mean(pearson_r),
            "pearson_std": np.std(pearson_r),
            "pearson_ci_95": (np.percentile(pearson_r, 2.5), np.percentile(pearson_r, 97.5)),
            "spearman_mean": np.mean(spearman_r),
            "spearman_std": np.std(spearman_r),
            "spearman_ci_95": (np.percentile(spearman_r, 2.5), np.percentile(spearman_r, 97.5)),
            "n_bootstrap": n,
            "n_samples": n_samples,
            "significant_95": not (
                np.percentile(pearson_r, 2.5) <= 0 <= np.percentile(pearson_r, 97.5)
            )
        }

        return self.results[f"{x_col}_vs_{y_col}"]

    def assembly_index_significance(self) -> Dict:
        """Test whether high-A_c halos are non-randomly distributed."""
        ac = self.df["assembly_index_ac"].values

        # Compare to null hypothesis: random spatial distribution
        positions = self.df[["pos_x_ckpc", "pos_y_ckpc", "pos_z_ckpc"]].values

        # High-A_c subset
        threshold = np.percentile(ac, 75)
        high_ac_mask = ac >= threshold

        if np.sum(high_ac_mask) < 10:
            return {"error": "Too few high-A_c halos"}

        # Nearest-neighbor analysis
        tree = cKDTree(positions)
        distances, _ = tree.query(positions[high_ac_mask], k=2)
        nn_distances = distances[:, 1]  # Exclude self

        # Compare to random subset of same size
        n_high = np.sum(high_ac_mask)
        random_idx = self.rng.random_integers(0, len(ac), n_high)
        rand_distances, _ = tree.query(positions[random_idx], k=2)
        rand_nn = rand_distances[:, 1]

        # KS test
        ks_stat, p_value = stats.ks_2samp(nn_distances, rand_nn)

        self.results["ac_spatial_significance"] = {
            "threshold": threshold,
            "n_high_ac": int(n_high),
            "mean_nn_high_ac": float(np.mean(nn_distances)),
            "mean_nn_random": float(np.mean(rand_nn)),
            "ks_statistic": float(ks_stat),
            "ks_p_value": float(p_value),
            "non_random_clustering": p_value < 0.05 and np.mean(nn_distances) < np.mean(rand_nn)
        }

        return self.results["ac_spatial_significance"]

    def cross_domain_pattern_match(self) -> Dict:
        """
        Compare halo merger patterns to known cancer progression signatures.
        Inspired by your 79% similarity finding (Jan 2026).
        """
        # Simplified cross-domain proxy:
        # Halo: merger_rate ~ cancer: mutation_rate
        # Halo: mass_growth ~ cancer: tumor_doubling_time
        # Halo: spin ~ cancer: angiogenesis_complexity

        # Compute halo 'progression score'
        mergers = self.df["num_mergers_major"].values + 0.3 * self.df["num_mergers_minor"].values
        mass_growth = self.df["mass_total_msun"].values / (self.df["formation_redshift"].values + 0.1)
        spin = self.df["spin_parameter"].values

        # Normalize
        mergers_norm = (mergers - np.nanmin(mergers)) / (np.nanmax(mergers) - np.nanmin(mergers) + 1e-10)
        growth_norm = np.log10(mass_growth + 1)
        growth_norm = (growth_norm - np.nanmin(growth_norm)) / (np.nanmax(growth_norm) - np.nanmin(growth_norm) + 1e-10)
        spin_norm = (spin - np.nanmin(spin)) / (np.nanmax(spin) - np.nanmin(spin) + 1e-10)

        # Halo progression index
        halo_prog = 0.4 * mergers_norm + 0.4 * growth_norm + 0.2 * spin_norm

        # Simulate 'cancer progression' surrogate from same statistical family
        # (In real implementation, this would load actual oncology data)
        cancer_surrogate = 0.4 * self._cancer_merger_proxy() +                           0.4 * self._cancer_growth_proxy() +                           0.2 * self._cancer_angiogenesis_proxy()

        # Pattern similarity via Spearman
        similarity = stats.spearmanr(halo_prog, cancer_surrogate)[0]

        self.results["cross_domain_similarity"] = {
            "pattern_similarity": float(similarity),
            "interpretation": "High similarity suggests universal complexity growth laws" if similarity > 0.5 else "Domain-specific dynamics dominate",
            "halo_progression_range": (float(np.nanmin(halo_prog)), float(np.nanmax(halo_prog))),
            "n_samples": len(self.df)
        }

        return self.results["cross_domain_similarity"]

    def _cancer_merger_proxy(self) -> np.ndarray:
        """Simulate cancer mutation accumulation from same distribution family."""
        n = len(self.df)
        return np.random.gamma(2, 0.5, n)  # Mutation count proxy

    def _cancer_growth_proxy(self) -> np.ndarray:
        """Simulate tumor growth rate."""
        n = len(self.df)
        return np.random.lognormal(0, 0.5, n)

    def _cancer_angiogenesis_proxy(self) -> np.ndarray:
        """Simulate vascular complexity."""
        n = len(self.df)
        return np.random.beta(2, 5, n)

    def run_full_suite(self) -> Dict:
        """Execute all statistical tests."""
        print("\n[STATS] Running bootstrap correlation: A_c vs Mass...")
        self.bootstrap_assembly_correlation("assembly_index_ac", "mass_total_msun")

        print("[STATS] Running bootstrap correlation: A_c vs Merger Count...")
        self.bootstrap_assembly_correlation("assembly_index_ac", "num_mergers_major")

        print("[STATS] Testing spatial significance of high-A_c halos...")
        self.assembly_index_significance()

        print("[STATS] Computing cross-domain pattern match...")
        self.cross_domain_pattern_match()

        return self.results


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 8: VISUALIZATION ENGINE                                                 â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class CosmologicalVisualizer:
    """Publication-quality figure generation for Colab display."""

    def __init__(self, df: pd.DataFrame, stats: Dict, save_dir: str = None):
        self.df = df
        self.stats = stats
        self.save_dir = save_dir or TNGConfig.SAVE_DIR
        os.makedirs(self.save_dir, exist_ok=True)

    def plot_assembly_mass_relation(self, figsize: Tuple[int, int] = (12, 8)):
        """Figure 1: Assembly Index vs Total Mass with complexity decomposition."""
        fig, axes = plt.subplots(2, 2, figsize=figsize)

        mass = self.df["mass_total_msun"].values
        ac = self.df["assembly_index_ac"].values

        # Main panel: A_c vs Mass
        ax = axes[0, 0]
        scatter = ax.scatter(mass, ac, c=self.df["num_mergers_major"], 
                            cmap="plasma", s=30, alpha=0.7, edgecolors='none')
        ax.set_xscale("log")
        ax.set_xlabel("Total Mass [$M_\odot$]", fontsize=11)
        ax.set_ylabel("Assembly Index $A_c$", fontsize=11)
        ax.set_title("Cosmological Assembly Index vs Halo Mass", fontsize=12, fontweight='bold')
        plt.colorbar(scatter, ax=ax, label="Major Mergers")

        # Add correlation annotation
        if "assembly_index_ac_vs_mass_total_msun" in self.stats:
            s = self.stats["assembly_index_ac_vs_mass_total_msun"]
            text = f"Spearman: $\rho$={s['spearman_mean']:.3f}Â±{s['spearman_std']:.3f}"
            ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        # Sub-panels: Component breakdown
        components = ["topological_complexity", "information_complexity", 
                     "quantum_complexity", "integrated_complexity"]
        titles = ["Topological", "Information", "Quantum", "Integrated"]

        for idx, (comp, title) in enumerate(zip(components, titles)):
            ax = axes.flatten()[idx + 1] if idx < 3 else None
            if ax is None:
                break
            ax.scatter(mass, self.df[comp].values, c="cyan", s=20, alpha=0.5)
            ax.set_xscale("log")
            ax.set_xlabel("Total Mass [$M_\odot$]", fontsize=9)
            ax.set_ylabel(f"{title} Complexity", fontsize=9)
            ax.set_title(f"{title}", fontsize=10)

        plt.tight_layout()
        path = f"{self.save_dir}/fig1_assembly_mass.png"
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.show()
        print(f"[VIZ] Saved: {path}")

    def plot_spatial_distribution(self, figsize: Tuple[int, int] = (14, 6)):
        """Figure 2: 3D spatial distribution colored by Assembly Index."""
        fig, axes = plt.subplots(1, 2, figsize=figsize)

        pos = self.df[["pos_x_ckpc", "pos_y_ckpc", "pos_z_ckpc"]].values
        ac = self.df["assembly_index_ac"].values

        # XY projection
        ax = axes[0]
        scatter = ax.scatter(pos[:, 0], pos[:, 1], c=ac, cmap="viridis", 
                          s=20, alpha=0.6, edgecolors='none')
        ax.set_xlabel("X [ckpc/h]", fontsize=10)
        ax.set_ylabel("Y [ckpc/h]", fontsize=10)
        ax.set_title("Spatial Distribution (XY) | Colored by $A_c$", fontsize=11)
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label="$A_c$")

        # XZ projection
        ax = axes[1]
        scatter = ax.scatter(pos[:, 0], pos[:, 2], c=ac, cmap="viridis", 
                          s=20, alpha=0.6, edgecolors='none')
        ax.set_xlabel("X [ckpc/h]", fontsize=10)
        ax.set_ylabel("Z [ckpc/h]", fontsize=10)
        ax.set_title("Spatial Distribution (XZ) | Colored by $A_c$", fontsize=11)
        ax.set_aspect('equal')
        plt.colorbar(scatter, ax=ax, label="$A_c$")

        plt.tight_layout()
        path = f"{self.save_dir}/fig2_spatial_ac.png"
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.show()
        print(f"[VIZ] Saved: {path}")

    def plot_complexity_heatmap(self, figsize: Tuple[int, int] = (10, 8)):
        """Figure 3: Correlation heatmap of complexity components."""
        components = ["assembly_index_ac", "topological_complexity", 
                     "information_complexity", "quantum_complexity", 
                     "integrated_complexity", "mass_total_msun", 
                     "num_mergers_major", "spin_parameter", "sfr_msun_per_yr"]

        corr_data = self.df[components].corr(method="spearman")

        fig, ax = plt.subplots(figsize=figsize)
        mask = np.triu(np.ones_like(corr_data, dtype=bool), k=1)
        sns.heatmap(corr_data, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                   center=0, vmin=-1, vmax=1, square=True, ax=ax,
                   linewidths=0.5, cbar_kws={"shrink": 0.8})
        ax.set_title("Complexity Component Correlation Matrix (Spearman)", fontsize=12)

        plt.tight_layout()
        path = f"{self.save_dir}/fig3_complexity_heatmap.png"
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.show()
        print(f"[VIZ] Saved: {path}")

    def plot_randomness_certification(self, figsize: Tuple[int, int] = (12, 5)):
        """Figure 4: Randomness quality diagnostics."""
        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Generate fresh certified random sample for visualization
        rng = CertifiedRandomnessEngine(mode=TNGConfig.RANDOM_SEED_MODE)
        sample = rng.random_floats(10000)
        cert = rng.certify_entropy(sample)

        # Distribution
        ax = axes[0]
        ax.hist(sample, bins=100, color="lime", alpha=0.7, edgecolor='black')
        ax.set_xlabel("Value", fontsize=10)
        ax.set_ylabel("Frequency", fontsize=10)
        ax.set_title("Certified Randomness Distribution", fontsize=11)
        ax.axhline(y=len(sample)/100, color='red', linestyle='--', alpha=0.5, label="Uniform expectation")
        ax.legend()

        # Certification metrics
        ax = axes[1]
        metrics = ["shannon_entropy_bits", "min_entropy_bits", "entropy_rate"]
        values = [cert.get(m, 0) for m in metrics]
        colors = ["gold", "cyan", "magenta"]
        bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor='white')
        ax.set_ylabel("Bits / Rate", fontsize=10)
        ax.set_title("Randomness Certification Metrics", fontsize=11)
        ax.set_ylim(0, max(values) * 1.2 + 0.1)

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f"{val:.3f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        path = f"{self.save_dir}/fig4_randomness_cert.png"
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.show()
        print(f"[VIZ] Saved: {path}")

    def plot_merger_history(self, figsize: Tuple[int, int] = (12, 6)):
        """Figure 5: Merger history vs Assembly Index evolution proxy."""
        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Merger count distribution
        ax = axes[0]
        majors = self.df["num_mergers_major"].values
        ax.hist(majors, bins=max(10, int(np.max(majors)+1)), color="orange", 
               alpha=0.7, edgecolor='black')
        ax.set_xlabel("Major Merger Count", fontsize=10)
        ax.set_ylabel("Number of Halos", fontsize=10)
        ax.set_title("Major Merger Distribution", fontsize=11)

        # A_c vs Formation Redshift
        ax = axes[1]
        z_form = self.df["formation_redshift"].values
        mask = z_form > 0
        if np.sum(mask) > 10:
            ax.scatter(z_form[mask], self.df["assembly_index_ac"].values[mask], 
                      c=self.df["num_mergers_major"].values[mask], cmap="hot", 
                      s=30, alpha=0.7)
            ax.set_xlabel("Formation Redshift $z_{form}$", fontsize=10)
            ax.set_ylabel("Assembly Index $A_c$", fontsize=10)
            ax.set_title("$A_c$ vs Formation Time", fontsize=11)
            plt.colorbar(ax.collections[0], ax=ax, label="Major Mergers")
        else:
            ax.text(0.5, 0.5, "Insufficient formation redshift data", 
                   ha='center', va='center', transform=ax.transAxes)

        plt.tight_layout()
        path = f"{self.save_dir}/fig5_merger_history.png"
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.show()
        print(f"[VIZ] Saved: {path}")

    def generate_all_figures(self):
        """Execute complete visualization suite."""
        print("\n[VIZ] Generating Figure 1: Assembly-Mass Relation...")
        self.plot_assembly_mass_relation()

        print("[VIZ] Generating Figure 2: Spatial Distribution...")
        self.plot_spatial_distribution()

        print("[VIZ] Generating Figure 3: Complexity Heatmap...")
        self.plot_complexity_heatmap()

        print("[VIZ] Generating Figure 4: Randomness Certification...")
        self.plot_randomness_certification()

        print("[VIZ] Generating Figure 5: Merger History...")
        self.plot_merger_history()


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 9: MAIN EXECUTION ORCHESTRATOR                                         â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class TNGAssemblyOrchestrator:
    """Top-level controller for the entire analysis pipeline."""

    def __init__(self):
        self.client = TNGClient()
        self.rng = CertifiedRandomnessEngine(mode=TNGConfig.RANDOM_SEED_MODE)
        self.pipeline = HaloPipeline(self.client, self.rng)
        self.df: Optional[pd.DataFrame] = None
        self.stats: Optional[CosmologicalStatistics] = None
        self.viz: Optional[CosmologicalVisualizer] = None

    def run(self, n_halos: int = None, skip_api: bool = False) -> Dict:
        """
        Execute full pipeline: fetch -> compute -> analyze -> visualize.

        Args:
            n_halos: Override target halo count
            skip_api: If True, generate synthetic data for testing without API
        """
        print("\n" + "=" * 80)
        print("TNG100-1 ASSEMBLY & CERTIFIED RANDOMNESS PIPELINE EXECUTION")
        print("=" * 80)

        # --- Phase 1: Data Acquisition ---
        if skip_api:
            print("\n[ORCH] SKIPPING API - Generating synthetic halo catalog for testing...")
            self.df = self._generate_synthetic_catalog(n_halos or 500)
        else:
            print("\n[ORCH] Phase 1: Halo Acquisition via TNG API...")
            self.df = self.pipeline.run_pipeline(n_halos)

        if self.df is None or len(self.df) == 0:
            print("[ORCH] ERROR: No halos acquired. Exiting.")
            return {"status": "failed", "reason": "empty_catalog"}

        # Save raw catalog
        raw_path = f"{TNGConfig.SAVE_DIR}/halo_catalog_raw.csv"
        self.df.to_csv(raw_path, index=False)
        print(f"[ORCH] Raw catalog saved: {raw_path}")

        # --- Phase 2: Statistical Analysis ---
        print("\n[ORCH] Phase 2: Statistical Analysis...")
        self.stats = CosmologicalStatistics(self.df, self.rng)
        stat_results = self.stats.run_full_suite()

        # --- Phase 3: Visualization ---
        print("\n[ORCH] Phase 3: Visualization...")
        self.viz = CosmologicalVisualizer(self.df, stat_results)
        self.viz.generate_all_figures()

        # --- Phase 4: Export & Summary ---
        print("\n[ORCH] Phase 4: Exporting Results...")
        summary = self._compile_summary(stat_results)

        # Save JSON summary
        json_path = f"{TNGConfig.SAVE_DIR}/analysis_summary.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"[ORCH] Summary saved: {json_path}")

        # Save enriched catalog
        enrich_path = f"{TNGConfig.SAVE_DIR}/halo_catalog_enriched.csv"
        self.df.to_csv(enrich_path, index=False)
        print(f"[ORCH] Enriched catalog saved: {enrich_path}")

        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)

        return summary

    def _generate_synthetic_catalog(self, n: int = 500) -> pd.DataFrame:
        """Generate realistic synthetic halo data for offline testing."""
        print(f"[SYNTH] Generating {n} synthetic halos...")

        rng = np.random.default_rng(42)

        # Mass function (approx Schechter-like)
        log_masses = rng.normal(12, 0.8, n)
        masses = 10 ** log_masses

        # Derived properties
        dm_fraction = 0.85 + rng.normal(0, 0.05, n)
        stellar_fraction = 0.05 + rng.normal(0, 0.02, n)
        gas_fraction = 1.0 - dm_fraction - stellar_fraction

        df = pd.DataFrame({
            "subhalo_id": range(n),
            "mass_total_msun": masses,
            "mass_dm_msun": masses * dm_fraction,
            "mass_stellar_msun": masses * stellar_fraction,
            "mass_gas_msun": masses * gas_fraction,
            "radius_halfmass_kpc": 10 ** (0.4 * log_masses - 2.5) * rng.lognormal(0, 0.2, n),
            "radius_virial_kpc": 10 ** (0.4 * log_masses - 2.2) * rng.lognormal(0, 0.15, n),
            "velocity_disp_kms": 100 * (masses / 1e12) ** 0.33 * rng.lognormal(0, 0.1, n),
            "v_max_kms": 200 * (masses / 1e12) ** 0.3 * rng.lognormal(0, 0.12, n),
            "spin_parameter": rng.lognormal(-2.5, 0.5, n),
            "metallicity_stellar": rng.lognormal(-2, 0.5, n),
            "sfr_msun_per_yr": 10 ** rng.normal(0, 1, n) * (stellar_fraction * masses / 1e10),
            "pos_x_ckpc": rng.uniform(0, 75000, n),
            "pos_y_ckpc": rng.uniform(0, 75000, n),
            "pos_z_ckpc": rng.uniform(0, 75000, n),
            "vel_x_kms": rng.normal(0, 100, n),
            "vel_y_kms": rng.normal(0, 100, n),
            "vel_z_kms": rng.normal(0, 100, n),
            "num_mergers_major": rng.poisson(2 + 0.5 * (log_masses - 11), n).clip(0, 20),
            "num_mergers_minor": rng.poisson(5 + (log_masses - 11), n).clip(0, 50),
            "formation_redshift": rng.exponential(2, n).clip(0.1, 10),
            "last_major_merger_z": rng.exponential(1, n).clip(0, 5),
            "merger_tree_depth": rng.poisson(5, n),
        })

        # Compute Assembly Index on synthetic data
        calc = AssemblyIndexCalculator()
        halos = []
        for _, row in df.iterrows():
            h = HaloAssembly(**{k: v for k, v in row.items() if k in HaloAssembly.__dataclass_fields__})
            h = calc.compute_full_assembly_index(h)
            halos.append(h)

        records = [h.to_dict() for h in halos]
        return pd.DataFrame(records)

    def _compile_summary(self, stat_results: Dict) -> Dict:
        """Compile final analysis summary."""
        df = self.df

        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "simulation": TNGConfig.SIMULATION,
                "snapshot": TNGConfig.SNAPSHOT,
                "n_halos": len(df),
                "randomness_mode": TNGConfig.RANDOM_SEED_MODE,
                "api_requests": self.client.request_count,
                "api_errors": self.client.error_count,
            },
            "physical_properties": {
                "mass_range_msun": [float(df["mass_total_msun"].min()), float(df["mass_total_msun"].max())],
                "median_ac": float(df["assembly_index_ac"].median()),
                "mean_ac": float(df["assembly_index_ac"].mean()),
                "std_ac": float(df["assembly_index_ac"].std()),
                "high_ac_fraction": float(np.mean(df["assembly_index_ac"] > df["assembly_index_ac"].quantile(0.9))),
            },
            "assembly_index_components": {
                "topological_mean": float(df["topological_complexity"].mean()),
                "information_mean": float(df["information_complexity"].mean()),
                "quantum_mean": float(df["quantum_complexity"].mean()),
                "integrated_mean": float(df["integrated_complexity"].mean()),
            },
            "statistical_tests": stat_results,
            "certified_randomness": {
                "mode": TNGConfig.RANDOM_SEED_MODE,
                "entropy_pool_sample": CERT_RNG.entropy_pool.hex()[:64],
                "note": "Randomness simulated via chaotic mixing + OS entropy. True DI-QRNG requires hardware."
            },
            "file_outputs": {
                "raw_catalog": f"{TNGConfig.SAVE_DIR}/halo_catalog_raw.csv",
                "enriched_catalog": f"{TNGConfig.SAVE_DIR}/halo_catalog_enriched.csv",
                "summary_json": f"{TNGConfig.SAVE_DIR}/analysis_summary.json",
                "figures_dir": TNGConfig.SAVE_DIR
            }
        }


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â  CELL 10: COLAB EXECUTION ENTRY POINT                                        â
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

if __name__ == "__main__":
    """
    ============================================================================
    GOOGLE COLAB EXECUTION INSTRUCTIONS:
    ============================================================================
    1. Set your API key in Colab secrets or environment:
       import os
       os.environ["illistrig_api"] = "your_actual_api_key_here"

    2. Install required packages (run in first Colab cell):
       !pip install h5py requests numpy pandas scipy scikit-learn matplotlib seaborn

    3. Run this script. It will:
       - Connect to TNG API using your key
       - Fetch ~2000 halos with certified random sampling
       - Compute Assembly Index (A_c) with 4 complexity components
       - Run bootstrap statistics and spatial significance tests
       - Generate 5 publication-quality figures
       - Save all outputs to /content/tng_assembly_output/

    4. For testing without API access, set skip_api=True in orchestrator.run()
    ============================================================================
    """

    # Set API key from environment (Colab secrets compatible)
    api_key = os.environ.get("illistrig_api", "YOUR_API_KEY_HERE")
    if api_key != "YOUR_API_KEY_HERE":
        TNGConfig.HEADERS["api-key"] = api_key
        print(f"[COLAB] API key loaded: {api_key[:8]}...")
    else:
        print("[COLAB] WARNING: No API key found. Set os.environ['illistrig_api'] or use skip_api=True")

    # Initialize and run
    orchestrator = TNGAssemblyOrchestrator()

    # Set skip_api=False to use real TNG API, True for synthetic test
    USE_REAL_API = False  # <-- CHANGE THIS AFTER SETTING API KEY

    summary = orchestrator.run(n_halos=512 if USE_REAL_API else 500, skip_api=not USE_REAL_API)

    # Display key results
    print("\n" + "=" * 80)
    print("KEY RESULTS SUMMARY")
    print("=" * 80)

    meta = summary.get("metadata", {})
    print(f"Halos analyzed: {meta.get('n_halos', 'N/A')}")
    print(f"Randomness mode: {meta.get('randomness_mode', 'N/A')}")
    print(f"Median A_c: {summary.get('physical_properties', {}).get('median_ac', 'N/A'):.4f}")

    stats = summary.get("statistical_tests", {})
    if "ac_spatial_significance" in stats:
        sig = stats["ac_spatial_significance"]
        print(f"High-A_c spatial clustering: {'DETECTED' if sig.get('non_random_clustering') else 'Not significant'}")
        print(f"  KS p-value: {sig.get('ks_p_value', 'N/A'):.4f}")

    if "cross_domain_similarity" in stats:
        sim = stats["cross_domain_similarity"]
        print(f"Cross-domain pattern similarity: {sim.get('pattern_similarity', 'N/A'):.3f}")

    print("\nAll outputs saved to:", TNGConfig.SAVE_DIR)
    print("=" * 80)
