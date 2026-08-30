"""
Classification-aware state representation for IDQN.

Extends RESCO's existing "drq" state function (states.py, same folder) with
per-lane car/truck/motorcycle counts, using vehicle.type -- the same
attribute dynamic_vlen_traffic_signal.py already reads.

Registers as a new option alongside drq rather than replacing it, so both
stay selectable via config. Does not modify states.py or main.py -- see the
registration line at the end of this file for how RESCO actually picks this
up. Point cfg.state at "drq_typed" (instead of "drq") to use it.
"""

import numpy as np
import resco_benchmark.mdp_options.states as _states_module

def drq_typed(signals):
    observations = dict()
    for signal_id in signals:
        signal = signals[signal_id]
        obs = []
        act_index = signal.current_phase
        for i, lane in enumerate(signal.lanes):
            lane_obs = []
            if i == act_index:
                lane_obs.append(1)
            else:
                lane_obs.append(0)

            total_wait, total_speed = 0, 0
            car_count, truck_count, motorcycle_count = 0, 0, 0
            vehicles = signal.observation.get_lane(lane).vehicles
            for vehicle in vehicles.values():
                total_wait += vehicle.wait
                total_speed += vehicle.average_speed
                if vehicle.type == "truck":
                    truck_count += 1
                elif vehicle.type == "motorcycle":
                    motorcycle_count += 1
                else:
                    car_count += 1

            lane_obs.append(signal.observation.get_lane(lane).approaching)
            lane_obs.append(total_wait)
            lane_obs.append(signal.observation.get_lane(lane).queued)
            lane_obs.append(total_speed)
            lane_obs.append(car_count)
            lane_obs.append(truck_count)
            lane_obs.append(motorcycle_count)

            obs.append(lane_obs)
        observations[signal_id] = np.expand_dims(np.asarray(obs), axis=0)
    return observations

#actual wrapper to register this new state function with RESCO's existing states.py module
_states_module.drq_typed = drq_typed