set system_test_directory=%CD%
cd %PREFIX%\Lib\site-packages\%PKG_NAME%
pytest --basetemp %system_test_directory%\pytest-temp -vvv -n 4 -m "not require_third_party" --system-test-dir=%system_test_directory%
