import numpy as np

def map_to_3d_temporal_manifold(t_series: np.ndarray, mode: str = "full_3d"):
    """
    Projects linear time into a 3D temporal geometry.
    Used for detecting Berry Phase and cyclic resonance in the X-Field.
    """
    t_min = t_series.min()
    t_max = t_series.max()
    epsilon = 1e-10
    
    # τ₁: Linear Causal Time (The standard arrow)
    tau_1 = t_series
    
    # τ₂ & τ₃: The cyclic phase dimensions (Schumann resonance loops)
    # Mapping to a cylindrical/toroidal surface
    phase = 2 * np.pi * (t_series - t_min) / (t_max - t_min + epsilon)
    tau_2 = np.cos(phase)
    tau_3 = np.sin(phase)
    
    if mode == "full_3d":
        return np.column_stack([tau_1, tau_2, tau_3])
    return tau_1

def compute_berry_curvature(phase_series: np.ndarray):
    """
    Calculates the geometric phase (Berry Phase) curvature.
    High curvature indicates the presence of a 'Participatory Node'.
    """
    # Simple discrete curl of the phase connections
    curvature = np.diff(np.angle(np.exp(1j * phase_series)))
    return np.sum(np.abs(curvature))
  
