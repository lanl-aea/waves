pip check
working_directory=$PWD
cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --unconditional-build --system-test-dir=${working_directory}
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --unconditional-build --system-test-dir=${working_directory}
