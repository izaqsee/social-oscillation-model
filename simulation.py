import os
import numpy as np
import matplotlib.pyplot as plt


def make_er_graph(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Undirected Erdos-Renyi adjacency (0/1), no self-loops."""
    A = (rng.random((n, n)) < p).astype(np.float32)
    np.fill_diagonal(A, 0.0)
    # symmetrize
    A = np.maximum(A, A.T)
    return A


def simulate(
    n: int = 800,
    steps: int = 600,
    edge_p: float = 0.02,
    kernel_frac: float = 0.15,
    seed: int = 0,
    noise_std: float = 0.04,
    inertia: float = 0.75,
):
    """
    Minimal self-excitation-on-network model.

    State:
        x_i in [-1, 1]

    Individual traits (distributed):
        L_i: damping (verbalization capacity)  higher => more stable
        I_i: internalization gain             higher => more susceptible
        S_i: saturation threshold             lower => clips earlier (more distortion / binary-like)
    """
    rng = np.random.default_rng(seed)

    # Network
    A = make_er_graph(n, edge_p, rng)
    deg = A.sum(axis=1)
    deg = np.maximum(deg, 1.0)  # avoid division by zero

    # --- Trait distributions (base population) ---
    # L: damping; I: susceptibility; S: saturation threshold
    L = rng.normal(loc=0.35, scale=0.08, size=n).astype(np.float32)
    I = rng.normal(loc=0.55, scale=0.10, size=n).astype(np.float32)
    S = rng.normal(loc=0.85, scale=0.08, size=n).astype(np.float32)

    # clamp to sane ranges
    L = np.clip(L, 0.05, 0.80)
    I = np.clip(I, 0.10, 1.20)
    S = np.clip(S, 0.40, 1.00)

    # --- Kernel agents: high I, low L, low S ---
    k = int(round(n * kernel_frac))
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

        # "Text amplification" nonlinearity: extreme states are more influential
        # gamma > 1 emphasizes extremes
        gamma = 1.4
        neigh_eff = np.sign(neigh) * (np.abs(neigh) ** gamma)

        # Self-damping: proportional to own state magnitude
        damp = L * x

        # Noise
        eta = rng.normal(loc=0.0, scale=noise_std, size=n).astype(np.float32)

        # Update (bounded by tanh + individual saturation S)
        u = inertia * x + (1.0 - inertia) * (I * neigh_eff - damp + eta)
        x_next = np.tanh(u)

        # Individual saturation: soft clip by threshold S (lower S => earlier clipping)
        # Map tanh output through a second nonlinearity
        x_next = np.clip(x_next, -S, S) / S  # keep in [-1,1] but with S-dependent steepening

        x = x_next

        M[t] = np.abs(x.mean())
        E[t] = np.mean(x * x)

    return M, E


def run_sweep(outdir: str):
    os.makedirs(outdir, exist_ok=True)

    # --- Single run (timeseries) ---
    M, E = simulate(kernel_frac=0.18, seed=1)
    plt.figure()
    plt.plot(M, label="M(t)=|mean(x)|")
    plt.plot(E, label="E(t)=mean(x^2)")
    plt.xlabel("time step")
    plt.ylabel("value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "timeseries.png"), dpi=180)
    plt.close()

    # --- Sweep kernel fraction ---
    fracs = np.linspace(0.0, 0.40, 21)
    steady_M = []
    steady_E = []

    for p in fracs:
        M, E = simulate(kernel_frac=float(p), seed=2)
        burn = int(len(M) * 0.5)
        steady_M.append(float(np.mean(M[burn:])))
        steady_E.append(float(np.mean(E[burn:])))

    plt.figure()
    plt.plot(fracs, steady_M, marker="o", label="steady M")
    plt.plot(fracs, steady_E, marker="s", label="steady E")
    plt.xlabel("kernel fraction")
    plt.ylabel("steady-state metric (post-burn-in mean)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "sweep_kernel_fraction.png"), dpi=180)
    plt.close()


if __name__ == "__main__":
    # 予想される動作:
    # - ./out/ に timeseries.png と sweep_kernel_fraction.png が生成される
    # - kernel fraction を増やすと、定常状態の M や E が上がりやすい（同期・一極化の増加）
    # - ネットワーク密度(edge_p)やノイズで立ち上がり方は変わる
    run_sweep(outdir="out")
    print("Done. See ./out/")
