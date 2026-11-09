"""Exact latent-count EM reconstruction for Poisson data with Gaussian read noise.

Observation model per detector pixel:
    Y = K + Normal(0, read_noise_sigma**2)
    K ~ Poisson(exposure * (A x + known_background_rate))

The E-step computes E[K | Y, current mean] from the discrete
Poisson-Gaussian posterior. Conditional Poisson splitting allocates the
expected total count to the source component. The M-step is multiplicative
and uses the exact adjoint of the discrete shift-and-bin operator.

This is a known-background model, not blind background estimation.
"""
from __future__ import annotations

import numpy as np
from scipy.special import gammaln, logsumexp

from research.sandbox.dithered_stack_operator import adjoint_operator, forward_operator


def expected_latent_counts(observations, poisson_mean, read_noise_sigma):
    """Return E[K|Y] under K~Poisson(mean), Y|K~N(K,sigma^2).

    The posterior sum is truncated at a conservative upper bound determined
    by the largest supplied mean and read-noise scale. Log weights avoid
    underflow. The routine accepts negative real-valued observations.
    """
    y = np.asarray(observations, dtype=float)
    mean = np.asarray(poisson_mean, dtype=float)
    if y.shape != mean.shape:
        raise ValueError("observations and poisson_mean must have matching shapes")
    if not np.all(np.isfinite(y)):
        raise ValueError("observations must be finite")
    if not np.all(np.isfinite(mean)) or np.any(mean < 0):
        raise ValueError("poisson_mean must be finite and non-negative")
    if not np.isfinite(read_noise_sigma) or read_noise_sigma <= 0:
        raise ValueError("read_noise_sigma must be finite and positive")

    max_mean = float(np.max(mean)) if mean.size else 0.0
    k_max = int(np.ceil(max_mean + 12.0 * np.sqrt(max_mean + read_noise_sigma**2)
                        + 20.0 + 8.0 * read_noise_sigma))
    if k_max > 2048:
        raise ValueError("Poisson-Gaussian posterior support exceeds safe limit (2048)")
    k = np.arange(k_max + 1, dtype=float)
    flat_mean = mean.ravel()
    flat_y = y.ravel()
    safe_mean = np.maximum(flat_mean, np.finfo(float).tiny)
    log_poisson = (
        k[None, :] * np.log(safe_mean[:, None])
        - safe_mean[:, None]
        - gammaln(k[None, :] + 1.0)
    )
    # At exactly zero Poisson mean, only K=0 has nonzero prior probability.
    zero_rows = flat_mean == 0
    if np.any(zero_rows):
        log_poisson[zero_rows, :] = -np.inf
        log_poisson[zero_rows, 0] = 0.0
    standardized = (flat_y[:, None] - k[None, :]) / read_noise_sigma
    log_gaussian = -0.5 * standardized**2
    log_weights = log_poisson + log_gaussian
    normalizer = logsumexp(log_weights, axis=1, keepdims=True)
    probabilities = np.exp(log_weights - normalizer)
    result = probabilities @ k
    return result.reshape(y.shape)


def poisson_gaussian_em(
    frames, phases_yx, frame_exposures, highres_shape, bin_factor,
    iterations=10, epsilon=1e-12, background_rate=0.0,
    read_noise_sigma=1.0,
):
    """Reconstruct a nonnegative source-rate image with known Poisson background."""
    observations = np.asarray(frames, dtype=float)
    phases = np.asarray(phases_yx, dtype=float)
    exposures = np.asarray(frame_exposures, dtype=float)
    shape = tuple(map(int, highres_shape))
    if observations.ndim != 3 or observations.shape[0] == 0:
        raise ValueError("frames must have shape (n_frames, detector_height, detector_width)")
    if phases.shape != (observations.shape[0], 2):
        raise ValueError("phases_yx must have one (row, column) pair per frame")
    if exposures.shape != (observations.shape[0],) or not np.all(np.isfinite(exposures)) or np.any(exposures <= 0):
        raise ValueError("frame_exposures must contain finite positive exposures")
    if not np.all(np.isfinite(observations)):
        raise ValueError("observations must be finite")
    if not np.all(np.isfinite(phases)):
        raise ValueError("phases must be finite")
    if len(shape) != 2 or min(shape) <= 0 or not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("highres_shape and bin_factor must be positive")
    if shape[0] % bin_factor or shape[1] % bin_factor:
        raise ValueError("high-resolution shape must be divisible by bin_factor")
    detector_shape = (shape[0] // bin_factor, shape[1] // bin_factor)
    if observations.shape[1:] != detector_shape:
        raise ValueError("detector frame dimensions do not match highres_shape and bin_factor")
    if not isinstance(iterations, (int, np.integer)) or iterations < 1:
        raise ValueError("iterations must be a positive integer")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and positive")
    if not np.isfinite(background_rate) or background_rate < 0:
        raise ValueError("background_rate must be finite and non-negative")
    if not np.isfinite(read_noise_sigma) or read_noise_sigma <= 0:
        raise ValueError("read_noise_sigma must be finite and positive")

    sensitivity = np.zeros(shape, dtype=float)
    for phase, exposure in zip(phases, exposures):
        sensitivity += exposure * adjoint_operator(
            np.ones(detector_shape), shape, bin_factor, tuple(phase)
        )
    # A positive initialization is important when some observed pixels are negative.
    total_positive = float(np.maximum(observations, 0.0).sum())
    estimate = np.full(
        shape, max(total_positive, 1.0) / max(float(sensitivity.sum()), epsilon),
        dtype=float,
    )
    safe_sensitivity = np.maximum(sensitivity, epsilon)

    for _ in range(int(iterations)):
        numerator = np.zeros_like(estimate)
        for frame, phase, exposure in zip(observations, phases, exposures):
            source_mean = exposure * forward_operator(estimate, bin_factor, tuple(phase))
            background_mean = exposure * background_rate
            total_mean = source_mean + background_mean
            expected_total = expected_latent_counts(
                frame, total_mean, read_noise_sigma
            )
            expected_source = np.divide(
                source_mean * expected_total,
                np.maximum(total_mean, epsilon),
                out=np.zeros_like(source_mean),
                where=total_mean > 0,
            )
            ratio = np.divide(
                expected_source,
                np.maximum(source_mean, epsilon),
                out=np.zeros_like(source_mean),
                where=source_mean > 0,
            )
            numerator += exposure * adjoint_operator(
                ratio, shape, bin_factor, tuple(phase)
            )
        estimate *= numerator / safe_sensitivity
        estimate = np.maximum(estimate, 0.0)
    return estimate
