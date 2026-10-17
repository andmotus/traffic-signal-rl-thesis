# Analysis

These scripts regenerate every table, figure and reported number in Chapters 3 and 4 and in the appendices of the thesis. They read the run logs committed in `RESCO/results/` and the official statistics in `docs/`. Nothing is copied by hand, and no simulation needs to be rerun.

## Running

```bash
pip install -r analysis/requirements.txt
python analysis/run_all.py
```

The full run takes a few seconds and needs neither SUMO nor PyTorch. It writes:

- `analysis/output/RESULTS.md`: all tables and numbers, formatted as in the thesis
- `analysis/output/tables/*.csv`: the same tables at full precision
- `analysis/output/figures/*.png`: the figures at 300 dpi

Each script can also be run on its own, for example `python analysis/h2_state_comparison.py`.

## What each script reproduces

| Thesis | Script | Output |
|---|---|---|
| Table 4.1, injection check (Section 4.1) | `h1_learned_vs_fixed.py` | `table_4_1_benchmark.csv` |
| Table 4.2, spread of converged delays, Max-Pressure on Ingolstadt1 (Section 4.2) | `h1_learned_vs_fixed.py` | `table_4_2_h1.csv` |
| Figure 4.1, Figure 4.2 | `h1_learned_vs_fixed.py` | `Figure_4_1_learning_curves.png`, `Figure_4_2_h1_delay.png` |
| Table 4.3, six-run test, minimum detectable effects (Section 4.3) | `h2_state_comparison.py` | `table_4_3_h2.csv`, `power_simulation.csv` |
| Figure 4.3 | `h2_state_comparison.py` | `Figure_4_3_h2_reward_delay.png` |
| Table 4.4, representativeness of the CO₂ runs (Section 4.5) | `h4_co2_national.py` | `table_4_4_co2_by_class.csv` |
| Table 3.4, Table 4.5 and the sensitivities of Section 4.5 | `h4_co2_national.py` | `table_3_4_inputs.csv`, `table_4_5_national.csv` |
| Figure 4.4, Figure 4.5 | `h4_co2_national.py` | `Figure_4_4_co2_by_class.png`, `Figure_4_5_h4_national.png` |
| Figure 3.2, Table A.1, Table B.1, development runs (Appendix B) | `appendix.py` | `Figure_3_2_instability.png`, `table_a_1_maxpressure.csv`, `table_b_1_severe_episodes.csv` |

`common.py` holds the shared loading, statistics and formatting code.

## Data used

| Folder | Content |
|---|---|
| `RESCO/results/multiseed21/` | 84 training runs, 21 per network and state, 200 episodes each (H1, H2, Figure 3.2, Table B.1) |
| `RESCO/results/multiseed/` | the first six runs per condition, a subset of `multiseed21/` (six-run test) |
| `RESCO/results/emissions/` | the four CO₂ validation runs, including the tripinfo file of each final episode (Fixed-Time reference for H1, H4) |
| `RESCO/results/*.json` | single development runs (Section 4.1, Appendices A and B) |
| `docs/fz1_2024.xlsx` | KBA FZ 1, vehicle stock on 1 January 2024 by registration district, sheet FZ1.1 |
| `docs/06-staedte-einwohner-groessen.xlsx` | Destatis, cities by size class on 31 December 2024 |
| `docs/lsaknoten_20241031.csv` | Stadt Köln, inventory of signalised intersections (964 rows) |

Some inputs are not files in the repository. They are constants at the top of `h4_co2_national.py` and `h1_learned_vs_fixed.py`, each with its source:

- the published RESCO delays (Ault & Sharon, 2021, Table 1)
- the OpenStreetMap node counts for Cologne (3,568) and Ingolstadt (558). The Overpass query that produced them is not yet in the repository.
- the fixed-time pool, adoption and peak-hour equivalents of Table 3.4
- German transport-sector emissions in 2025, 146.3 million t CO₂-equivalent (Umweltbundesamt, 2026)
- the plain-SUMO Fixed-Time measurement on Cologne1 (175.7 g per vehicle), used only as a plausibility check

## Definitions

- **Converged performance:** the median of the final 20 logged episodes of a run. RESCO logs one value fewer than the number of training episodes, so for a 200-episode run these are the last 20 of 199 logged values.
- **H1 reference:** the 100 episodes of the Fixed-Time validation run on the same network, against the 21 converged medians of the standard-state runs.
- **Tests:** two-sided Mann–Whitney U, with Holm correction across the two networks for each metric. The rank-biserial correlation is r = 2U/(n₁n₂) − 1, where U belongs to the first-named sample (IDQN in Table 4.2, B in Table 4.3). Positive r means that sample tends to have higher values.
- **Shift:** Hodges–Lehmann estimate of B − A, with a 95% percentile bootstrap interval from 5,000 resamples of both groups.
- **Power simulation:** the standard-state sample is resampled twice, 21 runs each. A constant shift is added to one resample, and Mann–Whitney is tested at α = 0.025, the Holm threshold. The minimum detectable effect is the smallest shift that gives at least 80% significant results in 1,500 such pairs.
- **CO₂ classes:** the InTAS buses on Ingolstadt1 count as trucks, matching the KBA definition used for the injection (buses, lorries and tractors).
- **Kreisfreie cities:** KBA registration districts whose name ends in ",STADT", plus Berlin and Hamburg. This rule misses Freiburg im Breisgau, which KBA lists as "FREIBURG I.BREISG.STADT". `h4_co2_national.py` reports the effect of including it as a sensitivity.

All resampling uses `numpy.random.default_rng(0)`, so every number is reproducible exactly; the CSV tables were checked to be identical with Python 3.12 / numpy 1.26 and Python 3.13 / numpy 2.5 (the PNG files differ at pixel level between matplotlib versions). The bootstrap intervals and minimum detectable effects are Monte Carlo estimates: a different seed moves them in the last reported digit.

The notebooks in `notebooks/` are the exploratory notebooks from the development phase. The reported results come from the scripts in this folder.
