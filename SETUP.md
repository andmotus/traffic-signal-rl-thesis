## Software needed on local machine

*SUMO 1.27.1*
"Simulation of Urban MObility" (SUMO) is an open source, highly portable, microscopic traffic simulation package designed to handle large road networks and different modes of transport. It is mainly developed by employees of the Institute of Transportation Systems at the German Aerospace Center.
[Repository](https://github.com/eclipse-sumo/sumo)
[Download](https://sumo.dlr.de/docs/Downloads.php)


# Environment Setup

## Prerequisites
- Python 3.10+
- Git

## Setup (Windows / PowerShell)

```powershell
# Clone this repo and enter it
git clone <your-repo-url>
cd <your-repo-name>

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\Activate.ps1
```

> If activation fails with a "running scripts is disabled" error, run once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

```powershell
# Install SUMO + Python bindings
pip install eclipse-sumo traci sumolib libsumo
pip freeze > requirements.txt

# Auto-set SUMO_HOME on every future venv activation
Add-Content -Path venv\Scripts\Activate.ps1 -Value '$env:SUMO_HOME = (python -c "import sumo, os; print(os.path.dirname(sumo.__file__))")'

# Clone the RESCO benchmark (Cologne / Ingolstadt scenarios included)
git clone https://github.com/Pi-Star-Lab/RESCO.git
```

## Verify installation

```powershell
sumo --version
cd RESCO\resco_benchmark\environments\cologne1
sumo -c cologne1.sumocfg --duration-log.statistics
```

Expected output ends with a statistics summary (`WaitingTime: 29.94`, `Inserted: 2014`, ...) — confirms SUMO, the RESCO scenario files, and the environment are all working end-to-end.

## Notes
- `SUMO_HOME` is set automatically whenever `venv\Scripts\Activate.ps1` runs; it is **not** cleared by `deactivate`.
- Add `venv/` to `.gitignore`; commit `requirements.txt` instead so the environment is reproducible from a clean clone.
- RESCO's RL dependencies (PyTorch, PFRL, gym) aren't installed yet — add those when training starts.