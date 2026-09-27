"""
Enables SUMO's emissions device so CO2 can be measured directly, for H4's
national scaling model. RESCO's own reward metric (waiting-time-based) has
no CO2 component, and RESCO does not enable SUMO's emissions device by
default -- confirmed directly in multi_signal.py's build_sumo_cmd.

RESCO already writes a tripinfo_<episode>.xml file for every episode as
part of its own reward computation. Once the emissions device is active,
CO2 data lands in those same files automatically -- no live TraCI hooking
needed. This module only adds the missing SUMO flag and prevents RESCO's
own end-of-run cleanup from deleting the file before it can be read.

Does not modify multi_signal.py or utils.py.
"""
import resco_benchmark.multi_signal as _multi_signal_module

_original_build_sumo_cmd = _multi_signal_module.MultiSignal.build_sumo_cmd


def _build_sumo_cmd_with_emissions(self):
    cmd = _original_build_sumo_cmd(self)
    cmd += ["--device.emissions.probability", "1.0"]
    return cmd


_multi_signal_module.MultiSignal.build_sumo_cmd = _build_sumo_cmd_with_emissions

# RESCO deletes tripinfo_*.xml (along with signals.pkl, state.xml.gz,
# metrics_*.csv) at the end of every run via cleanup_log_dir() -- see
# utils/utils.py. Disable it for these validation runs only, so the file
# survives for extract_co2.py to read. Must happen before main.py's own
# "from resco_benchmark.utils.utils import cleanup_log_dir" line runs.
import resco_benchmark.utils.utils as _utils_module
_utils_module.cleanup_log_dir = lambda: None