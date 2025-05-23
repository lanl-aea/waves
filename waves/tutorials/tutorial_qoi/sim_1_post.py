from waves import qoi

# Create multiple QOIs
load = qoi.create_qoi(
    name="load",
    calculated=5.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload",
    version="abcdef",
    date="2025-01-01",
)
gap = qoi.create_qoi(
    name="gap",
    calculated=1.0,
    units="mm",
    long_name="Radial gap",
    description="Radial gap between components A and B",
    group="Assembly ABC Preload",
    version="abcdef",
    date="2025-01-01",
)

# Combine QOIs into calculated QOIs set
sim_1_qois = qoi.create_qoi_set((load, gap))
print(sim_1_qois)
print(sim_1_qois["load"])

# Save calculated QOIs to CSV
qoi.write_qoi_set_to_csv(sim_1_qois, "sim_1_qois.csv")

# Save calculated QOIs to h5
sim_1_qois.to_netcdf("sim_1_qois.h5")
