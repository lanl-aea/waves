set -o xtrace
working_directory=$PWD
cd $PREFIX/lib/python3.1?/site-packages/$PKG_NAME
pytest --basetemp ${working_directory}/pytest-temp -vvv -n 4 -m "not require_third_party" --system-test-dir=${working_directory}/systemtest
