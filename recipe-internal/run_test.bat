set working_directory=%CD%
cd %PREFIX%\Lib\site-packages\%PKG_NAME%
pytest --basetemp %working_directory%\pytest-temp -vvv -n 4 -m "not require_third_party" --system-test-dir=%working_directory%
pytest --basetemp %working_directory%\pytest-temp -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=%working_directory%\systemtest
