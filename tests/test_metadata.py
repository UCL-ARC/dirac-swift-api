import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from api.processing.metadata import (
    RemoteSWIFTMetadataError,
    SWIFTMetadataEncoder,
    create_metadata,
)
from api.processing.units import RemoteSWIFTUnits
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


def test_create_metadata_success(template_swift_data_path: Path):
    test_filename = str(template_swift_data_path.resolve())
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

    metadata_dict = create_metadata(test_filename, test_swift_units)
    assert isinstance(metadata_dict, dict)
    assert metadata_dict["time"] == "0.014035469190861152 977.79*Gyr"


def test_create_metadata_failure_serialisation(mocker, template_swift_data_path: Path):
    test_filename = str(template_swift_data_path.resolve())
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

    with mocker.patch(
        "json.dumps",
        side_effect=TypeError("No nice way of serialising!"),
    ), pytest.raises(RemoteSWIFTMetadataError):
        create_metadata(test_filename, test_swift_units)
