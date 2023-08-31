"""Defines routes that return numpy arrays from HDF5 files."""
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.processing.data_processing import SWIFTProcessor, get_dataset_alias_map
from api.processing.masks import return_mask_boxsize
from api.processing.units import retrieve_units_from_file

router = APIRouter()

dataset_map = get_dataset_alias_map()


class SWIFTBaseDataSpec(BaseModel):
    """Data required in each POST request.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    alias: str | None = None
    filename: str | None = None


class SWIFTMaskedDataSpec(BaseModel):
    """Data required in each request for masked data.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    alias: str | None = None
    filename: str | None = None
    field: str
    boxsize_coefficients: list[float] = None
    columns: None | list[int] = None


class SWIFTUnmaskedDataSpec(BaseModel):
    """Data required in each request for unmasked data.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    alias: str | None = None
    filename: str | None = None
    field: str
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


@router.post("/mask")
async def get_unmasked_array_data(data_spec: SWIFTBaseDataSpec) -> dict[str, str]:
    processor = SWIFTProcessor(dataset_map)
    file_path = get_file_path(data_spec, processor)

    boxsize = return_mask_boxsize(file_path)

    return boxsize


def get_file_path(data_spec: SWIFTBaseDataSpec, processor: SWIFTProcessor) -> str:
    """Retrieve a file path from a data spec object
    Args:
        data_spec (SWIFTBaseDataSpec): SWIFT minimal data spec object
        processor (SWIFTProcessor): SWIFTProcessor object.

    Raises
    ------
        SWIFTDataSpecException: HTTP 400 exception on no filename found.

    Returns
    -------
        str: Path to requested file
    """
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
    if not Path(file_path).exists():
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SWIFT filename not found at the provided path: {file_path}.",
        )
    return file_path


@router.post("/masked_dataset")
async def get_masked_array_data(data_spec: SWIFTMaskedDataSpec) -> dict[str, str]:
    """Retrieve a masked array from a dataset.

    Applies masking to an array generated from the HDF5 file
    and returns the resulting array as JSON.

    Args:
        data_spec (SWIFTMaskedDataSpec):
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

    file_path = get_file_path(data_spec, processor)

    if not data_spec.boxsize_coefficients:
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mask information found. \
            Use the unmasked endpoint if requesting unmasked data.",
        )

    masked_array = processor.get_array_masked(
        file_path,
        data_spec.field,
        data_spec.boxsize_coefficients,
        data_spec.columns,
    )

    return processor.generate_json_from_ndarray(
        masked_array,
    )


@router.post("/unmasked_dataset")
async def get_unmasked_array_data(data_spec: SWIFTUnmaskedDataSpec) -> dict[str, str]:
    """Retrieve an unmasked array from a dataset.

    Returns the array generated from the HDF5 file
    using the data specification provided.

    Args:
        data_spec (SWIFTUnmaskedDataSpec):
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

    file_path = get_file_path(data_spec, processor)

    unmasked_array = processor.get_array_unmasked(
        file_path,
        data_spec.field,
        data_spec.columns,
    )

    return processor.generate_json_from_ndarray(
        unmasked_array,
    )


@router.get("/swiftmetadata")
async def retrieve_metadata():
    pass


@router.post("/swiftunits")
async def retrieve_units(data_spec: SWIFTBaseDataSpec) -> dict:
    processor = SWIFTProcessor(dataset_map)

    file_path = get_file_path(data_spec, processor)

    return JSONResponse(retrieve_units_from_file(file_path))
