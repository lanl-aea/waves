import xarray

import qoi

# Create multiple QOIs
load = qoi.create_qoi(
    name="load",
    calculated=5.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload",
    commit="abcdef",
)
gap = qoi.create_qoi(
    name="gap",
    calculated=1.0,
    units="mm",
    long_name="Radial gap",
    description="Radial gap between components A and B",
    group="Assembly ABC Preload",
    commit="abcdef",
)

# Combine QOIs into calculated QOIs set
sim_1_qois = qoi.create_qoi_set((load, gap))
sim_1_qois
sim_1_qois['load']

# Save calculated QOIs to CSV
qoi.write_qoi_set_to_csv(sim_1_qois, "sim_1_qois.csv")

# Save calculated QOIs to h5
sim_1_qois.to_netcdf("sim_1_qois.h5")

# Read expected QOIs from CSV
sim_1_expected_qois = qoi.read_qoi_set("sim_1_expected_qois.csv")
sim_1_expected_qois

# Compare calculated to expected values
# TODO: write function for CLI subcommand
sim_1_qois = xarray.merge((sim_1_qois, sim_1_expected_qois))
qoi.add_tolerance_attribute(sim_1_qois)
sim_1_qois

# Write comparison result to CSV
qoi.write_qoi_set_to_csv(sim_1_qois, "sim_1_qois_diff.csv")

# Accept new calculated values
# TODO: write function for CLI subcommand

# Create QOIs for different simulation
load_2 = qoi.create_qoi(
    name="load",
    calculated=30.0,
    units="lbf",
    long_name="Transverse load",
    description="Transverse load through component D",
    group="Assembly DEF Preload",
    commit="abcdef",
)
stress = qoi.create_qoi(
    name="stress",
    calculated=100.0,
    units="MPa",
    long_name="Membrane stress",
    description="Membrane stress in component E",
    group="Assembly DEF Preload",
    commit="abcdef",
)
sim_2_qois = qoi.create_qoi_set((load_2, stress))

# Combine QOIs into archive
commit_1_qois = qoi.create_qoi_archive((*sim_1_qois.values(), *sim_2_qois.values()))
# TODO: avoid writing attributes at dataset level
commit_1_qois['Assembly ABC Preload']['load']

# Write archive to H5
commit_1_qois.to_netcdf("commit_1_qois.h5")

# Create tolerance report from archive
qoi.write_qoi_report(commit_1_qois, "commit_1_report.pdf")

# Create QOIs for different commit
commit_2_qois = qoi.create_qoi_archive(
    (
        qoi.create_qoi(
            name="load",
            calculated=5.3,
            expected=4.5,
            lower_limit=3.5,
            upper_limit=5.5,
            units="N",
            long_name="Axial Load",
            description="Axial load through component XYZ",
            group="Assembly ABC Preload",
            commit="ghijkl",
        ),
        qoi.create_qoi(
            name="gap",
            calculated=1.0,
            expected=0.95,
            lower_limit=0.85,
            upper_limit=1.05,
            units="mm",
            long_name="Radial gap",
            description="Radial gap between components A and B",
            group="Assembly ABC Preload",
            commit="ghijkl",
        ),
        qoi.create_qoi(
            name="load",
            calculated=35.0,
            units="lbf",
            long_name="Transverse load",
            description="Transverse load through component D",
            group="Assembly DEF Preload",
            commit="ghijkl",
        ),
        qoi.create_qoi(
            name="stress",
            calculated=110.0,
            units="MPa",
            long_name="Membrane stress",
            description="Membrane stress in component E",
            group="Assembly DEF Preload",
            commit="ghijkl",
        )
    )
)
commit_2_qois.to_netcdf("commit_2_qois.h5")

# Merge archives
all_commit_qois = qoi.merge_qoi_archives((commit_1_qois, commit_2_qois))
all_commit_qois

# Create QOI history report
qoi.qoi_history_report(all_commit_qois, "qoi_history.pdf")

