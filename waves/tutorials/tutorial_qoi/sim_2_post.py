from waves import qoi

# Create QOIs for different simulation
load_2 = qoi.create_qoi(
    name="load",
    calculated=30.0,
    units="lbf",
    long_name="Transverse load",
    description="Transverse load through component D",
    group="Assembly DEF Preload",
    version="abcdef",
    date="2025-01-01",
)
stress = qoi.create_qoi(
    name="stress",
    calculated=100.0,
    units="MPa",
    long_name="Membrane stress",
    description="Membrane stress in component E",
    group="Assembly DEF Preload",
    version="abcdef",
    date="2025-01-01",
)
sim_2_qois = qoi.create_qoi_set((load_2, stress))

# Save calculated QOIs to CSV
qoi.write_qoi_set_to_csv(sim_2_qois, "sim_2_qois.csv")

# Save calculated QOIs to h5
sim_2_qois.to_netcdf("sim_2_qois.h5")
