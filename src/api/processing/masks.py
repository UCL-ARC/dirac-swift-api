"""Handle mask objects on the server side and return to clients."""
from pathlib import Path

import cloudpickle
import swiftsimio as sw

from api.processing.data_processing import SWIFTProcessor, get_dataset_alias_map


def return_mask_boxsize(filename: Path) -> dict[str, str]:
    """Retrieve the boxsize object from an object mask.

    Args:
        filename (str): Path to file on disk

    Returns
    -------
        dict[str, str]: Dictionary containing boxsize array, data type and unyt units.
    """
    processor = SWIFTProcessor(get_dataset_alias_map())
    mask = sw.mask(str(filename.resolve()))
    boxsize = mask.metadata.boxsize

    payload = processor.generate_dict_from_ndarray(boxsize)
    payload.update({"units": str(boxsize.units)})
    return payload


def return_mask(filename: Path) -> dict[str, str]:
    """Retrieve the boxsize object from an object mask.

    Args:
        filename (str): Path to file on disk

    Returns
    -------
        dict[str, str]: Dictionary containing boxsize array, data type and unyt units.
    """
    SWIFTProcessor(get_dataset_alias_map())
    mask = sw.mask(str(filename.resolve()))

    return cloudpickle.dumps(mask)
