# Cologne1 Arm A (standard state) -- 15 additional seeds
for ($i = 1; $i -le 15; $i++) {
    python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed21
}

# Cologne1 Arm B (classification-aware) -- 15 additional seeds
for ($i = 1; $i -le 15; $i++) {
    python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed21
}

# Ingolstadt1 Arm A (standard state) -- 15 additional seeds
for ($i = 1; $i -le 15; $i++) {
    python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed21
}

# Ingolstadt1 Arm B (classification-aware) -- 15 additional seeds
for ($i = 1; $i -le 15; $i++) {
    python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed21
}