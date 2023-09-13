from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


@pytest.fixture()
def template_swift_data_path(data_path) -> Path:
    """
    Return a Path object representing the sample swift data file linked from the SWIFTsimIO docs.

    File available http://virgodb.cosma.dur.ac.uk/swift-webstorage/IOExamples/cosmo_volume_example.hdf5

    """
    return data_path / "cosmo_volume_example.hdf5"
