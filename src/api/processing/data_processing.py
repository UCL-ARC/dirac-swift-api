"""Implements SWIFTsimIO data processing functionality on the server side.

This module calls SWIFTsimIO functions and creates numpy arrays from HDF5 files
read on the server.
"""
import json
from typing import Any

import h5py
import numpy as np
import numpy.typing as npt
from loguru import logger
from swiftsimio.accelerated import read_ranges_from_file


def get_dataset_alias_map():
    """Retrieve a dictionary mapping of aliases to file paths.

    Returns
    -------
        _type_: _description_
    """
    return {
        "downloaded_file": "/Users/hmoss/dirac-swift-api/sample_data/colibre_0023.hdf5",
        "sample_file": "/Users/hmoss/dirac-swift-api/sample_data/cosmo_volume_example.hdf5",
    }


class NumpyEncoder(json.JSONEncoder):
    """Enables JSON serialisation of numpy arrays."""

    def default(self, obj) -> Any:
        """Define default serialisation.

        Args:
            obj (_type_): Object to serialise
        Returns:
            Any: Serialised object
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class SWIFTProcessor:
    """Enables processing of HDF5 files on the server.

    Performs processing steps to return numpy arrays from HDF5 files as reuqested by users.
    """

    def __init__(self, data_alias_map: dict):
        """Class constructor.

        Args:
            data_alias_map (dict): Dictionary mapping dataset aliases to file paths.
        """
        self.data_alias_map = data_alias_map

    def retrieve_filename(self, dataset_alias: str | None) -> str | None:
        """Retrieve a full path to a file from an alias.

        Args:
            dataset_alias (str): Alias for a dataset

        Returns
        -------
            str | None : File path mapped to the alias
        """
        if dataset_alias:
            return self.data_alias_map.get(dataset_alias)
        return None

    def load_ndarray_from_json(self, json_array: str, data_type: str) -> npt.NDArray:
        """Convert JSON to a Numpy NDArray.

        Args:
            json_array (str): Numpy array as JSON
            data_type (str): Data type of elements in the original array

        Returns
        -------
            npt.NDArray: Numpy NDArray object
        """
        loaded_json = json.loads(json_array)
        return np.asarray(loaded_json, dtype=data_type)

    def generate_json_from_ndarray(self, array: npt.NDArray) -> dict[str, str]:
        """Serialise Numpy NDArrays to JSON.

        Args:
            array (npt.NDArray): Numpy NDArray representing a dataset

        Returns
        -------
            dict[str, str]:
                Dictionary containing serialised array, data type of array elements and byte order
        """
        json_array = json.dumps(array, cls=NumpyEncoder)
        data_type = array.dtype.str  # should preserve byte order
        return {
            "array": json_array,
            "dtype": data_type,
        }

    def get_array_masked(
        self,
        filename: str,
        field: str,
        mask_json: str,
        mask_data_type: str,
        mask_size: int,
        columns: None | np.lib.index_tricks.IndexExpression = None,
    ) -> npt.NDArray | None:
        """Retrieve a masked array.

        Args:
            filename (str): Path to HDF5 file
            field (str): Field to retrieve
            mask (None | npt.NDArray): Array mask
            mask_size (int): Size of array mask
            columns (None | np.lib.index_tricks.IndexExpression, optional):
                Selector for columns in the case of multidim arrays. Defaults to None.

        Returns
        -------
            npt.NDArray | None: Array with requested elements. Returns None if KeyError is raised.
        """
        mask = self.load_ndarray_from_json(mask_json, data_type=mask_data_type)

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
                    output_shape = mask_size  # type: ignore
                return read_ranges_from_file(
                    handle[field],
                    mask,
                    output_shape=output_shape,
                    output_type=output_type,
                    columns=columns,
                )
            except KeyError:
                logger.error(f"Could not read {field}")
                return None

    def get_array_unmasked(
        self,
        filename: str,
        field: str,
        columns: None | np.lib.index_tricks.IndexExpression = None,
    ) -> np.array:
        """Retrieve an unmasked array.

        Args:
            filename (str): Path to HDF5 file
            field (str): Field to retrieve
            columns (None | np.lib.index_tricks.IndexExpression, optional):
                Selector for columns in the case of multidim arrays. Defaults to None.

        Returns
        -------
            np.array | None: Array with requested elements. Returns None if KeyError is raised.
        """
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
                logger.error(f"Could not read {field}")
                return None
