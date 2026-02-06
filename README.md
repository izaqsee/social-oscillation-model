# Social Oscillation Model  
**Emergence of self-excitation in communication-mediated social networks**

This project proposes a minimal computational model to explore how self-excitation and synchronization emerge in text-based communication environments, such as social media.

---

## Core Hypothesis

In large-scale communication-mediated social systems, collective instability is determined not **solely** by network topology or information flow, but also by the **distribution of heterogeneous individual traits** within the population.

Specifically:

- A subset of individuals acts as **self-exciting “kernel” agents**.
- The remainder of the population behaves as **passive or non-self-exciting agents**.
- As the fraction of kernel agents increases, the system undergoes a **regime shift** from a stable state to synchronized, oscillatory, or unstable dynamics.

This suggests that collective polarization or runaway behavior can be interpreted as a **phase-transition-like phenomenon** driven by population composition, rather than being exclusively triggered by external shocks or ideological shifts.

---

## What the model does

The repository contains a minimal agent-based network simulation that:

1. Creates a random interaction network.
2. Assigns a fraction of agents as self-exciting kernels.
3. Simulates time evolution of agent states under mutual influence.
4. Computes key observables:
   - Mean activity (order parameter)
   - System energy (variance-like measure)
5. Sweeps the kernel fraction to observe regime transitions.

---

## Research Intent

The model serves as:

- **A conceptual minimal model**, prioritizing theoretical clarity over high-fidelity social realism.
- **A bridge** between:
  - network science,
  - epidemic-like cascade models,
  - and control-theoretic concepts of self-excitation.
- **A theoretical foundation** for exploring stabilization strategies, such as:
  - intentional decoupling of highly sensitive nodes,
  - low-pass filtering within social feedback loops.

---

## Run

~~~bash
pip install -r requirements.txt
python simulation.py
~~~

---

## Outputs

Outputs are saved in `./out/`:

- `timeseries.png`  
  (time evolution of mean activity and system energy)
- `sweep_kernel_fraction.png`  
  (steady-state metrics vs. kernel fraction)

---

## Companion project

A stabilization proposal based on intentional decoupling / low-pass filtering:

- (planned) `social-lpf` (separate repository)

---

## License

MIT (see LICENSE).

---

## How to cite

See `CITATION.cff` (works with GitHub citation UI).
