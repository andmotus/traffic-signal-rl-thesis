"""
Patches RESCO's Vehicle class so vehicle length and minimum gap are read from
the actual vType (car/truck/motorcycle) instead of RESCO's hardcoded 5m/2.5m
passenger-car assumption. Values here must match inject_vehicle_types.py's
VTYPE_DEFS exactly, since that's what actually created these vehicle types.

Importantly: this does NOT modify resco_benchmark/traffic_signal.py at all.
It subclasses Vehicle and monkey-patches the traffic_signal module's Vehicle
attribute at import time. RESCO's own Signal class calls Vehicle(...) by
name, resolved from the module's namespace at call time (not at class
definition time) -- so once this module has been imported, every subsequent
Vehicle(...) call anywhere in RESCO uses this version automatically.

Import this before running any training, e.g. via run_typed_training.py.
"""
import resco_benchmark.traffic_signal as _traffic_signal_module
import traci.constants as tc

_OriginalVehicle = _traffic_signal_module.Vehicle

_TYPED_VEHICLE_PARAMS = {
    "truck": (9.5, 3.0),
    "motorcycle": (2.2, 1.2),
}


class DynamicLengthVehicle(_OriginalVehicle):
    def __init__(self, vehicle: dict) -> None:
        super().__init__(vehicle)
        # fall back to whatever the original assigned (its 5/2.5 default)
        # for anything that isn't truck/motorcycle -- car behavior, and the
        # earlier baseline reproduction numbers, stay unaffected.
        self.length, self.min_gap = _TYPED_VEHICLE_PARAMS.get(
            vehicle[tc.VAR_TYPE], (self.length, self.min_gap)
        )


_traffic_signal_module.Vehicle = DynamicLengthVehicle