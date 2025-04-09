pip check
# FIXME: Set a system agnostic path if this shorter working directory fixes the system test failures.
# May need to pass in working directory as an environment variable through the recipe test environment.
# https://re-git.lanl.gov/aea/python-projects/waves/-/merge_requests/1163
working_directory="/scratch/$USER/waves/recipe-internal"
cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=${working_directory} --unconditional-build
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=${working_directory} --unconditional-build
