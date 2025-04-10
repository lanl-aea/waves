pip check
working_directory=${PWD}
# Avoid file system maximum path length issues during CI testing. Can't use /tmp on CI server because some system tests require execute permissions.
scratch_directory=/scratch/${USER}
if [[ -z ${scratch_directory} ]] && [[ -d ${scratch_directory} ]]; then working_directory=${scratch_directory}/${PKG_NAME}-${PKG_VERSION}-${PKG_BUILD_STRING}_${PKG_BUILDNUM}; fi
echo ${working_directory}
cd ${SP_DIR}/${PKG_NAME}
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=${working_directory} --unconditional-build
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=${working_directory} --unconditional-build
