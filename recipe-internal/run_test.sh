pip check
cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=$SP_DIR/$PKG_NAME/build/pytest
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=$SP_DIR/$PKG_NAME/build/pytest
