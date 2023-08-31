import json
from typing import Any

from fastapi import HTTPException, status
from swiftsimio.reader import SWIFTUnits
from unyt import unyt_quantity


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


def convert_swift_units_to_dict(swift_units: SWIFTUnits) -> str:
    swift_units_dict = swift_units.__dict__

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
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        ) from error

    return swift_units_dict


def retrieve_units_from_file(filename: str) -> str:
    units = SWIFTUnits(filename)
    units_dict = convert_swift_units_to_dict(units)
    return json.dumps(units_dict)


def create_unyt_quantities_from_json(input_json: str) -> dict[str, Any]:
    swift_unit_dict = json.loads(input_json)

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
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        ) from error

    return swift_unit_dict
