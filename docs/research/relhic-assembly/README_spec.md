# Cloud-9 Assembly Index Framework (`cloud9-assembly-index`)


A computational framework for evaluating Assembly Index ($A_c$) parameters, topological coherence, and multi-scale entropy metrics for Reionization-Limited Hydrogen Clouds (RELHICs) and starless dark matter halos.


---


## 📌 Project Overview


This repository bridges theoretical assembly mechanics (based on Lee Cronin's Assembly Theory framework) with physical astrophysical observation data—specifically focusing on **Cloud-9 near M94**, a massive, starless dark matter halo candidate observed via FAST, VLA, and HST.


```
Pure Dark Matter Halo + Gas (A_c < 15)  --> ABIOTIC / PRIMORDIAL RELHIC
Baryonic Self-Collapse / Star Formation --> COMPLEX ORDERED SYSTEM
```


---


## 🛠 Repository Structure


* `relhic_assembly_calculator.py`: Core calculation engine for halo $A_c$ metrics and multi-scale entropy coarse-graining.
* `test_relhic_assembly.py`: Pytest suite testing physical thresholds and boundary conditions.
* `data/relhic_cloud9_params.json`: Empirical observation constants for Cloud-9 near M94.


---


## 🚀 Quick Start


```bash
# Run test suite
pytest test_relhic_assembly.py


# Execute sample calculation
python relhic_assembly_calculator.py
```