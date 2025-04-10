pip check
system_test_directory=$PWD
cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=${system_test_directory}
