"""Defines routes that return numpy arrays from HDF5 files."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from api.processing.read_ranges import SWIFTProcessor, get_dataset_alias_map

router = APIRouter()

dataset_map = get_dataset_alias_map()


class SWIFTDataSpec(BaseModel):
    """Data required in each request.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    alias: str | None = None
    filename: str | None = None
    field: str
    mask: None | str = None
    mask_size: None | int = None
    columns: None | list[int] = None


class SWIFTDataSpecException(HTTPException):
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


@router.post("/masked_dataset")
async def get_masked_array_data(data_spec: SWIFTDataSpec) -> dict[str, str]:
    """Retrieve a masked array from a dataset.

    Applies masking to an array generated from the HDF5 file
    and returns the resulting array as JSON.

    Args:
        data_spec (SWIFTDataSpec):
            Dataset information required in POST request

    Raises
    ------
        SWIFTDataSpecException:
            Exceptions raised for incorrectly formatted requests

    Returns
    -------
        dict[str, str]:
            Numpy ndarray formatted as JSON. The resulting dictionary
            contains the array and the original data type.
    """
    processor = SWIFTProcessor(dataset_map)

    file_path = None
    if data_spec.filename:
        file_path = data_spec.filename
    else:
        file_path = processor.retrieve_filename(data_spec.alias)
    if file_path is None:
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SWIFT filename or file alias not found.",
        )

    if not data_spec.mask or not data_spec.mask_size:
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mask information found. \
            Use the unmasked endpoint if requesting unmasked data.",
        )

    masked_array = processor.get_array_masked(
        file_path,
        data_spec.field,
        data_spec.mask,
        data_spec.mask_size,
        data_spec.columns,
    )

    return processor.generate_json_from_ndarray(
        masked_array,
    )


@router.post("/unmasked_dataset")
async def get_unmasked_array_data(data_spec: SWIFTDataSpec) -> dict[str, str]:
    """Retrieve an unmasked array from a dataset.

    Returns the array generated from the HDF5 file
    using the data specification provided.

    Args:
        data_spec (SWIFTDataSpec):
            Dataset information required in POST request

    Raises
    ------
        SWIFTDataSpecException:
            Exceptions raised for incorrectly formatted requests

    Returns
    -------
        dict[str, str]:
            Numpy ndarray formatted as JSON. The resulting dictionary
            contains the array and the original data type.
    """
    processor = SWIFTProcessor(dataset_map)

    file_path = None
    if data_spec.filename:
        file_path = data_spec.filename
    else:
        file_path = processor.retrieve_filename(data_spec.alias)
    if file_path is None:
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SWIFT filename or file alias not found.",
        )

    unmasked_array = processor.get_array_unmasked(
        file_path,
        data_spec.field,
        data_spec.columns,
    )

    return processor.generate_json_from_ndarray(
        unmasked_array,
    )
