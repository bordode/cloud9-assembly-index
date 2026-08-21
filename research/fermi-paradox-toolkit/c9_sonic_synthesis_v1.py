#!/usr/bin/env python3
"""
SONIC SYNTHESIS: H/T/D/A Signal Processing Pipeline
Cloud-9 Module: c9_sonic_synthesis_v1.py

Implements the Fermi Void audio architecture:
  H = Cantonese Heartbeat (prosodic envelope)
  T = Taa Click Pivot (onset detection / transient extraction)
  D = Ubykh Vertical Density (multi-band feature stacking)
  A = Aymara Temporal Flip (time-reversal correlation)

Usage:
    python3 c9_sonic_synthesis_v1.py --input noise.wav --output analysis.json
"""

import numpy as np
import json
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from dataclasses import dataclass, asdict
from typing import List, Tuple


@dataclass
class SonicConfig:
    sr: int = 44100              # Sample rate
    h_bpm: float = 72.0          # Heartbeat tempo (Cantonese prosody ~72 BPM)
    h_syllable_ms: float = 280.0 # Average Cantonese syllable duration
    t_threshold: float = 0.85    # Click onset detection threshold (0-1)
    d_bands: int = 8             # Number of frequency bands for density stack
    d_overlap: float = 0.5       # STFT overlap
    a_window_ms: float = 500.0   # Aymara flip correlation window


class CantoneseHeartbeat:
    """Generates / detects prosodic heartbeat envelope."""

    def __init__(self, config: SonicConfig):
        self.config = config
        self.period_samples = int(60.0 / config.h_bpm * config.sr)
        self.syllable_samples = int(config.h_syllable_ms / 1000.0 * config.sr)

    def generate_envelope(self, duration_sec: float) -> np.ndarray:
        """Create a short-long-short-long pulse train."""
        total_samples = int(duration_sec * self.config.sr)
        envelope = np.zeros(total_samples)

        short_dur = int(self.syllable_samples * 0.6)
        long_dur = int(self.syllable_samples * 1.4)
        gap = int(self.syllable_samples * 0.3)

        pattern = [short_dur, gap, long_dur, gap]
        pos = 0
        while pos < total_samples:
            for i, dur in enumerate(pattern):
                if i % 2 == 0 and pos + dur < total_samples:
                    # Even indices = tone (Gaussian pulse)
                    envelope[pos:pos+dur] = np.exp(-0.5 * ((np.arange(dur) - dur//2) / (dur/4))**2)
                pos += dur
        return envelope

    def align_signal(self, audio: np.ndarray) -> np.ndarray:
        """Phase-align input to heartbeat grid via cross-correlation."""
        env = self.generate_envelope(len(audio) / self.config.sr)
        corr = signal.correlate(audio, env, mode='same')
        peak = np.argmax(np.abs(corr))
        shift = peak - len(audio)//2
        return np.roll(audio, shift)


class TaaClickPivot:
    """Detects sharp transient onsets (Taa-style clicks)."""

    def __init__(self, config: SonicConfig):
        self.config = config

    def detect(self, audio: np.ndarray) -> List[int]:
        """Returns sample indices of click pivots."""
        # Spectral flux onset detection
        hop = 512
        n_fft = 2048
        stft = np.abs(signal.stft(audio, nperseg=n_fft, noverlap=n_fft-hop)[2])

        # Spectral flux (difference across frames, only positive)
        flux = np.maximum(0, np.diff(stft, axis=1))
        flux_sum = np.sum(flux, axis=0)

        # Normalize and threshold
        flux_norm = flux_sum / np.max(flux_sum)
        peaks, _ = signal.find_peaks(flux_norm, height=self.config.t_threshold, 
                                     distance=int(0.05 * self.config.sr / hop))
        return [p * hop for p in peaks]

    def extract_pivot_context(self, audio: np.ndarray, pivot_idx: int, 
                              context_ms: float = 50.0) -> np.ndarray:
        """Extract Â±context_ms around pivot for density analysis."""
        half = int(context_ms / 1000.0 * self.config.sr / 2)
        start = max(0, pivot_idx - half)
        end = min(len(audio), pivot_idx + half)
        return audio[start:end]


class UbykhVerticalDensity:
    """Multi-band feature stacking at pivot instants."""

    def __init__(self, config: SonicConfig):
        self.config = config
        # Log-spaced bands (Ubykh has extreme vertical consonant stacking)
        self.bands = np.logspace(2, 4, config.d_bands)  # 100 Hz to 10 kHz

    def stack(self, audio: np.ndarray) -> dict:
        """Compute density vector across all bands."""
        density = {}
        for i, (low, high) in enumerate(zip(self.bands[:-1], self.bands[1:])):
            sos = signal.butter(4, [low, high], btype='band', fs=self.config.sr, output='sos')
            filtered = signal.sosfilt(sos, audio)
            # RMS + crest factor + zero-crossing rate
            rms = np.sqrt(np.mean(filtered**2))
            crest = np.max(np.abs(filtered)) / (rms + 1e-10)
            zcr = np.mean(np.diff(np.sign(filtered)) != 0)
            density[f"band_{i}"] = {"rms": float(rms), "crest": float(crest), "zcr": float(zcr)}
        return density

    def coherence_score(self, density_a: dict, density_b: dict) -> float:
        """Compare two density stacks for non-random coordination."""
        keys = sorted(density_a.keys())
        vec_a = np.array([[density_a[k]["rms"], density_a[k]["crest"]] for k in keys])
        vec_b = np.array([[density_b[k]["rms"], density_b[k]["crest"]] for k in keys])
        # Cosine similarity across bands
        dot = np.sum(vec_a * vec_b, axis=1)
        norm = np.linalg.norm(vec_a, axis=1) * np.linalg.norm(vec_b, axis=1) + 1e-10
        return float(np.mean(dot / norm))


class AymaraTemporalFlip:
    """Time-reversal correlation analysis."""

    def __init__(self, config: SonicConfig):
        self.config = config

    def flip_correlate(self, audio: np.ndarray) -> Tuple[float, np.ndarray]:
        """Compute correlation between signal and its time reversal."""
        reversed_audio = audio[::-1]
        window = int(self.config.a_window_ms / 1000.0 * self.config.sr)

        correlations = []
        for i in range(0, len(audio) - window, window // 2):
            seg = audio[i:i+window]
            rev = reversed_audio[len(audio)-i-window:len(audio)-i]
            if len(seg) == len(rev):
                corr = np.corrcoef(seg, rev)[0, 1]
                correlations.append(0.0 if np.isnan(corr) else corr)

        return float(np.mean(correlations)), np.array(correlations)

    def flip_consistency(self, audio: np.ndarray, pivots: List[int]) -> float:
        """Measure if pivots are symmetrically placed under time flip."""
        if len(pivots) < 2:
            return 0.0
        mid = len(audio) // 2
        left = [p for p in pivots if p < mid]
        right = [p for p in pivots if p >= mid]
        # Map right-side pivots to flipped coordinates
        flipped_right = [len(audio) - p for p in right]
        # Compare distributions
        hist_l, _ = np.histogram(left, bins=10, range=(0, mid))
        hist_r, _ = np.histogram(flipped_right, bins=10, range=(0, mid))
        # Jensen-Shannon similarity
        p = hist_l / (np.sum(hist_l) + 1e-10)
        q = hist_r / (np.sum(hist_r) + 1e-10)
        m = 0.5 * (p + q)
        kl_pm = np.sum(p * np.log((p + 1e-10) / (m + 1e-10)))
        kl_qm = np.sum(q * np.log((q + 1e-10) / (m + 1e-10)))
        js = 0.5 * (kl_pm + kl_qm)
        return float(1.0 / (1.0 + js))


class FermiVoidAnalyzer:
    """Main pipeline: H â T â D â A."""

    def __init__(self, config: SonicConfig = None):
        self.config = config or SonicConfig()
        self.H = CantoneseHeartbeat(self.config)
        self.T = TaaClickPivot(self.config)
        self.D = UbykhVerticalDensity(self.config)
        self.A = AymaraTemporalFlip(self.config)

    def analyze(self, audio: np.ndarray) -> dict:
        """Run full H/T/D/A pipeline."""
        # Step 1: H â Align to heartbeat
        aligned = self.H.align_signal(audio)

        # Step 2: T â Detect click pivots
        pivots = self.T.detect(aligned)

        # Step 3: D â Stack density at each pivot
        density_stacks = []
        for p in pivots[:20]:  # Limit to first 20 for performance
            ctx = self.T.extract_pivot_context(aligned, p)
            stack = self.D.stack(ctx)
            density_stacks.append({"pivot_sample": int(p), "density": stack})

        # Compute pairwise coherence
        coherence_matrix = np.zeros((len(density_stacks), len(density_stacks)))
        for i in range(len(density_stacks)):
            for j in range(i+1, len(density_stacks)):
                score = self.D.coherence_score(
                    density_stacks[i]["density"], 
                    density_stacks[j]["density"]
                )
                coherence_matrix[i, j] = score
                coherence_matrix[j, i] = score

        # Step 4: A â Temporal flip analysis
        flip_corr, flip_series = self.A.flip_correlate(aligned)
        flip_consistency = self.A.flip_consistency(aligned, pivots)

        return {
            "config": asdict(self.config),
            "heartbeat_period_samples": self.H.period_samples,
            "num_pivots": len(pivots),
            "pivot_samples": pivots[:20],
            "density_stacks": density_stacks,
            "mean_coherence": float(np.mean(coherence_matrix[coherence_matrix > 0])) if np.any(coherence_matrix > 0) else 0.0,
            "flip_correlation": flip_corr,
            "flip_consistency": flip_consistency,
            "fermi_score": self._compute_fermi_score(len(pivots), 
                                                      np.mean(coherence_matrix[coherence_matrix > 0]) if np.any(coherence_matrix > 0) else 0.0,
                                                      flip_corr, 
                                                      flip_consistency)
        }

    def _compute_fermi_score(self, n_pivots: int, coherence: float, 
                             flip_corr: float, flip_cons: float) -> float:
        """Composite anomaly score (0-1)."""
        # Normalize: more pivots = higher score (up to saturation)
        pivot_score = min(n_pivots / 50.0, 1.0)
        # High coherence across pivots = non-random
        # Flip correlation near 0.5 is most interesting (neither random nor perfectly symmetric)
        flip_interest = 1.0 - abs(flip_corr - 0.5) * 2.0
        # Flip consistency measures structural symmetry
        return float(0.3 * pivot_score + 0.3 * coherence + 0.2 * flip_interest + 0.2 * flip_cons)


# --- DEMO: Generate synthetic "void" and analyze ---
if __name__ == "__main__":
    np.random.seed(42)
    sr = 44100
    duration = 10.0  # seconds

    # Synthetic void: pink noise + sparse synthetic "message" pulses
    noise = np.random.randn(int(duration * sr))
    # Pink-ify
    freqs = np.fft.rfftfreq(len(noise), 1/sr)
    fft = np.fft.rfft(noise)
    pink_filter = 1.0 / np.sqrt(freqs[1:] + 1e-10)
    fft[1:] *= pink_filter
    void = np.fft.irfft(fft, n=len(noise))
    void = void / np.max(np.abs(void)) * 0.3

    # Inject sparse structured pulses (simulated "Final Warning" fragments)
    pulse_times = [2.1, 4.3, 6.5, 8.2]
    for t in pulse_times:
        idx = int(t * sr)
        if idx + 1000 < len(void):
            void[idx:idx+1000] += np.sin(2*np.pi*880*np.arange(1000)/sr) * np.exp(-np.arange(1000)/200) * 0.5

    analyzer = FermiVoidAnalyzer()
    result = analyzer.analyze(void)

    print("=" * 60)
    print("FERMI VOID SONIC ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Detected pivots (T): {result['num_pivots']}")
    print(f"Mean density coherence (D): {result['mean_coherence']:.4f}")
    print(f"Flip correlation (A): {result['flip_correlation']:.4f}")
    print(f"Flip consistency (A): {result['flip_consistency']:.4f}")
    print(f"Composite FERMI SCORE: {result['fermi_score']:.4f}")
    print("=" * 60)

    with open("sonic_analysis_demo.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Saved: sonic_analysis_demo.json")
