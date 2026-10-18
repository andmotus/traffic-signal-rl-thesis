# Vehicle-Type-Aware Reinforcement Learning for Traffic Signal Control

Code, data and run logs of the MSc thesis by Lukas Müller (Sustainability, Innovation and Technology, 2026).

The thesis extends the [RESCO](https://github.com/Pi-Star-Lab/RESCO) benchmark (Ault & Sharon, 2021) in four ways:

- It adds a vehicle-type mix (cars, trucks, motorcycles) to the Cologne1 and Ingolstadt1 scenarios, calibrated to the registered vehicle stock of both cities.
- It compares independent DQN with RESCO's standard state against a classification-aware state, in 21 training runs per condition.
- It measures the CO₂ effect of learned control by vehicle class.
- It scales that effect to a national estimate for German cities above 100,000 inhabitants.

In short:

- Learned control cuts the average delay per vehicle by about 40% against fixed-time control on both networks.
- The classification-aware state brings no significant further gain.
- The national estimate ranges from about 16,000 to 525,000 t CO₂ per year.

## Repository layout

```
analysis/                 scripts that regenerate every table, figure and number of the thesis
docs/                     setup guide, OpenStreetMap queries, input data (KBA, Destatis, Stadt Köln)
notebooks/                development notebooks
scripts/                  vehicle-type injection and registration of the typed scenarios in RESCO
RESCO/                    RESCO benchmark, copied at commit f1ed9a1, with the thesis extensions
  resco_benchmark/
    environments/
      cologne1/cologne1_typed.rou.xml         typed Cologne1 demand (+ cologne1_typed.sumocfg)
      ingolstadt1/ingolstadt1_typed.rou.xml   typed Ingolstadt1 demand (+ ingolstadt1_typed.sumocfg)
    mdp_options/
      classification_state.py      classification-aware state drq_typed (Arm B)
    dynamic_vlen_traffic_signal.py vehicle-length correction (has no effect on the states used; see its docstring)
    emissions_tracking.py          SUMO emissions device for the CO₂ validation runs
    run_typed_training.py          wrapper for Arm A and the baselines
    run_classification_training.py wrapper for Arm B
    run_emissions_tracking.py      wrapper for the CO₂ runs
    run_*.ps1                      the exact commands of every experiment
    run_*_log.txt                  console output of those scripts
    test_drq_typed.py              one-off check of the drq_typed counts
    extract_co2.py                 quick CO₂ total for a single run
  results/                run logs of all experiments
requirements.txt          exact environment used for the runs
```

All extensions are separate modules that patch RESCO at import time. RESCO's `main.py` runs unchanged inside the wrappers. The typed files for `cologne8` and `ingolstadt21` were generated as well but are not used in the thesis.

## Quick start

To regenerate all results from the committed run logs (no simulation, a few seconds):

```bash
pip install -r analysis/requirements.txt
python analysis/run_all.py
```

`analysis/README.md` lists which script reproduces which table and figure. To install the full environment or rerun the experiments, see [docs/SETUP.md](docs/SETUP.md).

## Experiments

All commands run from `RESCO/resco_benchmark/`. Each `.ps1` script lists the exact command lines.

| Experiment | Script | Results | Thesis |
|---|---|---|---|
| Development runs, 100 episodes | `run_dynamic_vlen_typed.ps1`, `run_classification.ps1` | `RESCO/results/*.json` | Section 4.1, Appendices A and B |
| Development runs, 200 episodes; these are also the first run of each condition below | `run_ingolstadt_200.ps1` (Ingolstadt1; there is no script for the Cologne1 runs) | `RESCO/results/*.json` | Appendix B |
| First multi-seed round, 6 runs per condition | `run_multiseed.ps1` (5 more per condition) | `RESCO/results/multiseed/` | Section 4.3 |
| Final sample, 21 runs per condition | `run_21seeds_all.ps1` (15 more per condition) | `RESCO/results/multiseed21/`, which also contains all runs of `multiseed/` | Sections 4.2 and 4.3 |
| CO₂ validation | `run_emissions.ps1` | `RESCO/results/emissions/` | Section 4.5 |

`run_typed.ps1` holds the first typed runs with RESCO's `main.py`, from before the wrappers existed; their result files are not in the repository.

RESCO has no seed control, so every rerun is a new independent draw and individual numbers will differ.

## Changes to RESCO

`RESCO/` is a copy of [Pi-Star-Lab/RESCO](https://github.com/Pi-Star-Lab/RESCO) at commit `f1ed9a1` (version 2.0), licensed under GPLv3. Compared with that commit:

- **Modified (2026):**
  - `resco_benchmark/config/config.yaml` and `resco_benchmark/config/signal.yaml`: one block each for `cologne1_typed` and `ingolstadt1_typed`. The signal block is an exact copy of the original scenario's.
  - `.gitignore`: `results*` removed, so that run logs are versioned.
- **Added:**
  - the typed route and `.sumocfg` files in the scenario folders
  - the modules and wrappers listed above, and the `.ps1` scripts with their logs
  - `results/`

All other files are identical to the original commit, which `git diff` against `f1ed9a1` shows.

## Data and licences

- **Code:** GPLv3 ([LICENSE](LICENSE)), the licence of RESCO.
- **Scenario data:** the Cologne and Ingolstadt scenario folders each contain their licence. The Cologne scenarios (TAPASCologne) are under CC BY-NC-SA 3.0, the Ingolstadt scenarios (InTAS) under GPLv3. The typed route files are derived from them and carry the same licences; they reassign vehicle types only (thesis, Section 3.2).
- **`docs/fz1_2024.xlsx`:** Kraftfahrt-Bundesamt, FZ 1, vehicle stock on 1 January 2024. Datenlizenz Deutschland – Namensnennung – Version 2.0. The sheet "Thesis" and the column "Kategorie Truck" were added for the thesis.
- **`docs/06-staedte-einwohner-groessen.xlsx`:** Statistisches Bundesamt, cities by size class on 31 December 2024. Reproduction permitted with source attribution.
- **`docs/lsaknoten_20241031.csv`:** Stadt Köln, *Ampelanlagen Köln* (offenedaten-koeln.de), inventory of 964 signalised intersections.
- **`docs/osm_traffic_signals.md`:** OpenStreetMap queries of 30 August 2026; data © OpenStreetMap contributors, ODbL.

## Citation

If you use this code, please cite RESCO:

> Ault, J., & Sharon, G. (2021). Reinforcement learning benchmarks for traffic signal control. *35th Conference on Neural Information Processing Systems (NeurIPS 2021) Track on Datasets and Benchmarks*.
