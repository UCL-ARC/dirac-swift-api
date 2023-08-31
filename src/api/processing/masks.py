"""Handle mask objects on the server side and return to clients."""
import swiftsimio as sw

from api.processing.data_processing import SWIFTProcessor, get_dataset_alias_map


def return_mask_boxsize(filename: str) -> dict[str, str]:
    """Retrieve the boxsize object from an object mask.

    Args:
        filename (str): Path to file on disk

    Returns
    -------
        dict[str, str]: Dictionary containing boxsize array, data type and unyt units.
    """
    processor = SWIFTProcessor(get_dataset_alias_map())
    mask = sw.mask(filename)
    boxsize = mask.metadata.boxsize

    boxsize_array = boxsize.value  # type: npt.NDArray
    boxsize_units = str(boxsize.units)

    array_json = processor.generate_json_from_ndarray(boxsize_array)

    array_json.update({"units": str(boxsize_units)})

    return array_json
