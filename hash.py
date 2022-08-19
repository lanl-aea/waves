import hashlib
import string

import xarray
import numpy


class _AtSignTemplate(string.Template):
    """Use the CMake '@' delimiter in a Python 'string.Template' to avoid clashing with bash variable syntax"""
    delimiter = '@'


class ParameterStudy():

    def __init__(self, data):
        self.samples = data
        self.set_name_template = _AtSignTemplate("set@number")

    def _create_parameter_set_hashes(self):
        """
        requires:

        * ``self.samples``: The parameter study samples. Rows are sets. Columns are parameters.

        creates attribute:

        * ``self.parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        """
        self.parameter_set_hashes = []
        for row in self.samples:
            set_values_catenation = ''.join(repr(element) for element in row)
            set_hash = hashlib.md5(set_values_catenation.encode('utf-8')).hexdigest()
            self.parameter_set_hashes.append(set_hash)

    def _create_parameter_set_names(self):
        """Construct parameter set names from the output file template and number of parameter sets

        Creates the class attribute ``self.parameter_set_names`` required to populate the ``generate()`` method's
        parameter study Xarray dataset object.

        requires:

        * ``self.parameter_set_hashes``: parameter set content hash set by ``_create_parameter_set_hashes``

        creates attribute:

        * ``self.parameter_set_names``: parameter set names identifying rows of parameter study
        """
        parameter_set_names = []
        for number in range(self.samples.shape[0]):
            template = self.set_name_template
            parameter_set_names.append(template.substitute({'number': number}))
        self.parameter_set_names = xarray.DataArray(parameter_set_names, coords=[self.parameter_set_hashes], dims=['parameter_set_hash'], name='parameter_set_names')

    def _create_parameter_array(self, data, name):
        """Create the standard structure for a parameter_study array

        requires:

        * ``self.parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study

        :param numpy.array data: 2D array of parameter study samples with shape (number of parameter sets, number of
            parameters).
        :param str name: Name of the array. Used as a data variable name when converting to parameter study dataset.
        """
        array = xarray.DataArray(
            data,
            coords=[self.parameter_set_hashes, self.parameter_names],
            dims=["parameter_set_hash", "parameters"],
            name=name
        )
        return array

    def _create_parameter_study(self):
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self.parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study
        * ``self.samples``: The parameter study samples. Rows are sets. Columns are parameters.

        optional:

        * ``self.quantiles``: The quantiles associated with the paramter study sampling distributions

        creates attribute:

        * ``self.parameter_study``
        """
        samples = self._create_parameter_array(self.samples, name="samples")
        if hasattr(self, "quantiles"):
            quantiles = self._create_parameter_array(self.quantiles, name="quantiles")
            self.parameter_study = xarray.concat([quantiles, samples],
                    xarray.DataArray(["quantiles", "samples"], dims="data_type")).to_dataset("parameters")
        else:
            self.parameter_study = samples.to_dataset("parameters").expand_dims(data_type=["samples"])
        self.parameter_study = xarray.merge([self.parameter_study,
                                             self.parameter_set_names]).set_coords('parameter_set_names')

    def _merge_parameter_studies(self, other_study):
        self.parameter_study = xarray.merge([other_study.astype(object), self.parameter_study])
        # Recover sample numpy array to match merged study
        merged_samples = []
        for set_hash, parameter_set in study3.parameter_study.sel(data_type='samples').groupby('parameter_set_hash'):
            merged_samples.append(parameter_set.squeeze().to_array().to_numpy())
        self.samples = numpy.array(merged_samples, dtype=object)
        # Recalculate lists with lengths matching the number of parameter sets
        self.parameter_set_hashes = list(self.parameter_study.coords['parameter_set_hash'].values)
        self._create_parameter_set_names()

    def generate(self, other_study=None):
        # In WAVES, self.samples would be set here.
        self._create_parameter_set_hashes()
        self._create_parameter_set_names()
        self.parameter_names = [f"parameter_{number}" for number in range(self.samples.shape[1])]
        self._create_parameter_study()

        if other_study:
            self._merge_parameter_studies(other_study)


if __name__ == "__main__":
    print('\nStudy1:')
    data1 = numpy.array([[1, 10.1, 'a'], [2, 20.2, 'b'], [4, 40.4, 'd']], dtype=object)
    study1 = ParameterStudy(data1)
    study1.generate()
    print(study1.parameter_study)
    print("")
    for set_name, set_hash, row in zip(study1.parameter_set_names, study1.parameter_set_hashes, study1.samples):
        print(f"{set_name}: {set_hash}: {row}")

    print('\nStudy1: read from file')
    study1.parameter_study.to_netcdf(path='study1.h5', mode='w', format="NETCDF4", engine='h5netcdf')
    study1.parameter_study.close()
    study_read = xarray.open_dataset('study1.h5')
    print(study_read)

    print('\nStudy2:')
    data2 = numpy.array([[1, 10.1, 'a'], [3, 30.3, 'c'], [5, 50.5, 'e'], [2, 20.2, 'b']], dtype=object)
    study2 = ParameterStudy(data2)
    study2.generate()
    print(study2.parameter_study)
    print("")
    for set_name, set_hash, row in zip(study2.parameter_set_names, study2.parameter_set_hashes, study2.samples):
        print(f"{set_name}: {set_hash}: {row}")

    print('\nStudy3:')
    study3 = ParameterStudy(data2)
    study3.generate(study_read)
    print(study3.parameter_study)
    print("")
    for set_name, set_hash, row in zip(study3.parameter_set_names, study3.parameter_set_hashes, study3.samples):
        print(f"{set_name}: {set_hash}: {row}")
