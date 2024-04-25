waves docs --print-local-path
waves fetch tutorials --destination waves_tutorials
SET modsim_template_directory=modsim_template_directory
waves fetch modsim_template --destination %modsim_template_directory%
cd %modsim_template_directory%
scons -h
waves visualize nominal --output-file nominal.svg
cd %SP_DIR%\%PKG_NAME%
pytest -vvv -n 4 -m "not programoperations and not systemtest"
pytest -vvv -n 4 -m "programoperations"
