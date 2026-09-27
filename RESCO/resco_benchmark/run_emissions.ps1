# Fixed-Time, Cologne1 -- no training needed, fast
python run_emissions_tracking.py "@cologne1_typed" "@FIXED" libsumo:False save_console_log:False gui:False episodes:100 log_dir:results/emissions

# Fixed-Time, Ingolstadt1 -- no training needed, fast
python run_emissions_tracking.py "@ingolstadt1_typed" "@FIXED" libsumo:False save_console_log:False gui:False episodes:100 log_dir:results/emissions

# Standard-state IDQN, Cologne1 -- real training, 200 episodes
python run_emissions_tracking.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/emissions

# Standard-state IDQN, Ingolstadt1 -- real training, 200 episodes
python run_emissions_tracking.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/emissions