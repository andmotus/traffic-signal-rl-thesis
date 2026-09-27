"""
Extracts total and per-vehicle CO2 from a run's final-episode tripinfo file.

Usage: python extract_co2.py "results/<run folder name>"
"""
import sys
import os
import glob
import xml.etree.ElementTree as ET


def extract_co2(tripinfo_path):
    tree = ET.parse(tripinfo_path)
    root = tree.getroot()
    total_co2_mg = 0.0
    n_vehicles = 0
    for trip in root.findall("tripinfo"):
        n_vehicles += 1
        emissions = trip.find("emissions")
        if emissions is not None:
            total_co2_mg += float(emissions.get("CO2_abs"))
    return total_co2_mg, n_vehicles


if __name__ == "__main__":
    run_folder = sys.argv[1]
    matches = glob.glob(os.path.join(run_folder, "**", "tripinfo_*.xml"), recursive=True)
    if not matches:
        print(f"No tripinfo file found under {run_folder}")
        sys.exit(1)
    matches.sort(key=lambda p: int(os.path.basename(p).replace("tripinfo_", "").replace(".xml", "")))
    tripinfo_path = matches[-1]

    total_co2_mg, n_vehicles = extract_co2(tripinfo_path)
    print(f"File: {tripinfo_path}")
    print(f"Vehicles: {n_vehicles}")
    print(f"Total CO2: {total_co2_mg / 1e6:,.2f} kg")
    print(f"CO2 per vehicle: {total_co2_mg / n_vehicles / 1000:,.1f} g")