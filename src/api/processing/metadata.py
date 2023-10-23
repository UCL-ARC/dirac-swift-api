"""Perform server side metadata processing."""
import json
from datetime import datetime
from functools import lru_cache
from typing import Any

import cloudpickle
import numpy as np
from swiftsimio.reader import (
    MassTable,
    SWIFTMetadata,
    SWIFTParticleTypeMetadata,
    SWIFTUnits,
)
from unyt import unyt_quantity

from api.processing.units import RemoteSWIFTUnits


class RemoteSWIFTMetadataError(Exception):
    """Custom error class for metadata serialisation."""


class SWIFTMetadataEncoder(json.JSONEncoder):
    """Enable JSON serialisation of numpy arrays."""

    def default(self, obj) -> Any:
        """Define default serialisation.

        Args:
            obj (_type_): Object to serialise
        Returns:
            Any: Serialised object
        """
        if isinstance(obj, unyt_quantity):
            return obj.to_string()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bytes_):
            return obj.decode("UTF-8")
        if isinstance(obj, RemoteSWIFTUnits):
            return repr(obj.__dict__)
        if isinstance(obj, MassTable):
            return repr(obj)
        if isinstance(obj, SWIFTParticleTypeMetadata):
            return repr(obj)
        if isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


@lru_cache(maxsize=128)
def create_swift_metadata(filename: str, units: RemoteSWIFTUnits | SWIFTUnits) -> bytes:
    """Return a SWIFTMetadata object, serialised with pickle.

    Args:
        filename (str): File path of specified HDF5 file
        units (Union[RemoteSWIFTUnits, SWIFTUnits]): Units object.

    Raises
    ------
        RemoteSWIFTMetadataError: Raised in case of failed JSON serialisation.

    Returns
    -------
        bytes: Pickled SWIFTMetadata object
    """

    metadata = SWIFTMetadata(filename, units)
    if hasattr(metadata.units, "_handle"):
        metadata.units._handle = None  # do not serialize file handle

    try:
        return cloudpickle.dumps(metadata)

    except Exception as error:  # noqa: BLE001
        message = f"Error serialising metadata: {error!s}"
        raise RemoteSWIFTMetadataError(message) from error


def reprocess_json(metadata_dictionary: dict, encoder: type[json.JSONEncoder]):
    """Encode and decode a dictionary to JSON to ensure correct formatting.

    Args:
        metadata_dictionary (dict): Dictionary representation of SWIFT Metadata
        encoder (json.JSONEncoder): Encoder object to dictate serialisation
    """
    json_metadata = json.dumps(metadata_dictionary, cls=encoder)
    return json.loads(json_metadata)


def create_swift_metadata_dict(filename: str, units: RemoteSWIFTUnits) -> dict:
    """Create JSON-serialisable metadata dictionary.

    Args:
        filename (str): File path of specified HDF5 file
        units (RemoteSWIFTUnits): Units object

    Raises
    ------
        RemoteSWIFTMetadataError: Raised in case of failed JSON serialisation.

    Returns
    -------
        dict: Dictionary containg metadata.
    """
    metadata = SWIFTMetadata(filename, units)

    metadata_dict = metadata.__dict__

    try:
        return reprocess_json(metadata_dict, SWIFTMetadataEncoder)
    except TypeError as type_error:
        message = f"Error serialising JSON: {type_error}"
        raise RemoteSWIFTMetadataError(message) from type_error
