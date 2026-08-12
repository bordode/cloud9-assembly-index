import numpy as np
from scipy import stats, spatial
from scipy.spatial.distance import cdist
from scipy.stats import entropy
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List, Optional, Callable
from enum import Enum
import warnings

# ============================================================================
# CORE CLOUD-9 ASSEMBLY INDEX FRAMEWORK WITH EXTENSIONS
# ============================================================================

class TemporalMode(Enum):
    """Three-dimensional time implementation"""
    CLASSICAL = 1      # Standard 1D time
    BERRY_PHASE = 2    # 2D temporal manifold (cyclic time)
    FULL_3D = 3        # Kletetschka-inspired 3D temporal geometry

@dataclass
class AssemblyResult:
    """Container for Cloud-9 assembly analysis"""
    A_c: float                      # Assembly index in bits
    z_score: float                  # Significance vs. random
    status: str                     # 'RANDOM', 'PARTICIPATORY', 'INTEGRATED'
    temporal_mode: TemporalMode
    phase_locking: float            # Degree of standing-wave coherence
    berry_curvature: Optional[np.ndarray]  # For quasi-particle detection
    temporal_entanglement: float    # Non-local temporal correlations

class Cloud9Analyzer:
    """
    Enhanced Cloud-9 Assembly Index calculator with:
    - 3D temporal manifold support
    - Geometric phase (Berry curvature) detection
    - Time-crystal-like periodicity analysis
    - Field coherence quantification
    """
    
    def __init__(self, grid_size: int = 128, k_neighbors: int = 10):
        self.grid_size = grid_size
        self.k = k_neighbors
        self.epsilon = 1e-10
        
    def compute_mutual_information(self, 
                                   X: np.ndarray, 
                                   Y: np.ndarray,
                                   temporal_mode: TemporalMode = TemporalMode.CLASSICAL
                                   ) -> float:
        """
        Mutual information with 3D temporal support
        I(X;Y) = H(X) + H(Y) - H(X,Y)
        
        For 3D time: X, Y are points in temporal manifold τ = (τ₁, τ₂, τ₃)
        """
        if temporal_mode == TemporalMode.CLASSICAL:
            # Standard k-NN entropy estimation (Kraskov-Stögbauer-Grassberger)
            return self._ksg_mi(X, Y)
        
        elif temporal_mode == TemporalMode.BERRY_PHASE:
            # 2D cyclic time: account for periodic boundary conditions
            X_wrapped = self._wrap_temporal_coordinates(X)
            Y_wrapped = self._wrap_temporal_coordinates(Y)
            return self._ksg_mi(X_wrapped, Y_wrapped)
        
        elif temporal_mode == TemporalMode.FULL_3D:
            # Full 3D temporal geometry with geodesic distance
            X_geo = self._temporal_geodesic_embed(X)
            Y_geo = self._temporal_geodesic_embed(Y)
            return self._ksg_mi(X_geo, Y_geo)
    
    def _ksg_mi(self, X: np.ndarray, Y: np.ndarray) -> float:
        """KSG k-nearest neighbor mutual information estimator"""
        n = X.shape[0]
        
        # Joint space
        XY = np.hstack([X, Y])
        
        # Find k-th nearest neighbor distances in joint space
        tree_xy = spatial.cKDTree(XY)
        dists_xy, _ = tree_xy.query(XY, k=self.k+1)
        epsilon = dists_xy[:, self.k] + self.epsilon
        
        # Count neighbors within epsilon in marginal spaces
        tree_x = spatial.cKDTree(X)
        tree_y = spatial.cKDTree(Y)
        
        n_x = np.array([len(tree_x.query_ball_point(X[i], r=epsilon[i]-self.epsilon)) 
                        for i in range(n)]) - 1
        n_y = np.array([len(tree_y.query_ball_point(Y[i], r=epsilon[i]-self.epsilon)) 
                        for i in range(n)]) - 1
        
        # Digamma corrections
        hx = np.mean(np.log(n_x + self.epsilon))
        hy = np.mean(np.log(n_y + self.epsilon))
        hxy = np.mean(np.log(epsilon)) + np.log(n)  # Simplified
        
        # MI estimate
        mi = (np.log(n) + np.log(self.k) - np.mean(np.log(n_x + 1)) - 
              np.mean(np.log(n_y + 1)) + np.log(self.k))
        
        return max(0, mi)
    
    def _wrap_temporal_coordinates(self, X: np.ndarray) -> np.ndarray:
        """Map linear time to cylindrical manifold (Berry phase)"""
        # τ₁ = linear time, τ₂ = phase (cyclic)
        t = X[:, 0]
        phase = 2 * np.pi * (t - t.min()) / (t.max() - t.min() + self.epsilon)
        
        return np.column_stack([
            np.cos(phase),  # τ₂₁
            np.sin(phase),  # τ₂₂
            np.log1p(t - t.min())  # τ₁ (log-compressed linear)
        ])
    
    def _temporal_geodesic_embed(self, X: np.ndarray) -> np.ndarray:
        """
        Embed in 3D temporal manifold with metric:
        ds² = -dτ₁² + dτ₂² + dτ₃² (signature -,+,+)
        """
        t = X[:, 0]
        
        # Three temporal dimensions
        tau_1 = t  # Causal time
        tau_2 = np.sin(2 * np.pi * t / (t.max() - t.min() + self.epsilon))  # Alternatives
        tau_3 = np.cos(2 * np.pi * t / (t.max() - t.min() + self.epsilon))  # Transitions
        
        # Geodesic distance embedding (simplified)
        return np.column_stack([tau_1, tau_2, tau_3])
    
    def compute_assembly_index(self,
                               density_snapshots: List[np.ndarray],
                               merger_tree: Optional[np.ndarray] = None,
                               temporal_mode: TemporalMode = TemporalMode.CLASSICAL
                               ) -> AssemblyResult:
        """
        Calculate Cloud-9 Assembly Index A_c
        
        A_c = ∫ I(ρ(t); ρ(t+Δt)) dt / Δt_min
        """
        n_snapshots = len(density_snapshots)
        
        # Flatten 3D grids to feature vectors
        features = [snap.flatten() for snap in density_snapshots]
        
        # Temporal mutual information integration
        mi_values = []
        for i in range(n_snapshots - 1):
            X = features[i].reshape(-1, 1)
            Y = features[i+1].reshape(-1, 1)
            mi = self.compute_mutual_information(X, Y, temporal_mode)
            mi_values.append(mi)
        
        # Assembly index: cumulative mutual information
        A_c = np.sum(mi_values)
        
        # Compare to random expectation (permutation null)
        A_c_random = self._null_assembly_index(features, temporal_mode)
        z_score = (A_c - A_c_random['mean']) / (A_c_random['std'] + self.epsilon)
        
        # Determine status
        if z_score < 1.0:
            status = 'RANDOM'
        elif z_score < 3.0:
            status = 'PARTICIPATORY'
        else:
            status = 'INTEGRATED'
        
        # Phase locking (time-crystal indicator)
        phase_locking = self._compute_phase_locking(mi_values)
        
        # Berry curvature (if merger tree provided)
        berry_curvature = None
        if merger_tree is not None:
            berry_curvature = self._compute_berry_curvature(merger_tree)
        
        # Temporal entanglement (3D time only)
        temporal_entanglement = 0.0
        if temporal_mode == TemporalMode.FULL_3D:
            temporal_entanglement = self._compute_temporal_entanglement(features)
        
        return AssemblyResult(
            A_c=A_c,
            z_score=z_score,
            status=status,
            temporal_mode=temporal_mode,
            phase_locking=phase_locking,
            berry_curvature=berry_curvature,
            temporal_entanglement=temporal_entanglement
        )
    
    def _null_assembly_index(self, features: List[np.ndarray], 
                             temporal_mode: TemporalMode) -> dict:
        """Generate null distribution by temporal permutation"""
        n_permutations = 100
        A_c_values = []
        
        for _ in range(n_permutations):
            shuffled = features.copy()
            np.random.shuffle(shuffled)
            
            mi_perm = []
            for i in range(len(shuffled) - 1):
                X = shuffled[i].reshape(-1, 1)
                Y = shuffled[i+1].reshape(-1, 1)
                mi_perm.append(self.compute_mutual_information(X, Y, temporal_mode))
            
            A_c_values.append(np.sum(mi_perm))
        
        return {
            'mean': np.mean(A_c_values),
            'std': np.std(A_c_values)
        }
    
    def _compute_phase_locking(self, mi_values: List[float]) -> float:
        """
        Detect time-crystal-like periodicity in mutual information
        High phase_locking → stable temporal oscillation (standing wave)
        """
        if len(mi_values) < 4:
            return 0.0
        
        # Look for periodicity via autocorrelation
        mi_series = np.array(mi_values)
        mi_normalized = mi_series - np.mean(mi_series)
        
        autocorr = np.correlate(mi_normalized, mi_normalized, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / (autocorr[0] + self.epsilon)
        
        # Find first peak after lag 0
        peaks = []
        for i in range(1, len(autocorr)-1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append((i, autocorr[i]))
        
        if not peaks:
            return 0.0
        
        # Phase locking strength = peak correlation / decay envelope
        first_peak = max(peaks, key=lambda x: x[1])
        return first_peak[1]
    
    def _compute_berry_curvature(self, merger_tree: np.ndarray) -> np.ndarray:
        """
        Compute Berry curvature from merger tree topology
        Indicates quasi-particle nature of halo
        """
        # merger_tree: [snapshot, mass, position_x, position_y, position_z, ...]
        
        # Gauge field from merger history
        n_snapshots = int(merger_tree[:, 0].max()) + 1
        
        # Berry connection: phase of density field
        berry_connections = []
        
        for t in range(n_snapshots - 1):
            mask_t = merger_tree[:, 0] == t
            mask_tp1 = merger_tree[:, 0] == t + 1
            
            if not np.any(mask_t) or not np.any(mask_tp1):
                continue
            
            # Density field gradient
            pos_t = merger_tree[mask_t, 2:5]
            mass_t = merger_tree[mask_t, 1]
            
            pos_tp1 = merger_tree[mask_tp1, 2:5]
            mass_tp1 = merger_tree[mask_tp1, 1]
            
            # Connection coefficient (simplified)
            A_t = np.angle(np.sum(mass_t * np.exp(1j * np.linalg.norm(pos_t, axis=1))))
            A_tp1 = np.angle(np.sum(mass_tp1 * np.exp(1j * np.linalg.norm(pos_tp1, axis=1))))
            
            berry_connections.append(A_tp1 - A_t)
        
        # Curvature = curl of connection
        curvature = np.diff(berry_connections) if len(berry_connections) > 1 else [0]
        
        return np.array(curvature)
    
    def _compute_temporal_entanglement(self, features: List[np.ndarray]) -> float:
        """
        Non-local temporal correlations (3D time only)
        MI between distant 'times' should decay slower than exponential
        if temporal manifold is curved
        """
        n = len(features)
        if n < 4:
            return 0.0
        
        # Compute MI between distant snapshots
        mi_distant = []
        for i in range(n):
            for j in range(i+2, min(i+5, n)):  # Skip adjacent
                X = features[i].reshape(-1, 1)
                Y = features[j].reshape(-1, 1)
                mi = self.compute_mutual_information(X, Y, TemporalMode.FULL_3D)
                mi_distant.append((j-i, mi))
        
        if not mi_distant:
            return 0.0
        
        # Fit decay: power-law vs. exponential
        distances = np.array([x[0] for x in mi_distant])
        mis = np.array([x[1] for x in mi_distant])
        
        # Power law: MI ~ d^(-α)
        log_d = np.log(distances + self.epsilon)
        log_mi = np.log(mis + self.epsilon)
        
        slope, _, r_value, _, _ = stats.linregress(log_d, log_mi)
        
        # If power law (linear in log-log), temporal entanglement is high
        # If exponential (curved), entanglement is low
        return abs(r_value) if slope < 0 else 0.0


# ============================================================================
# TIME CRYSTAL ANALYZER (for validation against IBM 144-qubit results)
# ============================================================================

class TimeCrystalAnalyzer:
    """
    Analyze quantum/classical systems for time-crystal behavior
    Directly applicable to KiSS-SIDM resonance experiments
    """
    
    def __init__(self, sampling_rate: float = 1e6):
        self.fs = sampling_rate
        
    def detect_temporal_periodicity(self, 
                                     signal: np.ndarray,
                                     threshold: float = 0.8
                                     ) -> dict:
        """
        Detect stable periodicity indicating time-crystal phase
        """
        # FFT for frequency content
        fft = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1/self.fs)
        power = np.abs(fft)**2
        
        # Find dominant frequencies
        peaks = self._find_peaks(power, threshold)
        
        # Temporal autocorrelation for stability
        autocorr = self._temporal_autocorrelation(signal)
        
        # Phase diagram reconstruction (history dependence)
        phase_diagram = self._reconstruct_phase_space(signal)
        
        return {
            'dominant_freqs': freqs[peaks] if peaks else [],
            'periodicity_strength': np.max(power) / (np.mean(power) + 1e-10),
            'autocorr_decay_time': self._estimate_decay(autocorr),
            'phase_space_attractors': self._count_attractors(phase_diagram),
            'is_time_crystal': len(peaks) > 0 and self._estimate_decay(autocorr) > len(signal)/2
        }
    
    def analyze_kiss_sidm(self,
                          time_series: np.ndarray,
                          injection_freq: float = 7830.0,  # 7.83 kHz
                          trigger_time: float = 72.4
                          ) -> dict:
        """
        Specific analysis for KiSS-SIDM 7.83 kHz Schumann resonance experiments
        """
        # Segment: pre-trigger, trigger, post-trigger
        pre = time_series[time_series[:, 0] < trigger_time]
        post = time_series[time_series[:, 0] >= trigger_time]
        
        # Q-factor evolution
        q_pre = self._compute_q_factor(pre, injection_freq)
        q_post = self._compute_q_factor(post, injection_freq)
        
        # Phase locking emergence
        phase_lock = self._compute_phase_locking_degree(pre, post, injection_freq)
        
        # Attractor basin analysis (history dependence)
        basin = self._attractor_basin_analysis(time_series, injection_freq)
        
        return {
            'Q_pre': q_pre,
            'Q_post': q_post,
            'Q_doubling': q_post / (q_pre + 1e-10),
            'phase_locking_degree': phase_lock,
            'attractor_memory': basin,
            'irreversibility_metric': self._test_irreversibility(time_series)
        }
    
    def _compute_q_factor(self, segment: np.ndarray, 
                          target_freq: float) -> float:
        """Compute quality factor from resonance peak"""
        if len(segment) < 10:
            return 0.0
        
        # Welch's method for PSD
        freqs, psd = signal.welch(segment[:, 1], self.fs, nperseg=min(256, len(segment)//4))
        
        # Find peak near target frequency
        idx = np.argmin(np.abs(freqs - target_freq))
        peak_power = psd[idx]
        
        # Half-power bandwidth
        half_power = peak_power / 2
        above_half = psd > half_power
        
        # Find contiguous region around peak
        left = idx
        while left > 0 and above_half[left]:
            left -= 1
        right = idx
        while right < len(freqs)-1 and above_half[right]:
            right += 1
        
        bandwidth = freqs[right] - freqs[left]
        
        return target_freq / (bandwidth + 1e-10)
    
    def _compute_phase_locking_degree(self, pre: np.ndarray, 
                                       post: np.ndarray,
                                       freq: float) -> float:
        """Measure phase synchronization before/after injection"""
        # Hilbert transform for instantaneous phase
        analytic_pre = signal.hilbert(pre[:, 1])
        analytic_post = signal.hilbert(post[:, 1])
        
        phase_pre = np.unwrap(np.angle(analytic_pre))
        phase_post = np.unwrap(np.angle(analytic_post))
        
        # Phase coherence (order parameter)
        # High value = phase locked, Low = incoherent
        r_pre = np.abs(np.mean(np.exp(1j * phase_pre)))
        r_post = np.abs(np.mean(np.exp(1j * phase_post)))
        
        return r_post - r_pre
    
    def _test_irreversibility(self, time_series: np.ndarray) -> float:
        """Test for time-reversal symmetry breaking (irreversible remanence)"""
        # Reverse time series
        reversed_ts = time_series[::-1].copy()
        
        # Compare correlation structure
        original_corr = np.corrcoef(time_series[:-1, 1], time_series[1:, 1])[0,1]
        reversed_corr = np.corrcoef(reversed_ts[:-1, 1], reversed_ts[1:, 1])[0,1]
        
        # Asymmetry indicates irreversibility
        return abs(original_corr - reversed_corr)
    
    def _find_peaks(self, power: np.ndarray, threshold: float) -> List[int]:
        """Simple peak detection"""
        peaks = []
        for i in range(1, len(power)-1):
            if power[i] > threshold * np.max(power):
                if power[i] > power[i-1] and power[i] > power[i+1]:
                    peaks.append(i)
        return peaks
    
    def _temporal_autocorrelation(self, signal: np.ndarray) -> np.ndarray:
        """Compute normalized autocorrelation"""
        sig = signal[:, 1] if signal.ndim > 1 else signal
        result = np.correlate(sig - np.mean(sig), sig - np.mean(sig), mode='full')
        result = result[len(result)//2:]
        return result / (result[0] + 1e-10)
    
    def _estimate_decay(self, autocorr: np.ndarray) -> float:
        """Estimate correlation decay time"""
        # Find where autocorr drops below 1/e
        threshold = 1/np.e
        below = np.where(autocorr < threshold)[0]
        return below[0] if len(below) > 0 else len(autocorr)
    
    def _reconstruct_phase_space(self, signal: np.ndarray, 
                                  delay: int = 10, 
                                  dim: int = 3) -> np.ndarray:
        """Takens embedding for phase space reconstruction"""
        sig = signal[:, 1] if signal.ndim > 1 else signal
        N = len(sig) - (dim - 1) * delay
        embedded = np.zeros((N, dim))
        for i in range(dim):
            embedded[:, i] = sig[i*delay : i*delay + N]
        return embedded
    
    def _count_attractors(self, phase_space: np.ndarray) -> int:
        """Simple attractor counting via clustering"""
        from sklearn.cluster import DBSCAN
        if len(phase_space) < 10:
            return 0
        clustering = DBSCAN(eps=0.1, min_samples=5).fit(phase_space)
        return len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)


# ============================================================================
# EXCITON-DARK MATTER ANALOGUE DETECTOR
# ============================================================================

class ExcitonDarkMatterAnalogue:
    """
    Detect Berry curvature and anomalous velocity in dark matter halos
    Treats halos as geometric quasi-particles (exciton analogues)
    """
    
    def __init__(self, halo_mass: float = 1e12,  # Solar masses
                 redshift: float = 0.0):
        self.M = halo_mass
     
