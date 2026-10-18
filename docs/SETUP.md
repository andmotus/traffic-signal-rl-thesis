# Setup

All experiments of the thesis ran on Windows with Python 3.12 and SUMO 1.27.1, installed as a Python package. The package versions are pinned in `requirements.txt` and need Python 3.12; numpy 1.26.4 has no package for Python 3.13.

If you only want to regenerate the tables and figures from the committed run logs, you need neither SUMO nor PyTorch. See [Analysis only](#analysis-only).

## Install

Windows (PowerShell):

```powershell
git clone https://github.com/andmotus/traffic-signal-rl-thesis.git
cd traffic-signal-rl-thesis
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SUMO_HOME = (python -c "import sumo, os; print(os.path.dirname(sumo.__file__))")
```

If activation fails with "running scripts is disabled on this system", run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.

Linux / macOS:

```bash
git clone https://github.com/andmotus/traffic-signal-rl-thesis.git
cd traffic-signal-rl-thesis
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export SUMO_HOME="$(python -c 'import sumo, os; print(os.path.dirname(sumo.__file__))')"
```

Run `pip install -r requirements.txt` from the repository root. It installs RESCO from `./RESCO` in editable mode, which makes `import resco_benchmark` work in the wrapper scripts.

**Paths of the typed scenarios.** The two typed presets in `RESCO/resco_benchmark/config/config.yaml`, `cologne1_typed` and `ingolstadt1_typed`, contain absolute paths of the machine the experiments ran on (`C:\dev\Activation_Lab\…`). To rerun a typed experiment elsewhere, replace these four paths with the absolute paths of the same files in your clone.

## Check the installation

```bash
sumo --version
sumo -c RESCO/resco_benchmark/environments/cologne1/cologne1_typed.sumocfg --no-step-log true --duration-log.statistics true
```

The second command runs one hour of the typed Cologne1 demand in plain SUMO. Its statistics summary includes `Inserted: 2013 (Loaded: 2015)`.

## Running the experiments

- Always run from `RESCO/resco_benchmark/`. RESCO's configuration changes into the parent folder if the working directory is anything else.
- Use the wrappers instead of `main.py`:
  - `run_typed_training.py` for standard-state IDQN and the baselines
  - `run_classification_training.py` with `state:drq_typed` for the classification-aware state
  - `run_emissions_tracking.py` for the CO₂ runs
- All runs used `libsumo:False save_console_log:False gui:False`. The `.ps1` scripts contain the exact command lines of every experiment.
- Results are written to `RESCO/results/<log_dir>/`: one JSON file per run with all per-episode metrics, and one folder per run with its `config.json`.
- A run of 200 episodes took about 50 minutes on Cologne1 and 30 minutes on Ingolstadt1.
- RESCO has no seed control, so a rerun is a new independent draw.

## Analysis only

```bash
pip install -r analysis/requirements.txt
python analysis/run_all.py
```

This needs only NumPy, SciPy, statsmodels, Matplotlib and openpyxl, and works with Python 3.12 or 3.13. See [analysis/README.md](../analysis/README.md).
