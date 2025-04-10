pip check
set system_test_directory=%CD%
cd %SP_DIR%\%PKG_NAME%
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=%system_test_directory%
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=%system_test_directory%
