#!/usr/bin/env python3
"""Independent replication study: pixel-integrated super-resolution (debinning).

Experiments
  E1  blind-lambda criteria (whiteness, L-curve, GCV) vs oracle, single frame
  E2  dithering: single vs 9-frame stack (full data) vs 9-frame stack (matched total noise)
  E3  vanishing point: noise level where fit stops beating bilinear; is sigma*b constant?

Usage:  python superres_study.py [--quick] [--seeds 3] [--out .]
Everything is seeded; results.json holds all per-cell numbers.
"""
import argparse, json, time, platform
import numpy as np, scipy
from scipy.sparse.linalg import LinearOperator, cg
from scipy.ndimage import zoom

N = 72                                   # divisible by 2, 3, 4
LAMS = np.logspace(-6, 0, 13)            # half-decade grid
SCENES = ["nebula", "stars", "mixed"]

# ---------------- scenes (synthetic, fixed seeds) ----------------
def _norm(x):
    x = x - x.min(); return x / x.max()

def _nebula(rng):
    f = np.fft.fftfreq(N); k = np.hypot(*np.meshgrid(f, f)); k[0, 0] = 1
    return _norm(np.fft.ifft2(np.fft.fft2(rng.standard_normal((N, N))) * k ** -1.5).real)

def _stars(rng, n=25, fwhm=1.3):
    yy, xx = np.mgrid[:N, :N]; s = fwhm / 2.355; img = np.zeros((N, N))
    for _ in range(n):
        cy, cx = rng.uniform(0, N, 2); fl = rng.lognormal(0, 0.8)
        d2 = (yy - cy) ** 2 + (xx - cx) ** 2
        img += fl * np.exp(-d2 / (2 * s * s))
    return img

def scene(name):
    rng = np.random.default_rng(100 + SCENES.index(name))
    if name == "nebula": return _nebula(rng)
    if name == "stars":  return _norm(_stars(rng) + 0.02)
    return _norm(0.7 * _nebula(rng) + 0.3 * _norm(_stars(rng)))

# ---------------- operators ----------------
def bin_(x, b, s=(0, 0)):
    if s != (0, 0): x = np.roll(x, s, axis=(0, 1))
    return x.reshape(N // b, b, N // b, b).mean((1, 3))

def binT(z, b, s=(0, 0)):
    u = np.repeat(np.repeat(z, b, 0), b, 1) / b ** 2
    if s != (0, 0): u = np.roll(u, (-s[0], -s[1]), axis=(0, 1))
    return u

def lap(x):
    return 4 * x - np.roll(x, 1, 0) - np.roll(x, -1, 0) - np.roll(x, 1, 1) - np.roll(x, -1, 1)

def _cg(M, rhs, x0=None):
    try:  x, _ = cg(M, rhs, x0=x0, rtol=1e-6, maxiter=600)
    except TypeError: x, _ = cg(M, rhs, x0=x0, tol=1e-6, maxiter=600)
    return x

def white(res):
    sc = 0.0
    for r in res:
        r = r - r.mean(); v = (r * r).mean() + 1e-30
        for d in ((0, 1), (1, 0), (1, 1), (1, -1)):
            c = (r * np.roll(r, d, (0, 1))).mean() / v; sc += c * c
    return sc / len(res)

def lcurve_pick(rn, pen):
    t = np.log(LAMS); x = np.log(rn); y = np.log(pen + 1e-12)
    x1, y1 = np.gradient(x, t), np.gradient(y, t)
    x2, y2 = np.gradient(x1, t), np.gradient(y1, t)
    k = (x1 * y2 - y1 * x2) / (x1 ** 2 + y1 ** 2 + 1e-30) ** 1.5
    k[0] = k[-1] = -np.inf
    return int(np.argmax(k))

def sweep(x, b, shifts, ys, crit=True, probes=2, seed=0):
    """Fit over the lambda grid; objective (1/K) sum||y_k-A_k x||^2 + lam ||Lap x||^2."""
    K = len(shifts); m = N // b
    rhs = sum(binT(y, b, s) for y, s in zip(ys, shifts)) / K
    def mk(lam):
        def mv(v):
            X = v.reshape(N, N)
            out = sum(binT(bin_(X, b, s), b, s) for s in shifts) / K + lam * lap(lap(X)) + 1e-10 * X
            return out.ravel()
        return LinearOperator((N * N, N * N), matvec=mv, dtype=float)
    rng = np.random.default_rng(seed)
    Z = [[rng.choice([-1.0, 1.0], (m, m)) for _ in shifts] for _ in range(probes)] if crit else []
    rm, wh, gc, rn, pen = [], [], [], [], []
    x0 = None
    for lam in LAMS:
        M = mk(lam); xh = _cg(M, rhs.ravel(), x0).reshape(N, N); x0 = xh.ravel()
        rm.append(np.sqrt(np.mean((xh - x) ** 2)))
        if not crit: continue
        res = [y - bin_(xh, b, s) for y, s in zip(ys, shifts)]
        r2 = sum((r ** 2).sum() for r in res)
        rn.append(np.sqrt(r2 / (K * m * m))); pen.append(np.linalg.norm(lap(xh)))
        wh.append(white(res))
        tr = 0.0
        for z in Z:
            w = sum(binT(zk, b, s) for zk, s in zip(z, shifts))
            u = _cg(M, w.ravel()).reshape(N, N)
            tr += sum((zk * bin_(u, b, s)).sum() for zk, s in zip(z, shifts)) / K
        tr /= probes; mt = K * m * m
        gc.append(mt * r2 / (mt - tr) ** 2)
    rm = np.array(rm)
    if not crit: return dict(rmse=rm)
    picks = dict(whiteness=int(np.argmin(wh)), lcurve=lcurve_pick(np.array(rn), np.array(pen)),
                 gcv=int(np.argmin(gc)))
    o = int(np.argmin(rm))
    return dict(rmse=rm, oracle=o, picks=picks,
                cost={k: float(rm[v] / rm[o] - 1) for k, v in picks.items()},
                basin_decades=float(0.5 * np.sum(rm <= 1.02 * rm[o])))

def rng_for(*a):
    return np.random.default_rng([int(v) for v in a])

def shifts_all(b): return [(i, j) for i in range(b) for j in range(b)]

# ---------------- experiments ----------------
def E1(seeds, log):
    cells = []
    for si, sc in enumerate(SCENES):
        x = scene(sc)
        for b in (2, 3, 4):
            for sg in (0.02, 0.05):
                for sd in range(seeds):
                    rng = rng_for(1, si, b, sg * 1e4, sd)
                    ys = [bin_(x, b) + sg / b * rng.standard_normal((N // b, N // b))]
                    r = sweep(x, b, [(0, 0)], ys, seed=sd)
                    cells.append(dict(scene=sc, b=b, sigma=sg, seed=sd,
                                      oracle_lam=float(LAMS[r["oracle"]]),
                                      picked_lam={k: float(LAMS[v]) for k, v in r["picks"].items()},
                                      cost=r["cost"], basin_decades=r["basin_decades"]))
        log(f"E1 {sc} done")
    return cells

def E2(seeds, log):
    cells = []; b = 3; sh = shifts_all(b); K = len(sh)
    for si, sc in enumerate(SCENES):
        x = scene(sc)
        for sg in (0.02, 0.05):
            for sd in range(seeds):
                for mode in ("single", "dither_full", "dither_matched"):
                    rng = rng_for(2, si, b, sg * 1e4, sd)
                    if mode == "single": S, f = [(0, 0)], 1.0
                    else: S, f = sh, (1.0 if mode == "dither_full" else np.sqrt(K))
                    ys = [bin_(x, b, s) + f * sg / b * rng.standard_normal((N // b, N // b)) for s in S]
                    r = sweep(x, b, S, ys, seed=sd)
                    cells.append(dict(scene=sc, sigma=sg, seed=sd, mode=mode,
                                      oracle_rmse=float(r["rmse"][r["oracle"]]),
                                      oracle_lam=float(LAMS[r["oracle"]]),
                                      cost=r["cost"], basin_decades=r["basin_decades"]))
        log(f"E2 {sc} done")
    return cells

SIGS = [0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08]
def E3(seeds, log):
    cells = []
    for si, sc in enumerate(SCENES):
        x = scene(sc)
        for b in (2, 3, 4):
            gains = []
            for sg in SIGS:
                g = []
                for sd in range(seeds):
                    rng = rng_for(3, si, b, sg * 1e4, sd)
                    y = bin_(x, b) + sg / b * rng.standard_normal((N // b, N // b))
                    bil = zoom(y, b, order=1, grid_mode=True, mode="grid-wrap")
                    rb = np.sqrt(np.mean((bil - x) ** 2))
                    rf = sweep(x, b, [(0, 0)], [y], crit=False)["rmse"].min()
                    g.append((rb - rf) / rb)
                gains.append(float(np.mean(g)))
            cross = None
            for i in range(1, len(SIGS)):
                if gains[i - 1] > 0 >= gains[i]:
                    cross = SIGS[i - 1] + (SIGS[i] - SIGS[i - 1]) * gains[i - 1] / (gains[i - 1] - gains[i]); break
            cells.append(dict(scene=sc, b=b, sigmas=SIGS, gain=gains, sigma_star=cross,
                              sigma_star_times_b=(cross * b if cross else None)))
        log(f"E3 {sc} done")
    return cells

# ---------------- summaries / tables ----------------
def pool(cells, keys, pred=lambda c: True):
    out = {}
    for c in cells:
        if not pred(c): continue
        for k in keys: out.setdefault(k, []).append(c["cost"][k])
    return {k: (100 * np.mean(v), 100 * np.max(v)) for k, v in out.items()}

CR = ["whiteness", "lcurve", "gcv"]
def tables(R):
    L = []
    L += ["### E1 - blind-lambda cost over oracle (%, mean / worst), single frame", "",
          "| scene | sigma | whiteness | L-curve | GCV |", "|---|---|---|---|---|"]
    for sc in SCENES:
        for sg in (0.02, 0.05):
            p = pool(R["E1"], CR, lambda c: c["scene"] == sc and c["sigma"] == sg)
            L.append(f"| {sc} | {sg} | " + " | ".join(f"{p[k][0]:.1f} / {p[k][1]:.1f}" for k in CR) + " |")
    bd = np.mean([c["basin_decades"] for c in R["E1"]])
    L += ["", f"Mean width of the RMSE basin (within 2% of optimum): **{bd:.1f} decades** (grid step 0.5).", "",
          "### E2 - dithering at b=3 (cost over oracle, %, mean / worst; oracle RMSE in last column)", "",
          "| mode | whiteness | L-curve | GCV | mean oracle RMSE |", "|---|---|---|---|---|"]
    for md in ("single", "dither_full", "dither_matched"):
        sel = [c for c in R["E2"] if c["mode"] == md]
        p = pool(sel, CR)
        L.append(f"| {md} | " + " | ".join(f"{p[k][0]:.1f} / {p[k][1]:.1f}" for k in CR)
                 + f" | {np.mean([c['oracle_rmse'] for c in sel]):.4f} |")
    L += ["", "### E3 - vanishing point (first downward zero-crossing of gain over bilinear)", "",
          "| scene | b | sigma* | sigma* x b | gain at sigma=0.08 |", "|---|---|---|---|---|"]
    for c in R["E3"]:
        s = "none in range" if c["sigma_star"] is None else f"{c['sigma_star']:.3f}"
        sb = "-" if c["sigma_star"] is None else f"{c['sigma_star_times_b']:.3f}"
        L.append(f"| {c['scene']} | {c['b']} | {s} | {sb} | {100*c['gain'][-1]:+.1f}% |")
    return "\n".join(L)

def figures(R, out):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    for a, sc in zip(ax, SCENES):
        for c in [c for c in R["E3"] if c["scene"] == sc]:
            a.plot(c["sigmas"], 100 * np.array(c["gain"]), "o-", label=f"b={c['b']}")
        a.axhline(0, color="k", lw=.6); a.set_title(sc); a.set_xlabel("sensor noise sigma")
    ax[0].set_ylabel("fit gain over bilinear (%)"); ax[0].legend()
    fig.tight_layout(); fig.savefig(f"{out}/figures/vanishing_point.png", dpi=130); plt.close(fig)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    for a, sg in zip(ax, (0.02, 0.05)):
        for j, md in enumerate(("single", "dither_full", "dither_matched")):
            sel = [c for c in R["E2"] if c["mode"] == md and c["sigma"] == sg]
            p = pool(sel, CR)
            a.bar(np.arange(3) + 0.27 * j, [p[k][0] for k in CR], 0.27, label=md)
        a.set_xticks(np.arange(3) + 0.27); a.set_xticklabels(CR); a.set_title(f"sigma={sg}")
    ax[0].set_ylabel("mean cost over oracle (%)"); ax[0].legend()
    fig.tight_layout(); fig.savefig(f"{out}/figures/blind_lambda_dither.png", dpi=130); plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true"); ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--out", default="."); a = ap.parse_args()
    seeds = 1 if a.quick else a.seeds
    t0 = time.time()
    log = lambda s: print(f"[{time.time()-t0:6.0f}s] {s}", flush=True)
    R = dict(meta=dict(N=N, lams=LAMS.tolist(), seeds=seeds, scenes=SCENES, numpy=np.__version__,
                       scipy=scipy.__version__, python=platform.python_version(),
                       noise_model="sensor-pixel sigma; binned noise = sigma/b",
                       dither="all b*b integer fine-pixel phases; matched = per-frame noise x sqrt(K)"))
    R["E1"] = E1(seeds, log); R["E2"] = E2(seeds, log); R["E3"] = E3(max(seeds - 1, 1), log)
    R["meta"]["runtime_s"] = time.time() - t0
    json.dump(R, open(f"{a.out}/results.json", "w"), indent=1)
    open(f"{a.out}/tables.md", "w").write(tables(R)); figures(R, a.out)
    log("done")

if __name__ == "__main__":
    main()
