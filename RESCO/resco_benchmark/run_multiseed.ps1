# Cologne1 Arm A (standard state) -- 5 additional seeds
python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@cologne1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed

# Cologne1 Arm B (classification-aware) -- 5 additional seeds
python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@cologne1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed

# Ingolstadt1 Arm A -- 5 additional seeds
python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_typed_training.py "@ingolstadt1_typed" "@IDQN" libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed

# Ingolstadt1 Arm B -- 5 additional seeds
python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed
python run_classification_training.py "@ingolstadt1_typed" "@IDQN" state:drq_typed libsumo:False save_console_log:False gui:False episodes:200 log_dir:results/multiseed