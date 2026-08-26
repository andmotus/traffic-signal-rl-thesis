"""
Adds cologne1_typed / ingolstadt1_typed environment presets to RESCO's own
config system, so `python main.py @cologne1_typed @IDQN ...` actually trains
on the KBA-calibrated heterogeneous route files.

IMPORTANT CORRECTION vs. the earlier update_sumocfg.py script: RESCO's
@presets are resolved entirely from config/config.yaml and config/signal.yaml
-- it never reads the .sumocfg files. update_sumocfg.py is only useful if you
ever run plain `sumo -c ...` directly outside RESCO. This script is the one
that actually matters for feeding typed data into RESCO-trained agents.

Two files need a matching new block, because RESCO looks up config by map
name in both places:
  - config.yaml:  network/route file paths + start/end time
  - signal.yaml:  per-intersection lane_sets and phase_pairs (unchanged
                   from the original, since only vehicle types changed,
                   not the physical network -- so this is a safe, exact copy)

Run this once. Safe to re-run: it skips any preset that already exists in
either file rather than duplicating it.

Before running: set RESCO_ROOT below to your local RESCO folder.
"""
import re
import os

RESCO_ROOT = "../RESCO"

CONFIG_YAML = os.path.join(RESCO_ROOT, "resco_benchmark", "config", "config.yaml")
SIGNAL_YAML = os.path.join(RESCO_ROOT, "resco_benchmark", "config", "signal.yaml")
ENVIRONMENTS_DIR = os.path.join(RESCO_ROOT, "resco_benchmark", "environments")

# (existing preset name, route filename to use instead, start_time, end_time)
NEW_PRESETS = [
    ("cologne1", "cologne1_typed.rou.xml", 25200, 28800),
    ("ingolstadt1", "ingolstadt1_typed.rou.xml", 57600, 61200),
]


def add_config_yaml_preset(text, base_name, route_filename, start_time, end_time):
    new_name = f"{base_name}_typed"
    if re.search(rf"^\s+{new_name}:", text, re.MULTILINE):
        print(f"config.yaml: '{new_name}' already present, skipping")
        return text

    pattern = rf"(        {base_name}:[ \t]*\n(?:            .*\n)*)"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not find existing '{base_name}:' block in config.yaml")

    env_folder = os.path.join(ENVIRONMENTS_DIR, base_name)
    network_path = os.path.join(env_folder, f"{base_name}.net.xml")
    route_path = os.path.join(env_folder, route_filename)

    new_block = (
        f"        {new_name}:     \n"
        f"            network: {network_path}\n"
        f"            route: {route_path}\n"
        f"            start_time: {start_time}    \n"
        f"            end_time: {end_time}\n"
        f"\n\n"
    )
    print(f"config.yaml: adding '{new_name}' (route -> {route_filename})")
    return text[:match.end()] + new_block + text[match.end():]


def find_brace_block(text, key):
    marker = f"'{key}': {{"
    start = text.find(marker)
    if start == -1:
        raise ValueError(f"Could not find '{key}': {{ block in signal.yaml")
    brace_start = start + len(marker) - 1
    depth, i = 0, brace_start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise ValueError("No matching close brace found")


def add_signal_yaml_preset(text, base_name):
    new_name = f"{base_name}_typed"
    if f"'{new_name}': {{" in text:
        print(f"signal.yaml: '{new_name}' already present, skipping")
        return text

    start, end = find_brace_block(text, base_name)
    block = text[start:end]
    new_block = block.replace(f"'{base_name}': {{", f"'{new_name}': {{", 1)
    print(f"signal.yaml: adding '{new_name}' (copy of '{base_name}' geometry, unchanged)")
    return text[:end] + "\n" + new_block + text[end:]


if __name__ == "__main__":
    with open(CONFIG_YAML, "r", encoding="utf-8") as f:
        config_text = f.read()
    with open(SIGNAL_YAML, "r", encoding="utf-8") as f:
        signal_text = f.read()

    for base_name, route_filename, start_time, end_time in NEW_PRESETS:
        config_text = add_config_yaml_preset(config_text, base_name, route_filename, start_time, end_time)
        signal_text = add_signal_yaml_preset(signal_text, base_name)

    with open(CONFIG_YAML, "w", encoding="utf-8") as f:
        f.write(config_text)
    with open(SIGNAL_YAML, "w", encoding="utf-8") as f:
        f.write(signal_text)

    print("\nDone. @cologne1_typed and @ingolstadt1_typed are now valid RESCO environment presets.")