import argparse

from waves import qoi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", type=float, default=5.0)
    parser.add_argument("--gap", type=float, default=0.85)
    args = parser.parse_args()

    # Create multiple QOIs
    load = qoi.create_qoi(
        name="load",
        calculated=args.load,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload",
        version="abcdef",
        date="2025-01-01",
    )
    gap = qoi.create_qoi(
        name="gap",
        calculated=args.gap,
        units="mm",
        long_name="Radial gap",
        description="Radial gap between components A and B",
        group="Assembly ABC Preload",
        version="abcdef",
        date="2025-01-01",
    )

    # Combine QOIs into calculated QOIs set
    simulation_1_qois = qoi.create_qoi_set((load, gap))
    print(simulation_1_qois)
    print(simulation_1_qois["load"])

    # Save calculated QOIs to CSV
    qoi.write_qoi_set_to_csv(simulation_1_qois, "simulation_1_qois.csv")

    # Save calculated QOIs to h5
    simulation_1_qois.to_netcdf("simulation_1_qois.h5", engine="h5netcdf")


if __name__ == "__main__":
    main()
