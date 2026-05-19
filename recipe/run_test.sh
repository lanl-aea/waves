set -o xtrace
system_test_directory=$PWD
cd $PREFIX/lib/python3.1?/site-packages/$PKG_NAME
pytest --basetemp ${system_test_directory}/pytest-temp -vvv -n 4 -m "not require_third_party" --system-test-dir=${system_test_directory}
