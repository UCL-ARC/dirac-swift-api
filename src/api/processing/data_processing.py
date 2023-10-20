"""Implements SWIFTsimIO data processing functionality on the server side.

This module calls SWIFTsimIO functions and creates numpy arrays from HDF5 files
read on the server. It uses code available under the GNU General Public License
version 3 from the SWIFTsimIO library https://github.com/SWIFTSIM/swiftsimio/.

"""
import json

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
        "downloaded_file": "/path/to/downloaded_file",
        "sample_file": "/path/to/sample_file",
    }


class SWIFTProcessorError(Exception):
    """Custom exception for data aprocessing errors."""


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
            str: File path mapped to the alias
        """
        if dataset_alias:
            mapped_filename = self.data_alias_map.get(dataset_alias)

            if not mapped_filename:
                msg = "Dataset alias not found in dataset map."
                raise (SWIFTProcessorError(msg))

            return mapped_filename
        return None

    @staticmethod
    def load_ndarray_from_json(
        json_array: str,
        data_type: str | None,
    ) -> npt.NDArray:
        """Convert JSON to a Numpy NDArray.

        Args:
            json_array (str): Numpy array as JSON
            data_type (str): Data type of elements in the original array

        Returns
        -------
            npt.NDArray: Numpy NDArray object
        """
        loaded_json = json.loads(json_array)

        try:
            return np.asarray(loaded_json, dtype=data_type)
        except TypeError as dtype_error:
            message = f"Invalid data type provided for conversion to numpy array. {dtype_error}"
            raise (SWIFTProcessorError(message)) from dtype_error
        except ValueError as array_value_error:
            message = f"Invalid array data for numpy.asarray(). {array_value_error}"
            raise (SWIFTProcessorError(message)) from array_value_error

    @staticmethod
    def generate_dict_from_ndarray(array: npt.NDArray) -> dict[str, str]:
        """Convert numpy-based arrays to JSON-serialisable objects.

        Args:
            array (npt.NDArray): Numpy NDArray representing a dataset

        Returns
        -------
            dict[str, str]:
                Dictionary containing serialised array, data type of array elements and byte order
        """
        data_type = array.dtype.str  # should preserve byte order
        return {
            "array": array.tolist(),
            "dtype": data_type,
        }

    @staticmethod
    def get_array_masked(
        filename: str,
        field: str,
        mask_json: str | None,
        mask_data_type: str | None,
        mask_size: int,
        columns: None | np.lib.index_tricks.IndexExpression = None,
    ) -> npt.NDArray | None:
        """Retrieve a masked array.

        Args:
            filename (str): Path to HDF5 file
            field (str): Field path to retrieve
            mask_json (None | str): String representation of array mask
            mask_data_type (str | None): Optionally include the original mask array dtype
            mask_size (int): Size of array mask
            columns (None | np.lib.index_tricks.IndexExpression, optional):
                Selector for columns in the case of multidim arrays. Defaults to None.

        Returns
        -------
            npt.NDArray | None: Array with requested elements. Returns None if KeyError is raised.
        """
        if not mask_json:
            msg = "No mask provided!"
            raise SWIFTProcessorError(msg)
        mask = SWIFTProcessor.load_ndarray_from_json(
            mask_json,
            data_type=mask_data_type,
        )

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
                message = f"Field {field} not found in {filename}."
                raise SWIFTProcessorError(message) from KeyError

    @staticmethod
    def get_array_unmasked(
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
