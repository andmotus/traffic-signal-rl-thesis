"""
Run wrapper for H4's CO2 validation runs. Usage identical to main.py:

    python run_emissions_tracking.py "@cologne1_typed" "@FIXED" libsumo:False save_console_log:False gui:False episodes:5
"""
import os
import emissions_tracking  # noqa: F401

main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
with open(main_path) as f:
    code = compile(f.read(), main_path, "exec")
exec(code, {"__name__": "__main__", "__file__": main_path})