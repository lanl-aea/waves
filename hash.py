class ParameterStudy():

    def __init__(data):  
        self.parameter_set_names = [f"set{number}" for number in range(data.shape[0])]
        self.parameter_names = [f"parameter_{number}" for number in range(data.shape[1])]
        self.samples = data

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
