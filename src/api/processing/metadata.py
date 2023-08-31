from swiftsimio.reader import SWIFTMetadata, RemoteSWIFTUnits, MassTable, SWIFTParticleTypeMetadata
from typing import Any
import json
import numpy as np
from unyt import unyt_quantity
from datetime import datetime

class RemoteSWIFTMetadataException(Exception):
    pass

class SWIFTMetadataEncoder(json.JSONEncoder):
    """Enables JSON serialisation of numpy arrays."""

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
            return repr(obj)
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


def create_metadata(filename: str, units: RemoteSWIFTUnits):

    metadata = SWIFTMetadata(filename, units)

    metadata_dict = metadata.__dict__

    try:
        # Enforce JSON serialisability in this step
        json_metadata = json.dumps(metadata_dict, cls=SWIFTMetadataEncoder)
        metadata_object = json.loads(json_metadata)
        return metadata_object
    except TypeError as error:
        message = f"Error serialising JSON: {str(error)}"
        raise RemoteSWIFTMetadataException(message) from error

