system_test_directory=$PWD
cd $PREFIX/lib/python3.1?/site-packages/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=${system_test_directory}
