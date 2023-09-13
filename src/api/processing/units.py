"""Handle server-side unit calculation and conversion to JSON."""
import json
from typing import Any

from fastapi import HTTPException, status
from swiftsimio.reader import SWIFTUnits
from unyt import unyt_quantity


class RemoteSWIFTUnits:
    """Create SWIFTUnits-type objects.

    Converts dictionaries of strings to dictionaries of type `unyt_quantity`
    matching the SWIFTUnits type.
    """

    def __init__(self, unit_dict: dict | None = None):
        """Class constructor.

        Args:
            unit_dict (_type_, optional): Optional dictionary of strings. Defaults to None.
        """
        if unit_dict is not None:
            for key, value in unit_dict.items():
                setattr(self, key, unyt_quantity.from_string(value))
                if isinstance(unit_dict[key], dict):
                    for nested_key, nested_value in unit_dict[key].items():
                        setattr(self, nested_key, nested_value)


class SWIFTUnytException(HTTPException):
    """Custom exception for incorrectly formatted POSTs.

    Args:
        HTTPException (_type_): HTTPException with status code.
    """

    def __init__(self, status_code: int, detail: str | None = None):
        """Class constructor.

        Args:
            status_code (int): HTTP response status code
            detail (str | None, optional):
                Additional exception details. Defaults to None.
        """
        if not detail:
            detail = "Error validating SWIFT particle dataset specification provided."
        super().__init__(status_code, detail=detail)


class UnytEncoder(json.JSONEncoder):
    """Enables JSON serialisation of unyt objects."""

    def default(self, obj) -> Any:
        """Define default serialisation.

        Args:
            obj (_type_): Object to serialise
        Returns:
            Any: Serialised object
        """
        if isinstance(obj, unyt_quantity):
            return obj.to_string()
        return json.JSONEncoder.default(self, obj)


def convert_swift_units_dict_types(swift_units_dict: dict) -> dict:
    """Convert unyt quantities to strings within a units dictionary.

    Intended to aid JSON serialisation.

    Args:
        swift_units_dict (SWIFTUnits):
            A dictionary representation of a SWIFTUnits object containing unit information.

    Raises
    ------
        SWIFTUnytException: Custom exception raised in case of conversion error.

    Returns
    -------
        dict: Dictionary representing units using strings.
    """
    try:
        for key in swift_units_dict:
            if isinstance(swift_units_dict[key], unyt_quantity):
                swift_units_dict[key] = swift_units_dict[key].to_string()
            for unit in swift_units_dict["units"]:
                if isinstance(swift_units_dict["units"][unit], unyt_quantity):
                    swift_units_dict["units"][unit] = swift_units_dict["units"][
                        unit
                    ].to_string()
    except KeyError as error:
        raise SWIFTUnytException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return swift_units_dict


def retrieve_units_json_compatible(filename: str) -> dict:
    """Retrieve a JSON-serialisable units dictionary.

    Args:
        filename (str): Path to HDF5 file.

    Returns
    -------
        dict: JSON-serialisable units dictionary.
    """
    units = SWIFTUnits(filename)
    return convert_swift_units_dict_types(units)


def retrieve_swiftunits_dict(filename: str) -> dict:
    """Return a SWIFTUnits dictionary from HDF5 file.

    Args:
        filename (str): Path to HDF5 file.

    Returns
    -------
        dict: Dictionary representation of SWIFTUnits object.
    """
    return SWIFTUnits(filename).__dict__


def create_unyt_quantities(swift_unit_dict: dict) -> dict[str, Any]:
    """Recreate unyt quantities within a dictionary of strings.

    Args:
        swift_unit_dict (dict): Unit dictionary containing string values.

    Raises
    ------
        SWIFTUnytException: Exception raised in case of conversion error.

    Returns
    -------
        dict[str, Any]: Dictionary containg `unyt_quantity`-type values.
    """
    excluded_fields = ["filename", "units"]
    try:
        swift_unit_dict["units"] = {
            key: unyt_quantity.from_string(value)
            for key, value in swift_unit_dict["units"].items()
        }
        swift_unit_dict = {
            key: (
                unyt_quantity.from_string(value)
                if key not in excluded_fields
                else value
            )
            for key, value in swift_unit_dict.items()
        }
    except KeyError as error:
        raise SWIFTUnytException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return swift_unit_dict
