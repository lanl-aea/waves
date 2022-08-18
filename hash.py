import xarray
import numpy

class ParameterStudy():

    def __init__(self, data):
        self.samples = data

        self.parameter_set_names = [f"set{number}" for number in range(self.samples.shape[0])]
        self.parameter_set_hashes = [hash(row.tobytes()) for row in self.samples]
        self.parameter_names = [f"parameter_{number}" for number in range(self.samples.shape[1])]

        self._create_parameter_study()

    def _create_parameter_array(self, data, name):
        """Create the standard structure for a parameter_study array

        requires:

        * ``self.parameter_set_names``: parameter set names used as rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study

        :param numpy.array data: 2D array of parameter study samples with shape (number of parameter sets, number of
            parameters).
        :param str name: Name of the array. Used as a data variable name when converting to parameter study dataset.
        """
        array = xarray.DataArray(
            data,
            coords=[self.parameter_set_names, self.parameter_names],
            dims=["parameter_sets", "parameters"],
            name=name
        )
        return array

    def _create_parameter_study(self):
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self.parameter_set_names``: parameter set names used as rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study
        * ``self.samples``: The parameter study samples

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

if __name__ == "__main__":
    data = numpy.array([[1, 10.0, 'a'], [2, 20.0, 'b']], dtype=object)
    study = ParameterStudy(data)
    print(study.parameter_study)
    print("")
    for set_name, set_hash, row in zip(study.parameter_set_names, study.parameter_set_hashes, study.samples):
        print(f"{set_name}: {set_hash}: {row}")
