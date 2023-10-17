from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


@pytest.fixture()
def template_swift_data_path(data_path) -> Path:
    """
    Return a Path object representing sample swift data.

    The data is a subset of the file linked from the SWIFTsimIO docs.

    File available:
    http://virgodb.cosma.dur.ac.uk/swift-webstorage/IOExamples/cosmo_volume_example.hdf5

    """
    return data_path / "test_subset.hdf5"


@pytest.fixture()
def template_dataset_alias_map(template_swift_data_path) -> dict:
    """Return a dictionary mapping a dataset alias to the test file."""
    return {
        "test_file": str(template_swift_data_path),
    }
