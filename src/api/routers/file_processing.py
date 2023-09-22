"""Defines routes that return numpy arrays from HDF5 files."""
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from api.processing.data_processing import SWIFTProcessor, get_dataset_alias_map
from api.processing.masks import return_mask, return_mask_boxsize
from api.processing.metadata import create_swift_metadata
from api.processing.units import (
    RemoteSWIFTUnits,
    retrieve_swiftunits_dict,
    retrieve_units_json_compatible,
)

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


class SWIFTMaskedDataSpec(SWIFTBaseDataSpec):
    """Data required in each request for masked data.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    filename: str
    field: str
    mask_array_json: str
    mask_data_type: str | None = None
    mask_size: int
    columns: None | int = None


class SWIFTUnmaskedDataSpec(SWIFTBaseDataSpec):
    """Data required in each request for unmasked data.

    A Pydantic model to validate HTTP POST requests.

    Args:
        BaseModel (_type_): Pydantic BaseModel
    """

    filename: str | None = None
    field: str
    columns: None | int = None


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


@router.post("/mask_boxsize")
async def get_mask_boxsize(data_spec: SWIFTBaseDataSpec) -> dict[str, str]:
    """Retrieve mask dimensions.

    Args:
        data_spec (SWIFTBaseDataSpec): Basic data specification indicating filename or alias.

    Returns
    -------
        dict[str, str]: Dictionary containing boxsize array, data type and unyt units.
    """
    processor = SWIFTProcessor(dataset_map)
    file_path = get_file_path(data_spec, processor)

    return return_mask_boxsize(file_path)


@router.post("/filepath")
async def get_filepath_from_alias(data_spec: SWIFTBaseDataSpec) -> Path:
    """Retrieve full file path.

    Args:
        data_spec (SWIFTBaseDataSpec): Basic data specification indicating filename or alias.

    Returns
    -------
        Path: Path object displaying full file path on the server.
    """
    processor = SWIFTProcessor(dataset_map)
    return get_file_path(data_spec, processor)


@router.post("/mask")
async def get_mask(data_spec: SWIFTBaseDataSpec) -> bytes:
    """Retrieve SWIFTMask object.

    Args:
        data_spec (SWIFTBaseDataSpec): Basic data specification indicating filename or alias.

    Returns
    -------
        bytes: Pickled SWIFTMask object.
    """
    processor = SWIFTProcessor(dataset_map)
    file_path = get_file_path(data_spec, processor)

    return return_mask(file_path)


def get_file_path(data_spec: SWIFTBaseDataSpec, processor: SWIFTProcessor) -> Path:
    """Retrieve a file path from a data spec object.

    Args:
        data_spec (SWIFTBaseDataSpec): SWIFT minimal data spec object
        processor (SWIFTProcessor): SWIFTProcessor object.

    Raises
    ------
        SWIFTDataSpecException: HTTP 400 exception on no filename found.

    Returns
    -------
        Path: Path to requested file
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
    return Path(file_path)


@router.post("/masked_dataset")
async def get_masked_array_data(data_spec: SWIFTMaskedDataSpec) -> dict:
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

    file_path = str(get_file_path(data_spec, processor).resolve())

    if not data_spec.mask_array_json:
        raise SWIFTDataSpecException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mask information found. \
            Use the unmasked endpoint if requesting unmasked data.",
        )

    masked_array = processor.get_array_masked(
        file_path,
        data_spec.field,
        data_spec.mask_array_json,
        data_spec.mask_data_type,
        data_spec.mask_size,
        data_spec.columns,
    )

    return processor.generate_dict_from_ndarray(
        masked_array,
    )


@router.post("/unmasked_dataset")
async def get_unmasked_array_data(data_spec: SWIFTUnmaskedDataSpec) -> dict:
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

    file_path = str(get_file_path(data_spec, processor).resolve())

    unmasked_array = processor.get_array_unmasked(
        file_path,
        data_spec.field,
        data_spec.columns,
    )

    return processor.generate_dict_from_ndarray(
        unmasked_array,
    )


@router.post("/swiftmetadata")
async def retrieve_metadata(data_spec: SWIFTBaseDataSpec) -> dict:
    """Retrieve metadata from a file path.

    Args:
        data_spec (SWIFTBaseDataSpec): Base dataspec specifying file path or alias.

    Returns
    -------
        dict: Metadata for specified file
    """
    processor = SWIFTProcessor(dataset_map)
    file_path = str(get_file_path(data_spec, processor).resolve())
    units = retrieve_swiftunits_dict(file_path)

    swift_units = RemoteSWIFTUnits(units)

    serialised_metadata = create_swift_metadata(file_path, swift_units)

    return Response(content=serialised_metadata, media_type="application/octet-stream")


@router.post("/swiftunits")
async def retrieve_units(data_spec: SWIFTBaseDataSpec) -> dict:
    """Retrieve units for the specified file.

    Args:
        data_spec (SWIFTBaseDataSpec): Base dataspec specifying file path or alias.

    Returns
    -------
        dict: Unit data for specified file
    """
    processor = SWIFTProcessor(dataset_map)

    file_path = str(get_file_path(data_spec, processor).resolve())

    return retrieve_units_json_compatible(file_path)
