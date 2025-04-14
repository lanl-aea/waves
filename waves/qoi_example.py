import xarray

import waves

# Create multiple QOIs
load = waves.qoi.create_qoi(
    name="load",
    calculated=5.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload",
    version="abcdef",
    date="2025-01-01",
)
gap = waves.qoi.create_qoi(
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
sim_1_qois = waves.qoi.create_qoi_set((load, gap))
sim_1_qois
sim_1_qois["load"]

# Save calculated QOIs to CSV
waves.qoi.write_qoi_set_to_csv(sim_1_qois, "sim_1_qois.csv")

# Save calculated QOIs to h5
sim_1_qois.to_netcdf("sim_1_qois.h5")

# Read expected QOIs from CSV
sim_1_expected_qois = waves.qoi._read_qoi_set("sim_1_expected_qois.csv")
sim_1_expected_qois

# Compare calculated to expected values
# TODO: write function for CLI subcommand
sim_1_qois = xarray.merge((sim_1_qois, sim_1_expected_qois))
waves.qoi._add_tolerance_attribute(sim_1_qois)
sim_1_qois

# Write comparison result to CSV
waves.qoi.write_qoi_set_to_csv(sim_1_qois, "sim_1_qois_diff.csv")

# Accept new calculated values
# TODO: write function for CLI subcommand

# Create QOIs for different simulation
load_2 = waves.qoi.create_qoi(
    name="load",
    calculated=30.0,
    units="lbf",
    long_name="Transverse load",
    description="Transverse load through component D",
    group="Assembly DEF Preload",
    version="abcdef",
    date="2025-01-01",
)
stress = waves.qoi.create_qoi(
    name="stress",
    calculated=100.0,
    units="MPa",
    long_name="Membrane stress",
    description="Membrane stress in component E",
    group="Assembly DEF Preload",
    version="abcdef",
    date="2025-01-01",
)
sim_2_qois = waves.qoi.create_qoi_set((load_2, stress))

# Combine QOIs into archive
commit_1_qois = waves.qoi._create_qoi_archive((*sim_1_qois.values(), *sim_2_qois.values()))
# TODO: avoid writing attributes at dataset level
commit_1_qois["Assembly ABC Preload"]["load"]

# Write archive to H5
commit_1_qois.to_netcdf("commit_1_qois.h5")

# Create tolerance report from archive
waves.qoi._write_qoi_report(commit_1_qois, "commit_1_report.pdf")

# Create QOIs for different commit
commit_2_qois = waves.qoi._create_qoi_archive(
    (
        waves.qoi.create_qoi(
            name="load",
            calculated=5.3,
            expected=4.5,
            lower_limit=3.5,
            upper_limit=5.5,
            units="N",
            long_name="Axial Load",
            description="Axial load through component XYZ",
            group="Assembly ABC Preload",
            version="ghijkl",
            date="2025-02-01",
        ),
        waves.qoi.create_qoi(
            name="gap",
            calculated=1.0,
            expected=0.95,
            lower_limit=0.85,
            upper_limit=1.05,
            units="mm",
            long_name="Radial gap",
            description="Radial gap between components A and B",
            group="Assembly ABC Preload",
            version="ghijkl",
            date="2025-02-01",
        ),
        waves.qoi.create_qoi(
            name="load",
            calculated=35.0,
            units="lbf",
            long_name="Transverse load",
            description="Transverse load through component D",
            group="Assembly DEF Preload",
            version="ghijkl",
            date="2025-02-01",
        ),
        waves.qoi.create_qoi(
            name="stress",
            calculated=110.0,
            units="MPa",
            long_name="Membrane stress",
            description="Membrane stress in component E",
            group="Assembly DEF Preload",
            version="ghijkl",
            date="2025-02-01",
        ),
    )
)
commit_2_qois.to_netcdf("commit_2_qois.h5")

# Merge archives
all_commit_qois = waves.qoi._merge_qoi_archives((commit_1_qois, commit_2_qois))
print(all_commit_qois)

# Create QOI history report
waves.qoi._qoi_history_report(all_commit_qois, "qoi_history.pdf", add_git_commit_date=False)

# Create QOI set with set_name attribute for parameter studies
# Group must still be unique
set_0_qoi = waves.qoi.create_qoi(
    name="load",
    calculated=5.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload set_0",
    set_name="set_0",
    version="abcdef",
)
set_1_qoi = waves.qoi.create_qoi(
    name="load",
    calculated=6.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload set_1",
    set_name="set_1",
    version="abcdef",
)
set_2_qoi = waves.qoi.create_qoi(
    name="load",
    calculated=7.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload set_2",
    set_name="set_2",
    version="abcdef",
)
set_3_qoi = waves.qoi.create_qoi(
    name="load",
    calculated=8.0,
    units="N",
    long_name="Axial Load",
    description="Axial load through component XYZ",
    group="Assembly ABC Preload set_3",
    set_name="set_3",
    version="abcdef",
)

study = waves.parameter_generators.CartesianProduct(
    {"height": [1.0, 2.0], "width": [0.2, 0.4]},
    output_file="study.h5",
    set_name_template="set_@number",
)
study.parameter_study
qoi_study = waves.qoi._create_qoi_study((set_0_qoi, set_1_qoi, set_2_qoi, set_3_qoi), study.parameter_study)
qoi_study

# Reindex on independent parameters
qoi_study = qoi_study.set_index(set_name=("height", "width")).unstack("set_name")
qoi_study
qoi_study.sel(height=2.0)
