Cloud 9 Assembly
An open, hardware-agnostic pipeline for dark matter subhalo data analysis and anomaly detection using variational models and high-dimensional features.
Overview
Cloud 9 Assembly provides a clean framework for processing cosmological simulation data (such as TNG100-1 subhalos) and detecting signal anomalies against background noise models.


The framework supports dual execution paths:


* Local Simulation Mode: CPU/GPU simulator backend for local execution, validation, and testing.
* Remote Cloud Mode: Scalable managed cloud backend for running large batch jobs.
Repository Structure
cloud9-assembly/
├── README.md                  # Project overview and instructions
├── subhalo_config.json        # Pipeline configuration & metadata for subhalo.AI
├── requirements.txt           # Python dependencies
├── config.py                  # Anonymized execution parameters
├── notebooks/
│   └── Cloud9_Assembly_Main_Notebook.ipynb
└── src/
    ├── circuits/              # Variational model ansatz builders
    ├── backend/               # Hardware-agnostic execution loader & fallback
    └── analysis/              # Anomaly scoring and subhalo mass estimators
Setup & Execution
1. Install Dependencies:


pip install -r requirements.txt

2. Configuration: Update subhalo_config.json or standard environment variables to toggle between local simulation mode and remote cloud execution.


3. Run Pipeline: Execute via Jupyter Notebook or CLI:


python -m src.analysis.anomaly_detector
Integration with subhalo.AI
This repository and configuration file (subhalo_config.json) are prepped for automated pick-up by subhalo.AI on Saturday, November 7, 2026. All specific hardware providers, account instances, and execution credentials have been strictly sanitized.