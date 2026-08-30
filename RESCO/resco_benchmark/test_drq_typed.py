"""
One-off verification: confirms drq_typed produces sane car/truck/motorcycle
counts before trusting it in an actual training run. Not part of the real
pipeline -- classification_state.py itself is never modified by this file.

Usage (same argument style as run_typed_training.py):
    python test_drq_typed_v2.py "@cologne1_typed" "@FIXED" libsumo:False save_console_log:False episodes:1 trials:1 gui:False
"""
import os
import dynamic_vlen_traffic_signal  # noqa: F401
import resco_benchmark.mdp_options.classification_state as classification_state
import resco_benchmark.mdp_options.states as states_module

from resco_benchmark.config.config import config as cfg
cfg.state = "drq_typed"

# wrap the already-registered drq_typed with a print, without editing
# classification_state.py -- purely for this one-off check
_original = classification_state.drq_typed
_call_count = 0


def _debug_wrapper(signals):
    global _call_count
    result = _original(signals)
    _call_count += 1
    if _call_count % 100 == 0:
        for signal_id, obs in result.items():
            car = obs[0, :, 4].sum()
            truck = obs[0, :, 5].sum()
            moto = obs[0, :, 6].sum()
            print(f"[check] call {_call_count}: car={car:.0f} truck={truck:.0f} motorcycle={moto:.0f}")
    return result


states_module.drq_typed = _debug_wrapper

main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
with open(main_path) as f:
    code = compile(f.read(), main_path, "exec")
exec(code, {"__name__": "__main__", "__file__": main_path})