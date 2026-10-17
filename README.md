# Vehicle-Type-Aware RL for Traffic Signal Control

MSc thesis project — Lukas Müller | Sustainability, Innovation and Technology

Extends the [RESCO](https://github.com/Pi-Star-Lab/RESCO) benchmark (Cologne & Ingolstadt
networks) with vehicle-classification-aware state representation, and estimates the
national CO₂-reduction potential for Germany from the resulting findings.

## Structure
- `RESCO/` — benchmark framework (git submodule, unmodified)
- `src/` — classification wrapper, training scripts, analysis
- `analysis/` — scripts that regenerate every table, figure and number of the thesis from the run logs (see `analysis/README.md`)
- `docs/` — proposal, setup notes

## Setup
See `docs/SETUP.md`.