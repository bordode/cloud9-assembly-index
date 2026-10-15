"""Cloud-9 SSBM demonstration utilities.

This module generates and analyses a synthetic narrowband signal. It is a
software demonstration only: it does not establish an astronomical detection,
validate the Assembly Index as a physical measure, or provide a calibrated
statistical significance for a real technosignature.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import numpy as np
from scipy import signal


class StellarType(str, Enum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"
    L = "L"
    T = "T"


class ScatteringModel(str, Enum):
    GAUSSIAN = "gaussian"
    THIN_SCREEN = "thin_screen"


@dataclass
class StellarParameters:
    stellar_type: StellarType = StellarType.G
    mass: float = 1.0
    radius: float = 1.0
    luminosity: float = 1.0
    rotation_period: float = 25.0
    activity_index: float = -4.9
    distance: float = 10.0


@dataclass
class ObservationConfig:
    frequency_start: float = 1.420e9
    frequency_end: float = 1.421e9
    frequency_resolution: float = 10.0
    integration_time: float = 100.0
    system_temperature: float = 20.0
    antenna_gain: float = 1.0

    @property
    def frequencies(self) -> np.ndarray:
        if self.frequency_resolution <= 0 or self.frequency_end <= self.frequency_start:
            raise ValueError("Frequency bounds and resolution must define a positive grid.")
        return np.arange(
            self.frequency_start,
            self.frequency_end,
            self.frequency_resolution,
            dtype=float,
        )


class StellarBroadeningKernel:
    """Simple normalized smoothing kernel for synthetic demonstrations."""

    def __init__(self, stellar_params: StellarParameters):
        self.stellar_params = stellar_params

    def apply_broadening(self, spectrum: np.ndarray, frequencies: np.ndarray) -> np.ndarray:
        if spectrum.ndim != 1 or frequencies.ndim != 1 or len(spectrum) != len(frequencies):
            raise ValueError("Spectrum and frequencies must be one-dimensional arrays of equal length.")
        if len(frequencies) < 3:
            return spectrum.copy()
        step = float(np.median(np.diff(frequencies)))
        sigma_hz = max(step, step * (1.0 + abs(self.stellar_params.activity_index)))
        half_width = max(2, min(50, int(np.ceil(4.0 * sigma_hz / step))))
        offsets = np.arange(-half_width, half_width + 1) * step
        kernel = np.exp(-0.5 * (offsets / sigma_hz) ** 2)
        kernel /= kernel.sum()
        return signal.convolve(spectrum, kernel, mode="same")


class SignalSimulator:
    """Create reproducible synthetic narrowband signals with optional noise."""

    def __init__(self, random_seed: Optional[int] = None):
        self.rng = np.random.default_rng(random_seed)

    def generate_narrowband(
        self,
        frequencies: np.ndarray,
        center_freq: float,
        power: float = 1.0,
        width_hz: float = 1.0,
    ) -> np.ndarray:
        if frequencies.ndim != 1 or len(frequencies) == 0:
            raise ValueError("frequencies must be a non-empty one-dimensional array.")
        if power < 0 or width_hz <= 0:
            raise ValueError("power must be non-negative and width_hz must be positive.")
        spectrum = power * np.exp(-0.5 * ((frequencies - center_freq) / width_hz) ** 2)
        for harmonic in (1, 2):
            for direction in (-1, 1):
                sideband = center_freq + direction * harmonic * width_hz * 10
                if frequencies.min() < sideband < frequencies.max():
                    spectrum += 0.15 * power * np.exp(
                        -0.5 * ((frequencies - sideband) / width_hz) ** 2
                    )
        return spectrum

    def generate_broadened_scenario(
        self,
        config: ObservationConfig,
        stellar: StellarParameters,
    ) -> tuple[np.ndarray, Dict[str, Any]]:
        frequencies = config.frequencies
        if len(frequencies) < 3:
            raise ValueError("Observation grid must contain at least three frequency channels.")
        center = float(np.median(frequencies))
        raw = self.generate_narrowband(frequencies, center, power=1.0, width_hz=max(
            config.frequency_resolution, 0.5
        ))
        broadened = StellarBroadeningKernel(stellar).apply_broadening(raw, frequencies)
        noise_std = max(config.system_temperature * 0.05, 1e-12)
        noisy = broadened + self.rng.normal(0.0, noise_std, size=len(frequencies))
        return noisy, {
            "data_kind": "synthetic",
            "stellar_type": stellar.stellar_type.value,
            "noise_std": noise_std,
            "center_frequency_hz": center,
        }


class ComplexityAnalyzer:
    """Descriptive signal metrics; these are not a validated physical Assembly Index."""

    @staticmethod
    def analyze(spectrum: np.ndarray) -> Dict[str, float]:
        values = np.asarray(spectrum, dtype=float)
        if values.ndim != 1 or len(values) < 2 or not np.all(np.isfinite(values)):
            raise ValueError("spectrum must be a finite one-dimensional array with at least two samples.")
        power = np.abs(values)
        total = float(power.sum())
        if total == 0:
            return {"normalized_entropy": 0.0, "concentration_proxy": 0.0}
        probabilities = power / total
        entropy = -float(np.sum(probabilities * np.log2(probabilities + 1e-15)))
        max_entropy = float(np.log2(len(probabilities)))
        normalized_entropy = entropy / max_entropy if max_entropy else 0.0
        return {
            "normalized_entropy": normalized_entropy,
            "concentration_proxy": 1.0 - normalized_entropy,
        }


class WidthAwareSETIPipeline:
    """Basic synthetic-data detector; not a calibrated scientific search pipeline."""

    def __init__(self, snr_threshold: float = 5.0):
        if snr_threshold <= 0:
            raise ValueError("snr_threshold must be positive.")
        self.snr_threshold = snr_threshold
        self.complexity_analyzer = ComplexityAnalyzer()

    def detect(
        self,
        spectrum: np.ndarray,
        frequencies: np.ndarray,
        stellar_params: Optional[StellarParameters] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        values = np.asarray(spectrum, dtype=float)
        freqs = np.asarray(frequencies, dtype=float)
        if values.ndim != 1 or freqs.ndim != 1 or len(values) != len(freqs) or len(values) < 3:
            raise ValueError("spectrum and frequencies must be equal-length 1-D arrays with at least 3 samples.")
        if not np.all(np.isfinite(values)) or not np.all(np.isfinite(freqs)):
            raise ValueError("spectrum and frequencies must contain only finite values.")
        noise = values - np.median(values)
        noise_rms = 1.4826 * float(np.median(np.abs(noise)))
        peak_idx = int(np.argmax(values))
        snr = float((values[peak_idx] - np.median(values)) / max(noise_rms, 1e-12))
        metrics = self.complexity_analyzer.analyze(values)
        return {
            "detected": bool(snr >= self.snr_threshold),
            "snr_estimate": snr,
            "snr_threshold": self.snr_threshold,
            "best_frequency_hz": float(freqs[peak_idx]),
            "noise_rms_estimate": noise_rms,
            "complexity_metrics": metrics,
            "data_kind": (metadata or {}).get("data_kind", "unspecified"),
            "stellar_type": stellar_params.stellar_type.value if stellar_params else "Unknown",
            "interpretation": "Synthetic/demo result only; not evidence of an extraterrestrial signal.",
        }


def run_production_test() -> Dict[str, Any]:
    """Run a deterministic smoke test on generated synthetic data."""
    config = ObservationConfig()
    star = StellarParameters()
    simulator = SignalSimulator(random_seed=42)
    spectrum, metadata = simulator.generate_broadened_scenario(config, star)
    result = WidthAwareSETIPipeline().detect(spectrum, config.frequencies, star, metadata)
    result["smoke_test"] = "completed"
    return result


if __name__ == "__main__":
    print(run_production_test())
