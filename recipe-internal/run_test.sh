pip check
cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --unconditional-build
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --unconditional-build
