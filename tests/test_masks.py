from pathlib import Path

import cloudpickle
import numpy as np
import swiftsimio as sw
from api.processing.masks import return_mask, return_mask_boxsize
from unyt import Unit


def test_return_mask_boxsize(template_swift_data_path: Path):
    expected_array = [142.2475106685633, 142.2475106685633, 142.2475106685633]
    expected_dtype = np.float64
    expected_units = Unit("Mpc")

    boxsize_dict = return_mask_boxsize(template_swift_data_path)
    boxsize_numpy_array = np.asarray(boxsize_dict["array"], dtype=boxsize_dict["dtype"])

    assert isinstance(boxsize_dict, dict)
    assert boxsize_dict["array"] == expected_array
    assert boxsize_numpy_array.dtype == expected_dtype
    assert Unit(boxsize_dict["units"]) == expected_units


def test_return_mask_success(template_swift_data_path: Path):
    canonical_mask = sw.mask(str(template_swift_data_path))

    test_mask_bytes = return_mask(template_swift_data_path)
    test_mask = cloudpickle.loads(test_mask_bytes)

    assert canonical_mask.metadata.named_columns == test_mask.metadata.named_columns
