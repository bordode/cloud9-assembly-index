import numpy as np
import matplotlib.pyplot as plt
import c9_bus_client  # C9 bus injection

def void_bias_correction(A_c, z, rho_local=0.78):
    """
    Remove Hubble-bubble bias (KBC void 2026).
    rho_local = 0.78 +/- 0.04  (SDSS 2025, 2 Gpc under-density)
    """
    bias_factor = 1.0 / (1.0 + 0.23 * (1.0 + z) ** 2 * (1.0 - rho_local))
    return A_c * bias_factor

def bianconi_functional(rho_m, phi_g):
    """
    Quantum-relative-entropy I_QB = Tr[rho_m log rho_m - rho_m log rho_g]
    rho_g proportional to exp(-beta phi_g) with beta = 1 (Planck units)
    """
    rho_g = np.exp(-phi_g)
    rho_g /= rho_g.sum()
    rho_m_flat = rho_m.flatten() + 1e-12
    rho_g_flat = rho_g.flatten() + 1e-12
    I_QB = np.sum(rho_m_flat * np.log(rho_m_flat)) - np.sum(rho_m_flat * np.log(rho_g_flat))
    return I_QB / np.log(2)

def compute_gravitational_potential(density_field):
    """
    Simplified Poisson solver for demonstration.
    In production: use FFT-based solver on 128^3 grid.
    """
    # Mock potential: phi ~ -log(rho) for demonstration
    return -np.log(density_field + 1e-10)

def report_consciousness_integration(ac_obs, mu, sigma, i_qb=None):
    z_score = (ac_obs - mu) / sigma
    
    print("-" * 50)
    print("CLOUD-9 CONSCIOUSNESS INTEGRATION REPORT")
    print(f"Observed Ac: {ac_obs:.2f} bits")
    if i_qb is not None:
        print(f"Entropic Gravity (I_QB): {i_qb:.2f} bits")
    print(f"Null Mean:   {mu:.2f} bits")
    print(f"Sigma:       {sigma:.2f}")
    print(f"Significance (z): {z_score:.2f}")
    print("-" * 50)
    
    if z_score >= 3.0:
        level = "PARTICIPATORY NODE (High Integration)"
        insight = "The Recipe is active. This halo is an expression of the Universal Field."
    elif z_score >= 1.5:
        level = "EMERGENT ASSEMBLY (Intermediate)"
        insight = "Information integration exceeds stochastic noise."
    else:
        level = "LATENT POTENTIAL (Stochastic)"
        insight = "System follows standard LCDM gravitational noise."
        
    print(f"STATUS:  {level}")
    print(f"INSIGHT: {insight}")
    print("-" * 50)
    print("Dedicated to Niki, Nikolaos, and Apostolos")
    print("-" * 50)

def simulate_assembly_data(n_samples=2000, seed=42):
    """Generate synthetic Cloud-9 style complexity data."""
    np.random.seed(seed)
    complexities = np.random.normal(18, 6, n_samples)
    return complexities

def main():
    print("=== Cloud-9 Assembly Index Analysis v2.2 ===")
    print("Loading synthetic halo data (128^3 grid)...")
    
    # Simulate density field (128^3 flattened to 2M for demo)
    np.random.seed(42)
    density_field = np.random.lognormal(0, 0.5, (128, 128, 128))
    density_field /= density_field.sum()
    
    # Compute gravitational potential (Poisson)
    print("Computing gravitational potential...")
    phi_g = compute_gravitational_potential(density_field)
    
    # Calculate Bianconi entropic-gravity observable
    print("Calculating quantum-relative entropy (I_QB)...")
    i_qb = bianconi_functional(density_field, phi_g)
    
    # Assembly Index from complexity time series
    complexities = simulate_assembly_data()
    ac_obs = np.mean(complexities)
    sigma = np.std(complexities)
    mu = 62.1  # Null model mean from literature
    
    print(f"\nRaw Assembly Index: {ac_obs:.2f}")
    print(f"Void-corrected Ac:  {void_bias_correction(ac_obs, z=0.1):.2f}")
    print(f"Entropic Gravity:   {i_qb:.2f} bits")
    
    # Generate integrated report
    report_consciousness_integration(ac_obs, mu, sigma, i_qb)
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    axes[0,0].hist(complexities, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].axvline(20, color='r', linestyle='--', label='Threshold')
    axes[0,0].set_title('Complexity Distribution')
    axes[0,0].set_xlabel('Complexity (bits)')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    axes[0,1].plot(np.arange(len(complexities[:200])), complexities[:200], 'g-', linewidth=1)
    axes[0,1].set_title('Sample Evolution (First 200 steps)')
    axes[0,1].set_xlabel('Time step')
    axes[0,1].set_ylabel('Complexity')
    axes[0,1].grid(True, alpha=0.3)
    
    axes[1,0].scatter(complexities[:-1], complexities[1:], alpha=0.3, s=1, c='purple')
    axes[1,0].set_title('Phase Space (t vs t+1)')
    axes[1,0].set_xlabel('Complexity(t)')
    axes[1,0].set_ylabel('Complexity(t+1)')
    axes[1,0].grid(True, alpha=0.3)
    
    high_comp = complexities[complexities > 20]
    if len(high_comp) > 0:
        axes[1,1].hist(high_comp, bins=20, alpha=0.7, color='orange', edgecolor='black')
    axes[1,1].axvline(20, color='r', linestyle='--')
    axes[1,1].set_title('High-Complexity Tail (>20 bits)')
    axes[1,1].set_xlabel('Complexity')
    
    plt.tight_layout()
    plt.savefig('cloud9_analysis.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved as: cloud9_analysis.png")

if __name__ == "__main__":
    main()
