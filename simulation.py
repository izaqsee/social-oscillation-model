import os
import argparse
import numpy as np
import matplotlib.pyplot as plt


def make_er_graph(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Undirected Erdos-Renyi adjacency (0/1), no self-loops."""
    A = (rng.random((n, n)) < p).astype(np.float32)
    np.fill_diagonal(A, 0.0)
    A = np.maximum(A, A.T)  # symmetrize
    return A


def simulate(
    n: int,
    steps: int,
    edge_p: float,
    kernel_frac: float,
    seed: int,
    noise_std: float,
    inertia: float,
    gamma: float,
):
    """
    Minimal self-excitation-on-network model.

    State:
        x_i in [-1, 1]

    Individual traits (heterogeneous):
        L_i: damping (verbalization / dissipative tendency)  higher => more stable
        I_i: internalization gain (susceptibility)           higher => more influenced by neighbors
        S_i: saturation threshold                             lower => earlier clipping (more binary-like)

    Kernel agents:
        high I, low L, low S
    """
    rng = np.random.default_rng(seed)

    # Network
    A = make_er_graph(n, edge_p, rng)
    deg = A.sum(axis=1)
    deg = np.maximum(deg, 1.0)  # avoid division by zero

    # Trait distributions (base population)
    L = rng.normal(loc=0.35, scale=0.08, size=n).astype(np.float32)
    I = rng.normal(loc=0.55, scale=0.10, size=n).astype(np.float32)
    S = rng.normal(loc=0.85, scale=0.08, size=n).astype(np.float32)

    # Clamp to sane ranges
    L = np.clip(L, 0.05, 0.80)
    I = np.clip(I, 0.10, 1.20)
    S = np.clip(S, 0.40, 1.00)

    # Kernel agents: high I, low L, low S
    k = int(round(n * kernel_frac))
    if k > 0:
        kernel_idx = rng.choice(n, size=k, replace=False)
        L[kernel_idx] = np.clip(rng.normal(loc=0.18, scale=0.05, size=k), 0.05, 0.40)
        I[kernel_idx] = np.clip(rng.normal(loc=0.95, scale=0.10, size=k), 0.30, 1.20)
        S[kernel_idx] = np.clip(rng.normal(loc=0.60, scale=0.06, size=k), 0.40, 0.85)

    # Initial state
    x = rng.normal(loc=0.0, scale=0.15, size=n).astype(np.float32)
    x = np.clip(x, -1.0, 1.0)

    # Logs
    M = np.zeros(steps, dtype=np.float32)  # order parameter |mean|
    E = np.zeros(steps, dtype=np.float32)  # mean square (energy-like)

    for t in range(steps):
        # Neighbor influence (normalized)
        neigh = (A @ x) / deg

        # Extreme amplification: gamma > 1 emphasizes extremes
        neigh_eff = np.sign(neigh) * (np.abs(neigh) ** gamma)

        # Self-damping
        damp = L * x

        # Noise
        eta = rng.normal(loc=0.0, scale=noise_std, size=n).astype(np.float32)

        # Update + bounding
        u = inertia * x + (1.0 - inertia) * (I * neigh_eff - damp + eta)
        x_next = np.tanh(u)

        # Individual saturation: S-dependent soft clipping
        x_next = np.clip(x_next, -S, S) / S  # keep in [-1,1], lower S => earlier clipping

        x = x_next
        M[t] = np.abs(x.mean())
        E[t] = np.mean(x * x)

    return M, E


def save_timeseries_plot(M: np.ndarray, E: np.ndarray, outdir: str, fname: str = "timeseries.png"):
    os.makedirs(outdir, exist_ok=True)
    plt.figure()
    plt.plot(M, label="M(t)=|mean(x)|")
    plt.plot(E, label="E(t)=mean(x^2)")
    plt.xlabel("time step")
    plt.ylabel("value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, fname), dpi=180)
    plt.close()


def save_sweep_plot(fracs, steady_M, steady_E, outdir: str, fname: str = "sweep_kernel_fraction.png"):
    os.makedirs(outdir, exist_ok=True)
    plt.figure()
    plt.plot(fracs, steady_M, marker="o", label="steady M")
    plt.plot(fracs, steady_E, marker="s", label="steady E")
    plt.xlabel("kernel fraction")
    plt.ylabel("steady-state metric (post-burn-in mean)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, fname), dpi=180)
    plt.close()


def run_single(args):
    M, E = simulate(
        n=args.n,
        steps=args.steps,
        edge_p=args.edge_p,
        kernel_frac=args.kernel_frac,
        seed=args.seed,
        noise_std=args.noise_std,
        inertia=args.inertia,
        gamma=args.gamma,
    )
    save_timeseries_plot(M, E, outdir=args.outdir)
    return M, E


def run_sweep(args):
    fracs = np.linspace(args.sweep_min, args.sweep_max, args.sweep_points)
    steady_M, steady_E = [], []

    for p in fracs:
        M, E = simulate(
            n=args.n,
            steps=args.steps,
            edge_p=args.edge_p,
            kernel_frac=float(p),
            seed=args.seed,  # fixed for comparability
            noise_std=args.noise_std,
            inertia=args.inertia,
            gamma=args.gamma,
        )
        burn = int(len(M) * args.burnin)
        steady_M.append(float(np.mean(M[burn:])))
        steady_E.append(float(np.mean(E[burn:])))

    save_sweep_plot(fracs, steady_M, steady_E, outdir=args.outdir)
    return fracs, steady_M, steady_E


def build_parser():
    p = argparse.ArgumentParser(description="Social Oscillation Model (minimal self-excitation simulation)")
    p.add_argument("--mode", choices=["single", "sweep", "both"], default="both",
                   help="Run a single simulation, a sweep over kernel fraction, or both.")
    p.add_argument("--outdir", type=str, default="out", help="Output directory for figures.")
    p.add_argument("--seed", type=int, default=2, help="Random seed.")
    p.add_argument("--n", type=int, default=800, help="Number of agents.")
    p.add_argument("--steps", type=int, default=600, help="Number of timesteps.")
    p.add_argument("--edge-p", type=float, default=0.02, dest="edge_p",
                   help="Erdos-Renyi edge probability.")
    p.add_argument("--kernel-frac", type=float, default=0.18, dest="kernel_frac",
                   help="Kernel fraction for single run (ignored in sweep).")
    p.add_argument("--noise-std", type=float, default=0.04, dest="noise_std",
                   help="Gaussian noise standard deviation.")
    p.add_argument("--inertia", type=float, default=0.75, help="Inertia term (0..1). Higher => slower response.")
    p.add_argument("--gamma", type=float, default=1.4, help="Extreme amplification exponent (>1 emphasizes extremes).")

    # Sweep options
    p.add_argument("--sweep-min", type=float, default=0.0, dest="sweep_min", help="Min kernel fraction in sweep.")
    p.add_argument("--sweep-max", type=float, default=0.40, dest="sweep_max", help="Max kernel fraction in sweep.")
    p.add_argument("--sweep-points", type=int, default=21, dest="sweep_points",
                   help="Number of sweep points (linspace).")
    p.add_argument("--burnin", type=float, default=0.5,
                   help="Burn-in fraction for steady-state averaging in sweep (0..1).")
    return p


if __name__ == "__main__":
    # 予想される動作:
    # - mode=both の場合、outdir に timeseries.png と sweep_kernel_fraction.png が生成される
    # - seed固定で再現性が確保される（同じ引数なら同じ出力）
    # - kernel fraction を増やすと、定常状態の E が上がりやすく、M も上がりやすい（条件により非単調もあり得る）
    args = build_parser().parse_args()

    if args.mode in ("single", "both"):
        run_single(args)

    if args.mode in ("sweep", "both"):
        run_sweep(args)

    print(f"Done. See ./{args.outdir}/")
