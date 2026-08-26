"""
Injects realistic vehicle-type heterogeneity (car / truck / motorcycle) into
RESCO route files, calibrated to real Kraftfahrt Bundesamt (KBA) fleet composition data for
Cologne and Ingolstadt (KBA Zulassungsbezirke und Gemeinden, 2024).

Source shares (car / motorcycle / truck):
  Cologne:    85.14% / 7.50% / 7.35%
  Ingolstadt: 87.39% / 7.55% / 5.05%

Physical vType parameters are set to realistic urban values so that the
classification signal actually affects signal-relevant behavior (clearance
time, acceleration profile), not just a label change.
"""
import xml.etree.ElementTree as ET
import random
import sys
import os

# --- Fleet composition targets, from KBA 2024 (Zulassungsbezirke und Gemeinden) ---
FLEET_SHARES = {
    "cologne":    {"car": 0.8514, "motorcycle": 0.0750, "truck": 0.0735},
    "ingolstadt": {"car": 0.8739, "motorcycle": 0.0755, "truck": 0.0505},
}

# --- Realistic urban vType physical parameters ---
# Car parameters follow the existing "pkw" definition already used in these scenarios
# (length 4.3m). Truck and motorcycle values reflect typical urban (not highway) profiles:
# truck = rigid urban delivery/box truck, not long-haul articulated.
VTYPE_DEFS = {
    "truck": dict(
        length="9.5", minGap="3.0", maxSpeed="20.0",  # ~72 km/h cap, realistic urban Lkw limit
        accel="1.1", decel="3.5", sigma="0.5", vClass="truck", guiShape="truck"
    ),
    "motorcycle": dict(
        length="2.2", minGap="1.2", maxSpeed="19.4",  # ~70 km/h urban cap
        accel="3.5", decel="6.0", sigma="0.5", vClass="motorcycle", guiShape="motorcycle"
    ),
}

def inject(rou_path, shares, seed=42):
    random.seed(seed)
    tree = ET.parse(rou_path)
    root = tree.getroot()

    # Find the existing car vType id (e.g. "pkw" in Cologne, "default_XXX"/"random_XXX" in Ingolstadt)
    existing_vtypes = root.findall("vType")
    car_ids = [vt.get("id") for vt in existing_vtypes if vt.get("vClass", "passenger") == "passenger"]

    # Add truck and motorcycle vType definitions (once)
    insert_at = list(root).index(existing_vtypes[-1]) + 1 if existing_vtypes else 0
    for name in ["truck", "motorcycle"]:
        vt = ET.Element("vType", {"id": name, **VTYPE_DEFS[name]})
        root.insert(insert_at, vt)
        insert_at += 1

    # Reassign vehicles (route files here use <trip> elements, not <vehicle>)
    vehicles = root.findall("trip")
    counts = {"car": 0, "motorcycle": 0, "truck": 0}
    for veh in vehicles:
        r = random.random()
        if r < shares["motorcycle"]:
            veh.set("type", "motorcycle")
            counts["motorcycle"] += 1
        elif r < shares["motorcycle"] + shares["truck"]:
            veh.set("type", "truck")
            counts["truck"] += 1
        else:
            counts["car"] += 1
            # leave as original car vType (unchanged)

    out_path = rou_path.replace(".rou.xml", "_typed.rou.xml")
    tree.write(out_path, encoding="UTF-8", xml_declaration=True)

    total = sum(counts.values())
    print(f"{os.path.basename(rou_path)}: {total} vehicles -> "
          f"car {counts['car']} ({counts['car']/total:.1%}), "
          f"motorcycle {counts['motorcycle']} ({counts['motorcycle']/total:.1%}), "
          f"truck {counts['truck']} ({counts['truck']/total:.1%})")
    print(f"  written to {out_path}")
    return out_path

if __name__ == "__main__":
    base = "../RESCO/resco_benchmark/environments"
    targets = [
        ("cologne1/cologne1.rou.xml", "cologne"),
        ("cologne8/cologne8.rou.xml", "cologne"),
        ("ingolstadt1/ingolstadt1.rou.xml", "ingolstadt"),
        ("ingolstadt21/ingolstadt21.rou.xml", "ingolstadt"),
    ]
    for rel_path, city in targets:
        full_path = os.path.join(base, rel_path)
        inject(full_path, FLEET_SHARES[city])