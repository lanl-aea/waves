import argparse

from waves import qoi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", type=float, default=30.0)
    parser.add_argument("--stress", type=float, default=100.0)
    args = parser.parse_args()

    # Create QOIs for different simulation
    load_2 = qoi.create_qoi(
        name="load",
        calculated=args.load,
        units="lbf",
        long_name="Transverse load",
        description="Transverse load through component D",
        group="Assembly DEF Preload",
        version="abcdef",
        date="2025-01-01",
    )
    stress = qoi.create_qoi(
        name="stress",
        calculated=args.stress,
        units="MPa",
        long_name="Membrane stress",
        description="Membrane stress in component E",
        group="Assembly DEF Preload",
        version="abcdef",
        date="2025-01-01",
    )

    # Combine QOIs into calculated QOIs set
    simulation_2_qois = qoi.create_qoi_set((load_2, stress))

    # Save calculated QOIs to CSV
    qoi.write_qoi_set_to_csv(simulation_2_qois, "simulation_2_qois.csv")

    # Save calculated QOIs to h5
    simulation_2_qois.to_netcdf("simulation_2_qois.h5", engine="h5netcdf")


if __name__ == "__main__":
    main()
