"""
Creates *_typed.sumocfg files that point at the KBA-calibrated *_typed.rou.xml
route files produced by inject_vehicle_types.py.

The original .sumocfg files are left untouched, so baseline reproduction runs
(against the unmodified, single-vehicle-type data) still work exactly as before.
Run this after inject_vehicle_types.py.
"""
import xml.etree.ElementTree as ET
import os

def update_sumocfg(cfg_path, new_route_file):
    tree = ET.parse(cfg_path)
    root = tree.getroot()

    route_files_elem = root.find("input/route-files")
    if route_files_elem is None:
        raise ValueError(f"No <route-files> element found in {cfg_path}")

    old_value = route_files_elem.get("value")
    route_files_elem.set("value", new_route_file)

    out_path = cfg_path.replace(".sumocfg", "_typed.sumocfg")
    tree.write(out_path, encoding="UTF-8", xml_declaration=True)

    print(f"{os.path.basename(cfg_path)} -> {os.path.basename(out_path)} "
          f"(route-files: {old_value} -> {new_route_file})")
    return out_path

if __name__ == "__main__":
    base = "../RESCO/resco_benchmark/environments"
    # Same scenario list as inject_vehicle_types.py — keep these two in sync
    # if you add Cologne3 / Ingolstadt7 later.
    targets = [
        "cologne1/cologne1.sumocfg",
        "cologne8/cologne8.sumocfg",
        "ingolstadt1/ingolstadt1.sumocfg",
        "ingolstadt21/ingolstadt21.sumocfg",
    ]
    for rel_cfg in targets:
        full_cfg = os.path.join(base, rel_cfg)
        if not os.path.exists(full_cfg):
            print(f"WARNING: {full_cfg} not found, skipping")
            continue
        scenario_name = os.path.basename(full_cfg).replace(".sumocfg", "")
        new_route = f"{scenario_name}_typed.rou.xml"
        update_sumocfg(full_cfg, new_route)