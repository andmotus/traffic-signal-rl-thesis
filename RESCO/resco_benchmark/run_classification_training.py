"""
Run wrapper for classification-aware (Arm B) training. Applies both patches
before main.py runs:
  - dynamic_vlen_traffic_signal.py (correct vehicle length/gap, same as Arm A)
  - mdp_options/classification_state.py (registers drq_typed)

Which state function actually gets used is controlled the same way as every
other setting -- via command-line override, not hardcoded here:

    python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False

Omit "state:drq_typed" (or pass "state:drq") to run the original,
non-classification-aware state through this same wrapper -- useful for
re-confirming Arm A results without switching scripts.
"""
import os
import torch
import dynamic_vlen_traffic_signal  # noqa: F401
import resco_benchmark.mdp_options.classification_state  # noqa: F401

# PyTorch 2.6+ changed torch.load's default to a stricter mode that RESCO's
# checkpoint loading code (agents/action_value/pfrl_dqn.py) wasn't written
# for. Safe here since checkpoints are only ever our own, locally-generated
# training output -- never loaded from an untrusted source.
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
with open(main_path) as f:
    code = compile(f.read(), main_path, "exec")
exec(code, {"__name__": "__main__", "__file__": main_path})