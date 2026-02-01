```markdown
# Cloud9 Assembly Index

**Cosmological Assembly Index (A_c) Analysis Pipeline**  
*Detect non-random, high-complexity structures in dark matter halos using information-theoretic measures*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/bordode/cloud9-assembly-index)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Easy Start (5 minutes)

### Option A: Docker (Recommended for First-Time Users)
```bash
docker run -v $(pwd)/output:/output bordode/cloud9-assembly-index:easy
```

Output: `cloud9_assembly_analysis.png` + `results.json` in your current directory.

Option B: Native Python

```bash
pip install cloud9-assembly-index
cloud9-download-samples --category demonstration
cloud9-analyze --config easy_demo.yaml --progress
```

What you'll see: A 5-stage progress bar completing in 2 minutes with a multi-panel figure showing assembly index evolution, mutual information trajectories, and significance evaluation against 1,000 null-model halos.

---

✅ Prerequisites Check

Before installation, verify your environment:

```bash
curl -sSL https://raw.githubusercontent.com/bordode/cloud9-assembly-index/main/verify_env.py | python
```

Expected Output:

```
✓ Python 3.9.18 detected (requirement: ≥3.9)
✓ pip 23.2.1 available
✓ 4.2GB disk space available (recommended: ≥2GB)
✓ 16.3GB RAM detected (recommended: ≥8GB for 128³ grid)
⚠ Git not in PATH (optional: for development installation)
Recommendation: Proceed with pip installation or Docker
```

Hardware Requirements:
- Minimum: 8GB RAM (uses 64³ grid, 1 minute execution)
- Recommended: 16GB RAM (uses 128³ grid, 5 minutes execution)
- Storage: 2GB free space for sample data and outputs

---

📦 Installation Options

Level 1: Zero-Configuration (Container)
For reproducible environments without dependency conflicts:

```bash
# Pull and verify
docker pull bordode/cloud9-assembly-index:easy-1.0
docker run --rm bordode/cloud9-assembly-index:easy-1.0 cloud9-verify-install

# Run with sample data (auto-downloaded)
docker run -v $(pwd)/output:/output bordode/cloud9-assembly-index:easy
```

Features:
- Pre-installed Python 3.11, NumPy 1.24+, SciPy 1.10+
- Bundled synthetic halo data (10¹² M⊙, z=0, known A_c = 1.8 bits for validation)
- Reduced 64³ grid for sub-10-minute execution on laptops
- Progress bars with memory reporting and checkpointing

Level 2: Native Installation (pip/conda)

```bash
# Create isolated environment
python -m venv cloud9-env
source cloud9-env/bin/activate  # Windows: cloud9-env\Scripts\activate

# Install with dependencies
pip install cloud9-assembly-index

# Verify installation
cloud9-verify-install
# Should output: "Cloud9 Assembly Index v1.2.0 - All components functional"
```

Dependency Resolution (if conflicts occur):

```bash
# Using conda for BLAS-optimized libraries
conda create -n cloud9 python=3.11 numpy scipy scikit-learn matplotlib
conda activate cloud9
pip install cloud9-assembly-index
```

---

🏃 Running Your First Analysis

Step 1: Download Sample Data (First-Time Setup)

```bash
# Download 3 demonstration halos (10¹¹, 10¹², 10¹³ M⊙) with precomputed validation values
cloud9-download-samples --category demonstration
cloud9-list-samples  # Verify download and view metadata
```

Step 2: Execute with Progress Monitoring

```bash
cloud9-analyze --config easy_demo.yaml --progress --checkpoint-dir ./checkpoints/
```

Real-Time Output:

```
[14:32:01] Cloud9 Assembly Analysis v1.2.0-easy
[14:32:01] Configuration: easy_demo.yaml (Δt=50Myr, 128³ grid, k=20)
[14:32:01] Input: 3 demonstration halos
[14:32:02] Stage 1/5: Density field reconstruction ▓▓▓▓▓▓▓▓▓░ 80% (ETA: 0:00:12)
[14:32:14] Stage 2/5: Merger tree traversal ▓▓▓▓▓▓▓▓▓▓ 100% (3/3 halos complete)
[14:32:45] Stage 3/5: Mutual information estimation ▓▓▓▓▓▓▓░░░ 60% (current: z=1.2)
[14:33:12] Stage 4/5: Null-model calibration (1,000 ensemble halos)
[14:33:58] Stage 5/5: Visualization generation
[14:34:02] Output: cloud9_assembly_analysis.png, results.json, checkpoints/complete/
[14:34:02] Execution complete: 2m 1s total, 1.4GB peak memory
```

Resume after interruption:

```bash
cloud9-analyze --resume ./checkpoints/stage3_z1.2/
```

Step 3: Custom Data Preparation (Your Simulations)

```bash
# Validate format (auto-detects GADGET-4, Aurora, AREPO, HDF5, FITS)
cloud9-validate-data --path ./my_simulation/snap_*.hdf5 --format auto-detect
# Output: detected format, redshift range, particle count, unit consistency status

# Convert to standardized input
cloud9-convert-format --input ./my_simulation/ --output ./cloud9_input/ --grid 128
```

Supported Data Sources:
- Local Simulation Snapshots: GADGET-4, AREPO, Aurora (HDF5 format)
- UniverseMachine Catalog: Query via API with mass/redshift ranges
- Observational Catalogs: JWST/Hubble with photometric redshifts
- Synthetic Generation: On-the-fly halo mass function models

---

📊 Understanding Your Results

Generate guided interpretation:

```bash
cloud9-interpret-results --input results.json --format tutorial
```

Panel-by-Panel Guide

Panel A: Assembly Index Evolution
- Solid curve: Cumulative A_c(z) for analyzed halo
- Shaded region: 1σ scatter from null ensemble (1,000 ΛCDM halos)
- Key feature: Rapid increase at z > 4 indicates early deterministic assembly
- Interpretation: A_c(z=0) = 2.1 bits exceeds 99.7% of null ensemble → "non-trivial assembly"

Panel B: Mutual Information Trajectory
- Content: I[ρ(x,t); ρ(x,t+Δt)] vs. cosmic time
- Physical meaning: Information gain/loss during halo assembly
- Interpretation challenge: High values indicate predictable, non-random structure growth
- Note: k-NN estimator variance shown as error bars; check convergence with k

Panel C: Significance Evaluation
- Vertical line: Observed A_c = 2.1 bits
- Histogram: Null ensemble distribution N(μ=0.8, σ=0.3)
- z-score: 4.3 (>3 threshold for "non-trivial" classification)
- ⚠️ Caution: Single-halo analysis; apply multiple testing correction for sample studies

Panel D: Merger Tree Integration
- Content: Main branch progenitor identification with mass ratios
- Method: Most massive progenitor (MMP) selection at each Δt = 50Myr step
- Validation: Progenitor count per snapshot and branch completeness metrics

---

⚙️ Configuration Guide (Level 2: Guided Configuration)

Interactive setup wizard:

```bash
python -m cloud9.configure
```

Configuration Parameters (with guidance):

```yaml
# Cloud9 Assembly Analysis Configuration
# Generated: 2026-02-01T14:32:01Z

data:
  source_type: "simulation_snapshot"  # Options: simulation_snapshot, universemachine_query, observational_catalog, synthetic
  path_pattern: "./snapshots/snapshot_*.hdf5"
  redshift_range: [0, 10]  # [z_min, z_max] for analysis
  box_size_mpc_h: 100.0  # Simulation box size in Mpc/h
  particle_type: [1]  # GADGET: 1=DM, 4=stars, 5=BH
  coordinate_system: "comoving"  # Options: comoving, physical

processing:
  temporal_resolution_myr: 50  # Δt: time between snapshots for MI calculation
  # Guidance: 50 Myr for z<2, 25 Myr for z>4 (rapid assembly phases)
  # Trade-off: Smaller values improve resolution but increase noise and computation time
  
  grid_resolution: 128  # N for N³ density grid
  # Options: 64³ (fast, ~1 min, laptops), 128³ (standard, ~5 min), 256³ (high-res, ~30 min)
  
  density_assignment: "CIC"  # Options: NGP (fastest), CIC (standard), TSC (smoothest)
  smoothing_scale: null  # Optional Gaussian smoothing in kpc/h

mutual_information:
  estimator: "knn"
  k_neighbors: 20  # Balance: small k (low bias, high variance), large k (smooth, biased)
  # Recommendation: 20 for 128³ grids, scale with sample size
  distance_metric: "euclidean"
  algorithm: "kd_tree"  # Options: brute_force, kd_tree, ball_tree
  bias_correction: "miller_madow"  # Options: none, miller_madow, jackknife

calibration:
  ensemble_source: "universemachine"  # Options: universemachine, illustris_tng, eagle, custom_catalog
  ensemble_size: 10000  # Statistical power: 1000 (exploratory), 10000 (publication), 100000 (precision)
  matching_criteria: ["mass_final", "formation_time"]  # Halo properties for fair comparison
  # Note: UniverseMachine requires network access for catalog query; firewall/proxy configuration may be needed

significance:
  threshold_type: "fixed"  # Options: fixed, adaptive_fdr
  fixed_threshold_z: 3.0  # Standard 3-sigma for "non-trivial assembly" claim
  # Warning: z > 3 borrowed from particle physics; consider look-elsewhere effects for multiple halo testing
  # Astronomy convention often uses 5-sigma for discovery claims

output:
  figure_path: "./cloud9_assembly_analysis.png"
  report_format: ["json", "hdf5"]  # Structured data for downstream analysis
  checkpoint_dir: "./checkpoints/"  # Enable interruption recovery
  verbosity: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

advanced:
  entropy_bias_correction: "miller_madow"
  void_correction_enabled: true  # Adjust for local density environment
  quadrature_rule: "trapezoidal"  # Options: trapezoidal, simpsons, adaptive
  consciousness_reporting: false  # Suppress undocumented diagnostic output
```

Resource-Aware Auto-Scaling:
- Laptop (8GB RAM): Auto-selects 64³ grid, 1,000-halo ensemble, 2 minutes
- Workstation (16GB+ RAM): Auto-selects 128³ grid, 10,000-halo ensemble, 5 minutes
- HPC Cluster: Configurable 256³ grid, custom ensemble sizes with MPI support

---

🧬 Advanced Usage (Level 3: Full API Control)

Programmatic Python API:

```python
from cloud9 import AssemblyAnalyzer, Config

# Load configuration
config = Config.load("custom_config.yaml")
config.processing.grid_resolution = 256  # Override specific parameters

# Initialize analyzer
analyzer = AssemblyAnalyzer(config)

# Run analysis with full control
result = analyzer.run(halo_catalog_path="./my_halos/", 
                     checkpoint_dir="./checkpoints/",
                     resume_from="./checkpoints/stage2/")

# Access intermediate results
print(f"Assembly Index at z=0: {result.assembly_index:.2f} bits")
print(f"Significance: {result.z_score:.2f} sigma")
print(f"Null-model percentile: {result.percentile:.1f}%")

# Custom visualization
fig = result.plot(panels=['assembly_index', 'mutual_info', 'significance', 'merger_tree'])
fig.save("custom_output.pdf", dpi=300)

# Batch processing
halos = ["halo_001.hdf5", "halo_002.hdf5", "halo_003.hdf5"]
for halo in halos:
    result = analyzer.run(halo)
    result.save(f"./outputs/{halo}_results.json")
```

Modular Pipeline Access:

```python
from cloud9.density import DensityField
from cloud9.entropy import MutualInformationEstimator
from cloud9.assembly import AssemblyIndex

# Step-by-step execution for custom workflows
density = DensityField.from_particles(particle_data, grid_resolution=128)
density_smooth = density.apply_smoothing(scale=50)  # kpc/h

mi_estimator = MutualInformationEstimator(k=20, algorithm='kd_tree')
mi_values = mi_estimator.fit_transform(density_snapshots)  # List of density fields

assembly = AssemblyIndex(integration_method='trapezoidal')
a_c = assembly.compute(mi_values, redshifts=redshift_array)
```

---

🛠️ Technical Implementation

Pipeline Stages with Verification Checkpoints

Stage	Operations	Typical Runtime	Verification Checkpoint	
1. Data Ingestion	Format detection, validation, unit conversion	1-5 min	File header validation; particle count confirmation; checksum verification	
2. Density Field	Gridding, normalization, smoothing	10-30 min	Grid statistics (mean density, dynamic range); memory usage report; mass conservation check	
3. Mutual Information	k-NN searches, entropy calculation, bias correction	30-120 min	Neighbor count distribution; entropy convergence with k; variance estimate	
4. Merger Tree	Progenitor identification, branch selection, temporal alignment	5-15 min	Progenitor count per snapshot; branch completeness metric; merger event catalog	
5. Calibration	Null ensemble comparison, significance evaluation	1-5 min	Null-model distribution statistics; coverage assessment; p-value calibration	
6. Visualization	Multi-panel layout, color mapping, annotation	1-2 min	Multi-panel preview; figure dimension verification; metadata embedding	

Error Handling and Recovery

Error Category	Detection	User Message	Recovery Action	
Python Version Conflict	Import stage	"NumPy 1.19 detected, 1.24 required for array protocol compatibility"	Auto-suggest conda/pip upgrade command with version pinning	
Insufficient Memory	Grid allocation	"128³ grid requires 8.2GB RAM, 4.1GB available"	Offer 64³ fallback with accuracy estimate; disk-backed array option	
Data Format Incompatibility	Validation stage	"HDF5 file missing 'PartType1/Coordinates' dataset"	Suggest format conversion utility with example; metadata extraction guidance	
Network Timeout (UniverseMachine)	Ensemble query	"Catalog query timeout after 60s"	Enable local caching, reduced ensemble fallback, retry with exponential backoff	
Numerical Instability	MI estimation	"k-NN search found identical points (possible duplicate data)"	Suggest jitter addition or deduplication; alternative estimator fallback	
Checkpoint Corruption	Resume attempt	"Checkpoint from v1.1.0 incompatible with v1.2.0"	Offer restart or version rollback with migration guidance	

Command-Line Reference

```bash
cloud9-analyze          # Main analysis pipeline
  --config PATH         # Configuration file (YAML)
  --progress            # Show progress bars and ETA
  --checkpoint-dir DIR  # Enable resume capability
  --resume PATH         # Resume from checkpoint
  --output-dir DIR      # Output directory (default: ./)
  --verbose LEVEL       # DEBUG, INFO, WARNING, ERROR

cloud9-validate-data    # Check input data format and integrity
  --path PATTERN        # File glob pattern
  --format FORMAT       # Auto-detect, gadget4, arepo, hdf5, fits

cloud9-convert-format   # Convert simulation data to standard format
  --input DIR           # Input directory
  --output DIR          # Output directory
  --grid N              # Grid resolution (64, 128, 256)

cloud9-download-samples # Get demonstration data
  --category TYPE       # demonstration, validation, stress_test

cloud9-interpret-results # Guided results interpretation
  --input JSON          # results.json file
  --format TYPE         # tutorial, technical, json

cloud9-verify-install   # Post-installation smoke test
```

---

🐛 Troubleshooting Common Issues

Issue: `git clone` fails with "filename too long" error (exit code 128)

Cause: Legacy filesystem limit (255 bytes) with philosophical manifesto filenames

Fix: 

```bash
# Use shallow clone to avoid long filenames
git clone --depth 1 https://github.com/bordode/cloud9-assembly-index.git
# Or download ZIP release from GitHub Releases page
```

Issue: `ImportError: NumPy ABI mismatch`

Fix:

```bash
pip uninstall numpy scipy cloud9-assembly-index
pip install numpy==1.24.3 scipy==1.10.1 cloud9-assembly-index
```

Issue: Memory exhaustion during Stage 3 (k-NN search)

Fix:

```bash
# Use reduced grid configuration
cloud9-analyze --config easy_demo.yaml  # Uses 64³ grid instead of 128³
# Or enable disk-backed arrays (slower but memory-efficient)
export CLOUD9_MEMORY_MODE=disk
```

Issue: UniverseMachine catalog access fails behind institutional firewall

Fix:

```bash
# Configure proxy
export HTTPS_PROXY=http://proxy.institution.edu:8080
# Or use local ensemble fallback
cloud9-analyze --config local_config.yaml  # Uses pre-downloaded ensemble
```

---

📚 Citation and References

If you use Cloud9 Assembly Index in your research, please cite:

```bibtex
@software{cloud9_assembly_index,
  author = {Bordo de},
  title = {Cloud9 Assembly Index: Cosmological Complexity Analysis},
  url = {https://github.com/bordode/cloud9-assembly-index},
  version = {1.2.0},
  year = {2026},
}

@article{assembly_index_cosmology,
  title={Detecting Non-Random Structure in Dark Matter Halos via Information-Theoretic Assembly Indices},
  journal={The Astrophysical Journal},
  year={2026},
  note={In preparation}
}
```

Methodology References:
- Kraskov, Stögbauer & Grassberger (2004) - k-NN entropy estimation
- Bianconi (2001) - Entropic gravity functional formulation
- UniverseMachine: Behroozi et al. (2019) - Null-model calibration data

---

🧩 Architecture Overview

Tiered User Access:
- Level 1 (Zero-Config): Docker container with bundled sample data, 5-minute demo
- Level 2 (Guided): Interactive configuration wizard, custom data integration, resource-aware scaling
- Level 3 (Expert): Full API access, modular pipeline components, custom algorithms

Core Modules:
- `cloud9.density` - Density field reconstruction (NGP/CIC/TSC)
- `cloud9.entropy` - Mutual information estimation (k-NN, KSG estimator)
- `cloud9.assembly` - Temporal integration and Assembly Index computation
- `cloud9.calibration` - Null-model ensemble generation and significance testing
- `cloud9.visualize` - Publication-ready figure generation
- `cloud9.config` - Configuration validation and serialization

---

🔒 Ethics and Methodology Notes

The Consciousness Integration Reporting functionality referenced in commit history is available as an optional diagnostic metric for algorithmic behavior analysis. Enable with:

```yaml
advanced:
  consciousness_reporting: true  # Default: false
```

This feature provides quantitative metrics regarding information integration complexity. It does not make claims regarding phenomenal consciousness or observer effects in quantum systems.

The 7.83 Hz Schumann Resonance reference in legacy documentation is preserved as a metaphorical framework only. No operational synchronization or audio components are involved in computational execution. The repository focuses exclusively on cosmological structure formation analysis via statistical mechanics and information theory.

---

📞 Support and Contribution

- Bug Reports: GitHub Issues with `verify_env.py` output attached
- Feature Requests: GitHub Discussions
- Contributing: See CONTRIBUTING.md for development setup (Level 3 API required)
- License: MIT License - See LICENSE file for details

Repository Structure:

```
cloud9-assembly-index/
├── README.md                   # This file
├── verify_env.py              # Environment checker
├── easy_demo.yaml             # Quick-start configuration
├── examples/                  # Jupyter notebooks and tutorials
├── cloud9/                    # Main package
│   ├── density.py
│   ├── entropy.py
│   ├── assembly.py
│   ├── calibration.py
│   └── cli.py
├── tests/                     # Validation suite
├── checkpoints/               # Resume-state storage (gitignored)
└── output/                    # Default results directory (gitignored)
```

---

Generated for Cloud9 Assembly Index v1.2.0 - "Easy Format" Implementation

Last Updated: 2026-02-01

```
