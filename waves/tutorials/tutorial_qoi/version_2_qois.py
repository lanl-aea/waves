from waves import qoi


version_2_qois = qoi._create_qoi_archive(
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
            version="ghijkl",
            date="2025-02-01",
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
            version="ghijkl",
            date="2025-02-01",
        ),
        qoi.create_qoi(
            name="load",
            calculated=35.0,
            units="lbf",
            long_name="Transverse load",
            description="Transverse load through component D",
            group="Assembly DEF Preload",
            version="ghijkl",
            date="2025-02-01",
        ),
        qoi.create_qoi(
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
version_2_qois.to_netcdf("version_2_qois.h5", engine="h5netcdf")
