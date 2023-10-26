waves docs --print-local-path
waves fetch tutorials --destination waves_tutorials
modsim_template_directory="modsim_template_directory"
waves fetch modsim_template --destination ${modsim_template_directory}
cd ${modsim_template_directory}
scons -h
waves visualize nominal --output-file nominal.svg
cd $SP_DIR/$PKG_NAME
pytest
