pip check
system_test_directory=${PWD}
# Avoid file system maximum path length issues during CI testing. Can't use /tmp on CI server because some system tests require execute permissions.
scratch_root=/scratch
if [[ ! -z ${scratch_root} ]] && [[ -d ${scratch_root} ]]; then system_test_directory=${scratch_root}/${USER}/${PKG_NAME}-${PKG_VERSION}-${PKG_BUILD_STRING}_${PKG_BUILDNUM}; fi
echo "system test directory: ${system_test_directory}"
cd ${SP_DIR}/${PKG_NAME}
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=${system_test_directory} --unconditional-build
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=${system_test_directory} --unconditional-build
