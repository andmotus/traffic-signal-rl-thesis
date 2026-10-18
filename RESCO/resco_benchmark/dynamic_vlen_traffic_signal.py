"""
Vehicle-length correction for RESCO's internal vehicle representation.

RESCO's Vehicle class (traffic_signal.py) gives every observed vehicle a
length of 5 m and a minimum gap of 2.5 m, marked in the source as a
passenger-car simplification. This module subclasses Vehicle so that trucks
and motorcycles carry the length and gap of their SUMO type definitions
(9.5/3.0 m and 2.2/1.2 m, the values of VTYPE_DEFS in
scripts/inject_vehicle_types.py); every other vehicle keeps RESCO's 5/2.5 m.
The subclass replaces the class in the traffic_signal module at import time.
RESCO's Signal class resolves Vehicle(...) from the module namespace when it
is called, so every vehicle created after the import uses the subclass.

Effect on the experiments: none. In this RESCO version Vehicle.length and
Vehicle.min_gap are read only by the CoSLight state (mdp_options/states.py),
which is not used in the thesis. The drq, drq_typed, wave and mplight states,
the rewards and the logged metrics do not use them. A seeded test episode run
with and without this module gave identical states and rewards on both
networks and for both state representations (thesis, Section 3.2). The
correction is kept because later work with a length-based state on
heterogeneous demand would need it.

The physical vehicle lengths are not affected by any of this: SUMO simulates
every vehicle with the length of its vType in the route file.

Does not modify traffic_signal.py. Imported by run_typed_training.py and
run_classification_training.py; the CO2 runs (run_emissions_tracking.py) were
made without it.
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