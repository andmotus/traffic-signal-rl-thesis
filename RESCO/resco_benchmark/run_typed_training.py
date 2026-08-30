"""
Thin wrapper around RESCO's main.py that applies the vehicle-length patch
(dynamic_vlen_traffic_signal.py) before training starts.

main.py and traffic_signal.py are never touched -- this file is the only
thing that's different. Usage is identical to main.py, just call this
instead:

    python run_typed_training.py "@cologne1_typed" "@MAXPRESSURE" libsumo:False save_console_log:False gui:False
"""
import os
import dynamic_vlen_traffic_signal  # noqa: F401  (import applies the patch as a side effect)

main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
with open(main_path) as f:
    code = compile(f.read(), main_path, "exec")
exec(code, {"__name__": "__main__", "__file__": main_path})