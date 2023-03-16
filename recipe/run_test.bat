waves docs --print-local-path
waves fetch tutorials --destination waves_tutorials
SET quickstart_directory=quickstart_directory
waves quickstart %quickstart_directory%
cd %quickstart_directory%
scons -h
waves visualize nominal --output-file nominal.svg
cd %SP_DIR%\%PKG_NAME%
pytest
