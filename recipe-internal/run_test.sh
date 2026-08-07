set -o xtrace
working_directory=${PWD}
# Avoid file system maximum path length issues during CI testing. Can't use /tmp on CI server because some system tests require execute permissions.
scratch_root=/scratch
if [[ ! -z ${scratch_root} ]] && [[ -d ${scratch_root} ]]; then working_directory=${scratch_root}/$(id -un)/${PKG_NAME}-${PKG_VERSION}-${PKG_BUILD_STRING}; fi
if [[ ! -d ${working_directory} ]]; then mkdir -p ${working_directory}; fi
echo "working directory: ${working_directory}"
cd $PREFIX/lib/python3.1?/site-packages/$PKG_NAME
pytest --basetemp ${working_directory}/pytest-temp -vvv -n 4 -m "not require_third_party" --system-test-dir=${working_directory}/systemtest --unconditional-build
pytest --basetemp ${working_directory}/pytest-temp -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=${working_directory}/systemtest --unconditional-build
