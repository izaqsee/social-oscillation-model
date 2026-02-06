# Social Oscillation Model (Text-mediated self-excitation)

A minimal network simulation of self-excitation and synchronization in text-based communication environments.
The model focuses on **heterogeneity** in individual traits:

- **L**: verbalization / damping (emotion labeling, cognitive reappraisal capacity)
- **I**: internalization gain (susceptibility to others' text)
- **S**: saturation threshold (nonlinear clipping)

## Core idea (hypothesis)
In text-heavy environments, collective instability is governed not only by network connectivity but also by the **distribution** of individual traits.
A small fraction of "oscillation-kernel" agents (high I, low L, low S) can push the system across a critical region where
global polarization/synchrony rapidly increases.

## Model (high level)
Agents hold a signed state x_i ∈ [-1, 1] (e.g., affective conviction).
At each step, agents update based on:
- inertia (persistence)
- network input (neighbors' states)
- self-damping (verbalization)
- bounded nonlinearity (tanh + saturation-like effects)
- noise

## What this repo provides
- `simulation.py`: minimal simulation + plot outputs
- One key experiment: sweep the fraction of "kernel" agents and observe an order parameter.

## Expected behavior (predictions)
- Increasing kernel fraction increases global synchrony/polarization.
- A sharp rise (phase-transition-like) may appear depending on network density and nonlinearity.
- Adding stronger damping (higher L) or weaker coupling (lower connectivity) shifts the critical region rightward.

## Run
```bash
pip install -r requirements.txt
python simulation.py

## Outputs
Outputs are saved in ./out/:

timeseries.png (M(t), E(t))

sweep_kernel_fraction.png (kernel fraction vs steady-state order parameter)

## Companion project

A stabilization proposal based on intentional decoupling / low-pass filtering:

(planned) social-lpf (separate repository)

## License

MIT (see LICENSE).

## How to cite

See CITATION.cff (works with GitHub citation UI).