import h5py
import numpy as np
from swiftsimio.accelerated import read_ranges_from_file
import json

def get_dataset_alias_map():
    """Retrieve a dictionary mapping of aliases to file paths

    Returns:
        _type_: _description_
    """
    return {
        "test_file": "/Users/hmoss/dirac-swift-api/sample_data/colibre_0023.hdf5"
    }

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class SWIFTProcessor:
    def __init__(self, data_alias_map: dict):
        """Class constructor

        Args:
            data_alias_map (dict): _description_
        """
        self.data_alias_map = data_alias_map

    def retrieve_filename(self, dataset_alias: str):
        """Retrieve a full path to a file from an alias.

        Args:
            dataset_alias (str): _description_

        Returns:
            _type_: _description_
        """
        return self.data_alias_map.get(dataset_alias)

    def load_ndarray_from_json(self, json_array: str):

        loaded_json = json.loads(json_array)
        restored_array = np.asarray(loaded_json)

        return restored_array

    def generate_json_from_ndarray(self, array: np.ndarray):
        json_array = json.dumps(array, cls=NumpyEncoder)
        return json_array

    def get_array_masked(
        self,
        filename: str,
        field: str,
        mask: None | np.ndarray,
        mask_size: int,
        columns: None | np.lib.index_tricks.IndexExpression = None,
    ):
        use_columns = columns is not None

        if not use_columns:
            columns = np.s_[:]

        with h5py.File(filename, "r") as handle:
            try:
                first_value = handle[field][0]
                output_type = first_value.dtype
                output_size = first_value.size

                if output_size != 1 and not use_columns:
                    output_shape = (mask_size, output_size)
                else:
                    output_shape = mask_size
                return read_ranges_from_file(
                    handle[field],
                    mask,
                    output_shape=output_shape,
                    output_type=output_type,
                    columns=columns,
                )
            except KeyError:
                print(f"Could not read {field}")
                return None

    def get_array_unmasked(
        self,
        filename: str,
        field: str,
        columns: None | np.lib.index_tricks.IndexExpression = None,
    ):
        use_columns = columns is not None

        if not use_columns:
            columns = np.s_[:]
        with h5py.File(filename, "r") as handle:
            try:
                result_array = (
                    handle[field][:, columns]
                    if handle[field].ndim > 1
                    else handle[field][:]
                )

                return result_array
            except KeyError:
                print(f"Could not read {field}")
                return None
