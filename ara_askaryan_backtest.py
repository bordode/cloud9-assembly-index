#!/usr/bin/env python3
"""
ARA Askaryan Backtest - Complete Termux-compatible version
Cloud-9 Terrestrial Validation Case #2 (C9-2026-ARA-001)

This version avoids SciPy so it can run in Termux environments where
scipy extension modules fail to import.
"""

import math
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# Statistical replacements
# -----------------------------
def _log_comb(n, k):
    if k < 0 or k > n:
        return float('-inf')
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def binom_sf(k, n, p):
    """Survival function P(X > k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 1.0
    if k >= n:
        return 0.0
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0 if k < n else 0.0

    terms = []
    for x in range(k + 1, n + 1):
        logpmf = _log_comb(n, x) + x * math.log(p) + (n - x) * math.log(1 - p)
        terms.append(logpmf)
    m = max(terms)
    return float(math.exp(m) * sum(math.exp(t - m) for t in terms))


def norm_ppf(p):
    """Inverse CDF for standard normal using Acklam approximation."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("p must be in (0,1)")

    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]

    plow = 0.02425
    phigh = 1 - plow

    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def norm_isf(p):
    """Inverse survival function for standard normal."""
    return norm_ppf(1 - p)


# -----------------------------
# Configuration
# -----------------------------
N_SIGNALS = 13
N_BACKGROUNDS = 2000
RNG_SEED = 42
OUTPUT_DIR = Path("output_ara")
OUTPUT_DIR.mkdir(exist_ok=True)


# -----------------------------
# Event model
# -----------------------------
@dataclass
class ARAEvent:
    event_id: int
    is_signal: int
    zenith_deg: float
    depth_m: float
    arrival_azimuth_deg: float
    true_azimuth_deg: float
    freqs_hz: np.ndarray
    spectrum: np.ndarray
    time_s: np.ndarray
    waveform: np.ndarray
    pol_vec: np.ndarray
    sys_tag: str


# -----------------------------
# Mock data generator
# -----------------------------
class ARAMockDataGenerator:
    def __init__(self, rng_seed=RNG_SEED):
        self.rng = np.random.default_rng(rng_seed)

    def _askaryan_waveform(self, n_samples=256):
        t = np.linspace(-4e-9, 4e-9, n_samples)
        sigma = 0.8e-9
        pulse = np.exp(-0.5 * (t / sigma) ** 2) * np.sign(t)
        noise = self.rng.normal(0, 0.08, size=n_samples)
        return t, pulse + noise

    def _radar_waveform(self, n_samples=256):
        t = np.linspace(0, 1e-6, n_samples)
        f_c = self.rng.uniform(5e6, 40e6)
        tone = np.sin(2 * np.pi * f_c * t)
        envelope = 0.7 + 0.3 * np.sin(2 * np.pi * self.rng.uniform(0.5e6, 2e6) * t)
        noise = self.rng.normal(0, 0.2, size=n_samples)
        return t, envelope * tone + noise

    def _comms_waveform(self, n_samples=256):
        t = np.linspace(0, 2e-6, n_samples)
        f1 = self.rng.uniform(100e6, 150e6)
        f2 = f1 + self.rng.uniform(1e6, 5e6)
        tone = np.sin(2 * np.pi * f1 * t) + 0.6 * np.sin(2 * np.pi * f2 * t + 0.7)
        noise = self.rng.normal(0, 0.15, size=n_samples)
        return t, tone + noise

    def _thermal_waveform(self, n_samples=256):
        t = np.linspace(0, 1e-6, n_samples)
        noise = self.rng.normal(0, 1.0, size=n_samples)
        return t, noise

    def _compute_spectrum(self, waveform, dt):
        n = len(waveform)
        freqs = np.fft.rfftfreq(n, dt)
        spec = np.abs(np.fft.rfft(waveform))
        return freqs, spec

    def generate_events(self, n_signals=N_SIGNALS, n_bkg=N_BACKGROUNDS):
        events = []
        eid = 0

        for _ in range(n_signals):
            zenith = float(self.rng.uniform(0, 45))
            depth = float(self.rng.uniform(50, 200))
            true_az = float(self.rng.uniform(0, 360))
            reco_az = float(true_az + self.rng.normal(0, 3))
            t, wf = self._askaryan_waveform()
            dt = float(t[1] - t[0])
            freqs, spec = self._compute_spectrum(wf, dt)
            pol = np.array([
                self.rng.normal(0, 0.1) + 0.9,
                self.rng.normal(0, 0.1) + 0.1,
                self.rng.normal(0, 0.1)
            ])
            pol /= np.linalg.norm(pol) + 1e-9
            events.append(ARAEvent(
                event_id=eid,
                is_signal=1,
                zenith_deg=zenith,
                depth_m=depth,
                arrival_azimuth_deg=reco_az,
                true_azimuth_deg=true_az,
                freqs_hz=freqs,
                spectrum=spec,
                time_s=t,
                waveform=wf,
                pol_vec=pol,
                sys_tag="signal"
            ))
            eid += 1

        sys_tags = ["radar", "comms", "thermal"]
        for _ in range(n_bkg):
            tag = self.rng.choice(sys_tags, p=[0.3, 0.3, 0.4])
            zenith = float(self.rng.uniform(30, 90))
            depth = float(self.rng.uniform(-10, 10))
            true_az = float(self.rng.uniform(0, 360))
            reco_az = float(true_az + self.rng.normal(0, 15))

            if tag == "radar":
                t, wf = self._radar_waveform()
            elif tag == "comms":
                t, wf = self._comms_waveform()
            else:
                t, wf = self._thermal_waveform()

            dt = float(t[1] - t[0])
            freqs, spec = self._compute_spectrum(wf, dt)

            if tag == "thermal":
                pol = self.rng.normal(0, 1.0, size=3)
            else:
                pol = np.array([1.0, 0.0, 0.0]) + self.rng.normal(0, 0.5, size=3)
            pol /= np.linalg.norm(pol) + 1e-9

            events.append(ARAEvent(
                event_id=eid,
                is_signal=0,
                zenith_deg=zenith,
                depth_m=depth,
                arrival_azimuth_deg=reco_az,
                true_azimuth_deg=true_az,
                freqs_hz=freqs,
                spectrum=spec,
                time_s=t,
                waveform=wf,
                pol_vec=pol,
                sys_tag=str(tag)
            ))
            eid += 1

        return events


# -----------------------------
# Veto engine
# -----------------------------
class VetoEngine:
    def __init__(self, zenith_max_signal=60.0, depth_min_signal=20.0):
        self.zenith_max_signal = zenith_max_signal
        self.depth_min_signal = depth_min_signal

    def geometric_veto(self, event):
        return (event.zenith_deg <= self.zenith_max_signal) and (event.depth_m >= self.depth_min_signal)

    def systematic_score(self, event):
        freqs = event.freqs_hz
        spec = event.spectrum
        total = np.sum(spec) + 1e-9

        def band_power(lo, hi):
            mask = (freqs >= lo) & (freqs <= hi)
            return float(np.sum(spec[mask]) / total)

        p_radar = band_power(5e6, 60e6)
        p_comms = band_power(80e6, 200e6)

        wf = event.waveform
        ac = np.correlate(wf, wf, mode="full")
        ac = ac[ac.size // 2:]
        ac_norm = ac / (np.max(np.abs(ac)) + 1e-9)
        peak2 = float(np.max(ac_norm[1:])) if len(ac_norm) > 1 else 0.0

        tag_penalty = 0.3 if event.sys_tag in ("radar", "comms") else 0.0
        score = 0.5 * p_radar + 0.5 * p_comms + 0.4 * max(0.0, peak2) + tag_penalty
        return float(np.clip(score, 0.0, 1.0))


# -----------------------------
# Domain scoring
# -----------------------------
class DomainScorer:
    def topo_score(self, event):
        dphi = abs(event.arrival_azimuth_deg - event.true_azimuth_deg)
        dphi = min(dphi, 360.0 - dphi)
        return float(np.exp(-0.5 * (dphi / 10.0) ** 2))

    def quant_score(self, event):
        freqs = event.freqs_hz
        spec = event.spectrum + 1e-12
        p = spec / np.sum(spec)
        f0 = 80e6
        sigma_f = 25e6
        template = np.exp(-0.5 * ((freqs - f0) / sigma_f) ** 2) + 1e-12
        q = template / np.sum(template)
        kl = float(np.sum(p * np.log(p / q)))
        return float(np.clip(1.0 / (1.0 + kl), 0.0, 1.0))

    def iit_score(self, event):
        wf = event.waveform
        if len(wf) < 4:
            return 0.5
        wf_z = (wf - np.mean(wf)) / (np.std(wf) + 1e-9)
        ar1 = np.corrcoef(wf_z[:-1], wf_z[1:])[0, 1]
        ar2 = np.corrcoef(wf_z[:-2], wf_z[2:])[0, 1]
        ar = 0.7 * ar1 + 0.3 * ar2
        ar = float(np.clip(ar, -0.99, 0.99))
        return float(np.clip((ar + 1.0) / 2.0, 0.0, 1.0))

    def red_score(self, event):
        cov = np.outer(event.pol_vec, event.pol_vec)
        eigvals = np.linalg.eigvalsh(cov)
        eigvals = np.sort(np.abs(eigvals))
        ratio = float(eigvals[-1] / (np.sum(eigvals) + 1e-9))
        return float(np.clip(ratio, 0.0, 1.0))


# -----------------------------
# Fusion
# -----------------------------
class AssemblyIndexFusion:
    def __init__(self, w_topo=1.0, w_quant=1.1, w_iit=1.2, w_red=0.9, base=2.0, span=0.8):
        self.weights = np.array([w_topo, w_quant, w_iit, w_red], dtype=float)
        self.base = base
        self.span = span
        self.w_sum = float(np.sum(self.weights))

    def fuse(self, scores):
        s = np.clip(np.array(scores, dtype=float), 1e-6, 1.0)
        gmean = float(np.exp(np.sum(self.weights * np.log(s)) / self.w_sum))
        return float(self.base + self.span * gmean)


# -----------------------------
# Pipeline
# -----------------------------
class ARADetectionPipeline:
    def __init__(self):
        self.gen = ARAMockDataGenerator()
        self.veto = VetoEngine()
        self.dom = DomainScorer()
        self.fuse = AssemblyIndexFusion()

    def run(self):
        events = self.gen.generate_events()
        rows = []
        for ev in events:
            geo_pass = self.veto.geometric_veto(ev)
            a_sys = self.veto.systematic_score(ev)
            a_topo = self.dom.topo_score(ev)
            a_quant = self.dom.quant_score(ev)
            a_iit = self.dom.iit_score(ev)
            a_red = self.dom.red_score(ev)
            a_c = self.fuse.fuse([a_topo, a_quant, a_iit, a_red])
            rows.append({
                "event_id": ev.event_id,
                "is_signal": ev.is_signal,
                "sys_tag": ev.sys_tag,
                "zenith_deg": ev.zenith_deg,
                "depth_m": ev.depth_m,
                "geo_pass": int(geo_pass),
                "A_topo": a_topo,
                "A_quant": a_quant,
                "A_iit": a_iit,
                "A_red": a_red,
                "A_c": a_c,
                "A_sys": a_sys,
            })
        return pd.DataFrame(rows)

    @staticmethod
    def significance_scan(df, thresholds):
        results = []
        for thr in thresholds:
            mask_sel = (df["geo_pass"] == 1) & (df["A_c"] > thr) & (df["A_sys"] < 0.4)
            sel = df[mask_sel]
            n_sig = int(sel["is_signal"].sum())
            n_bkg = int(len(sel) - n_sig)
            n_bkg_tot = int(((df["is_signal"] == 0) & (df["geo_pass"] == 1)).sum())
            p_bkg = (n_bkg / n_bkg_tot) if n_bkg_tot > 0 else 0.0
            p_bkg = max(p_bkg, 1e-12)
            total_sel = n_sig + n_bkg
            p_val = binom_sf(n_sig - 1, total_sel, p_bkg) if total_sel > 0 else 1.0
            p_val = min(max(p_val, 1e-300), 1 - 1e-16)
            sigma = float(norm_isf(p_val / 2.0))
            results.append({
                "threshold": thr,
                "n_sig": n_sig,
                "n_bkg": n_bkg,
                "p_val": p_val,
                "sigma": sigma,
            })
        return pd.DataFrame(results)


# -----------------------------
# Diagnostics
# -----------------------------
def plot_diagnostics(df, scan_df, fname):
    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    ax = axes.ravel()

    bins = np.linspace(df["A_c"].min(), df["A_c"].max(), 40)
    df[df["is_signal"] == 1]["A_c"].plot.hist(bins=bins, alpha=0.7, label="signal", ax=ax[0])
    df[df["is_signal"] == 0]["A_c"].plot.hist(bins=bins, alpha=0.7, label="background", ax=ax[0])
    ax[0].set_xlabel("A_c")
    ax[0].set_title("Assembly index distribution")
    ax[0].legend()

    for label, mask, color in [("signal", df["is_signal"] == 1, "C0"), ("background", df["is_signal"] == 0, "C1")]:
        ax[1].scatter(df.loc[mask, "A_c"], df.loc[mask, "A_sys"], s=10, alpha=0.5, label=label, c=color)
    ax[1].axhline(0.4, color="k", ls="--", lw=1)
    ax[1].set_xlabel("A_c")
    ax[1].set_ylabel("A_sys")
    ax[1].set_title("Systematic veto plane")
    ax[1].legend()

    domains = ["A_topo", "A_quant", "A_iit", "A_red"]
    means = np.array([
        df.loc[df["is_signal"] == 1, domains].mean().values,
        df.loc[df["is_signal"] == 0, domains].mean().values,
    ])
    im = ax[2].imshow(means, aspect="auto", cmap="viridis")
    ax[2].set_xticks(range(len(domains)))
    ax[2].set_xticklabels(domains, rotation=45)
    ax[2].set_yticks([0, 1])
    ax[2].set_yticklabels(["signal", "background"])
    ax[2].set_title("Domain score means")
    fig.colorbar(im, ax=ax[2], fraction=0.046, pad=0.04)

    thr_grid = np.linspace(df["A_c"].min(), df["A_c"].max(), 50)
    tpr_list, fpr_list = [], []
    for thr in thr_grid:
        m_sel = (df["geo_pass"] == 1) & (df["A_c"] > thr) & (df["A_sys"] < 0.4)
        sel = df[m_sel]
        tp = int(sel["is_signal"].sum())
        fp = int(len(sel) - tp)
        p_total = int((df["is_signal"] == 1).sum())
        n_total = int((df["is_signal"] == 0).sum())
        tpr_list.append(tp / p_total if p_total > 0 else 0.0)
        fpr_list.append(fp / n_total if n_total > 0 else 0.0)
    ax[3].plot(fpr_list, tpr_list, marker="o", ms=3)
    ax[3].set_xlabel("FPR")
    ax[3].set_ylabel("TPR")
    ax[3].set_title("Operating curve")

    ax[4].plot(scan_df["threshold"], scan_df["sigma"], marker="o")
    ax[4].axhline(5.1, color="r", ls="--", label=r"5.1$\sigma$")
    ax[4].set_xlabel("A_c threshold")
    ax[4].set_ylabel(r"Discovery Significance ($\sigma$)")
    ax[4].set_title("Significance scan")
    ax[4].legend()

    sc = ax[5].scatter(df["zenith_deg"], df["depth_m"], c=df["A_c"], cmap="plasma", s=8)
    ax[5].invert_yaxis()
    ax[5].set_xlabel("Zenith (deg)")
    ax[5].set_ylabel("Depth (m)")
    ax[5].set_title("Geometry vs assembly index")
    fig.colorbar(sc, ax=ax[5], fraction=0.046, pad=0.04)

    fig.tight_layout()
    fig.savefig(fname, dpi=200)
    plt.close(fig)


# -----------------------------
# Main
# -----------------------------
def main():
    pipe = ARADetectionPipeline()
    df = pipe.run()
    df.to_pickle(OUTPUT_DIR / "ara_backtest_results.pkl")

    thresholds = np.linspace(2.0, 2.6, 13)
    scan_df = pipe.significance_scan(df, thresholds)
    scan_df.to_csv(OUTPUT_DIR / "ara_backtest_scan.csv", index=False)

    sel = (df["geo_pass"] == 1) & (df["A_c"] > 2.2) & (df["A_sys"] < 0.4)
    df_sel = df[sel]
    summary = {
        "N_signals_injected": int(df["is_signal"].sum()),
        "N_background_injected": int((df["is_signal"] == 0).sum()),
        "N_signals_recovered": int(df_sel["is_signal"].sum()),
        "N_background_leakage": int(len(df_sel) - df_sel["is_signal"].sum()),
        "A_c_min_signal": float(df[df["is_signal"] == 1]["A_c"].min()),
        "A_c_max_signal": float(df[df["is_signal"] == 1]["A_c"].max()),
        "operating_threshold": 2.2,
    }
    with open(OUTPUT_DIR / "ara_backtest_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    plot_diagnostics(df, scan_df, OUTPUT_DIR / "ara_backtest_diagnostics.png")
    print("Done. Outputs written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
