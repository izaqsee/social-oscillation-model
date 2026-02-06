# Social Oscillation Model (Text-mediated self-excitation)

A minimal network simulation of self-excitation and synchronization in text-based communication environments.

## Core idea (hypothesis)
In text-heavy environments, collective instability is governed not only by network connectivity but also by the **distribution** of individual traits.

## Run

~~~bash
pip install -r requirements.txt
python simulation.py
~~~

## Outputs
Outputs are saved in `./out/`:

- `timeseries.png` (M(t), E(t))
- `sweep_kernel_fraction.png` (kernel fraction vs steady-state order parameter)

## Companion project
A stabilization proposal based on intentional decoupling / low-pass filtering:

- (planned) `social-lpf` (separate repository)

## License
MIT (see LICENSE).

## How to cite
See `CITATION.cff` (works with GitHub citation UI).
