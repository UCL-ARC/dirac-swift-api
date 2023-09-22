import json
from datetime import datetime
from pathlib import Path
from pickle import UnpicklingError

import cloudpickle
import numpy as np
import pytest
from api.processing.metadata import (
    RemoteSWIFTMetadataError,
    SWIFTMetadataEncoder,
    create_swift_metadata,
    create_swift_metadata_dict,
)
from api.processing.units import RemoteSWIFTUnits, create_unyt_quantities
from swiftsimio.reader import MassTable
from unyt import unyt_quantity


def test_swift_metadata_json_dump_no_encoder_failure():
    test_swift_units = RemoteSWIFTUnits(
        {
            "units": {
                "mass": "1e+10 kg",
            },
            "mass": "1.e+10 Msun",
            "length": "1. Mpc",
            "time": "977.79 Gyr",
            "current": "1. statA",
            "temperature": "1. K",
        },
    )
    test_mass_table = MassTable(np.asarray([1, 2, 3]), "kg")
    swift_metadata = {
        "test unit quantity": unyt_quantity(5, "Mpc"),
        "test ndarray": np.asarray([1, 2, 3]),
        "test bytestring": b"test string",
        "test mass table": test_mass_table,
        "test swift units": test_swift_units,
        "test numpy 32-bit int": np.int32(5),
        "test numpy 64-bit int": np.int64(4),
        "test datetime": datetime.fromisoformat("2023-09-10T12:00:00.550000"),
    }

    with pytest.raises(TypeError):
        json.dumps(swift_metadata)


def test_swift_metadata_json_dump_with_encoder_success():
    test_swift_units = RemoteSWIFTUnits(
        {
            "units": {
                "mass": "1e+10 kg",
            },
            "mass": "1.e+10 Msun",
            "length": "1. Mpc",
            "time": "977.79 Gyr",
            "current": "1. statA",
            "temperature": "1. K",
        },
    )
    test_mass_table = MassTable(np.asarray([1, 2, 3]), "kg")
    swift_metadata = {
        "test unit quantity": unyt_quantity(5, "Mpc"),
        "test ndarray": np.asarray([1, 2, 3]),
        "test bytestring": np.bytes_("test string"),
        "test mass table": test_mass_table,
        "test swift units": test_swift_units,
        "test numpy 32-bit int": np.int32(5),
        "test numpy 64-bit int": np.int64(4),
        "test datetime": datetime.fromisoformat("2023-09-10T12:00:00.550000"),
    }

    expected_datetime = "2023-09-10T12:00:00.550000"

    json_string = json.dumps(swift_metadata, cls=SWIFTMetadataEncoder)
    output_dict = json.loads(json_string)
    assert expected_datetime == output_dict["test datetime"]


def test_create_swift_metadata_dict_failure_serialisation(
    mocker,
    template_swift_data_path: Path,
):
    test_filename = str(template_swift_data_path.resolve())
    test_swift_units_dict = {
        "units": {
            "mass": "1e+10 kg",
        },
        "mass": "1.e+10 Msun",
        "length": "1. Mpc",
        "time": "977.79 Gyr",
        "current": "1. statA",
        "temperature": "1. K",
    }

    test_unyt_quantity_dict = create_unyt_quantities(test_swift_units_dict)

    test_swift_units = RemoteSWIFTUnits(test_unyt_quantity_dict)

    mock_json_reproc = mocker.patch(
        "api.processing.metadata.reprocess_json",
    )

    mock_json_reproc.side_effect = TypeError("No nice way of serialising things found!")

    with pytest.raises(RemoteSWIFTMetadataError) as error:
        create_swift_metadata_dict(test_filename, test_swift_units)

    assert "No nice way of serialising things found!" in str(error.value)


def test_create_swift_metadata_dict_success(template_swift_data_path: Path):
    test_filename = str(template_swift_data_path.resolve())
    test_swift_units_dict = {
        "units": {
            "mass": "1e+10 kg",
        },
        "mass": "1.e+10 Msun",
        "length": "1. Mpc",
        "time": "977.79 Gyr",
        "current": "1. statA",
        "temperature": "1. K",
    }

    test_unyt_quantity_dict = create_unyt_quantities(test_swift_units_dict)

    test_swift_units = RemoteSWIFTUnits(test_unyt_quantity_dict)

    result = create_swift_metadata_dict(test_filename, test_swift_units)
    expected_black_holes = 150
    assert result["n_black_holes"] == expected_black_holes


def test_create_swift_metadata_success(template_swift_data_path: Path):
    test_filename = str(template_swift_data_path.resolve())
    test_swift_unit_dict = {
        "units": {
            "mass": "1e+10 kg",
        },
        "mass": "1.e+10 Msun",
        "length": "1. Mpc",
        "time": "977.79 Gyr",
        "current": "1. statA",
        "temperature": "1. K",
    }

    test_unyt_quantity_dict = create_unyt_quantities(test_swift_unit_dict)

    test_swift_units = RemoteSWIFTUnits(test_unyt_quantity_dict)

    metadata_bytes = create_swift_metadata(test_filename, test_swift_units)
    assert isinstance(metadata_bytes, bytes)

    metadata = cloudpickle.loads(metadata_bytes)
    expected_black_holes = 150
    assert metadata.n_black_holes == expected_black_holes


def test_create_swift_metadata_failure_unpickle_truncated(
    template_swift_data_path: Path,
):
    test_filename = str(template_swift_data_path.resolve())
    test_swift_unit_dict = {
        "units": {
            "mass": "1e+10 kg",
        },
        "mass": "1.e+10 Msun",
        "length": "1. Mpc",
        "time": "977.79 Gyr",
        "current": "1. statA",
        "temperature": "1. K",
    }

    test_unyt_quantity_dict = create_unyt_quantities(test_swift_unit_dict)

    test_swift_units = RemoteSWIFTUnits(test_unyt_quantity_dict)

    metadata_bytes = create_swift_metadata(test_filename, test_swift_units)
    assert isinstance(metadata_bytes, bytes)

    with pytest.raises(UnpicklingError) as error:
        cloudpickle.loads(metadata_bytes[:-1])

    assert "data was truncated" in error.value.__str__()
