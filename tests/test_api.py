from pathlib import Path

import cloudpickle
import pytest
import swiftsimio as sw
from api.main import app
from api.processing.data_processing import SWIFTProcessor
from api.routers.file_processing import (
    SWIFTBaseDataSpec,
    SWIFTDataSpecException,
    get_file_path,
)
from fastapi import status
from fastapi.testclient import TestClient
from swiftsimio.reader import SWIFTMetadata
from unyt import unyt_array

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping": "pong"}


def test_get_mask_boxsize_success(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }
    expected_array = [142.2475106685633, 142.2475106685633, 142.2475106685633]

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/mask_boxsize",
        json=payload,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["array"] == expected_array


def test_get_mask_boxsize_failure(mock_auth_client_success_jwt_decode):
    payload = {
        "data_spec": {
            "filename": "/an/incorrect/file/path",
        },
    }
    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/mask_boxsize",
        json=payload,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_filepath_from_alias_fails_if_not_str(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": template_swift_data_path,
        },
    }

    with pytest.raises(TypeError) as error:
        mock_auth_client_success_jwt_decode.post("/swiftdata/filepath", json=payload)

    assert "not JSON serializable" in str(error.value)


def test_get_filepath_from_alias_success(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/filepath",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == str(template_swift_data_path)


def test_get_filepath_from_alias_failure_no_alias_found(
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "alias": "An imaginary dataset",
        },
    }
    expected_error_message = "SWIFT dataset alias not found in dataset map."

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/filepath",
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == expected_error_message


def test_get_mask(template_swift_data_path, mock_auth_client_success_jwt_decode):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }

    expected_mask_cell_size = unyt_array([17.78093883, 17.78093883, 17.78093883], "Mpc")

    response = mock_auth_client_success_jwt_decode.post("/swiftdata/mask", json=payload)

    assert response.status_code == status.HTTP_200_OK

    mask_object = cloudpickle.loads(response.content)
    assert isinstance(mask_object, sw.SWIFTMask)
    assert mask_object.__dict__["cell_size"].all() == expected_mask_cell_size.all()


def test_get_file_path_success_alias(template_swift_data_path):
    data_alias_map = {
        "test_dataset": str(template_swift_data_path),
    }
    data_spec = SWIFTBaseDataSpec(alias="test_dataset", filename=None)

    processor = SWIFTProcessor(data_alias_map)

    file_path = get_file_path(data_spec, processor)

    assert isinstance(file_path, Path)
    assert str(file_path) == data_alias_map["test_dataset"]
    assert file_path.exists()


def test_get_file_path_success_filename(template_swift_data_path):
    data_alias_map = {
        "test_dataset": "A non-existent file",
    }
    data_spec = SWIFTBaseDataSpec(alias=None, filename=str(template_swift_data_path))

    processor = SWIFTProcessor(data_alias_map)

    file_path = get_file_path(data_spec, processor)

    assert isinstance(file_path, Path)
    assert str(file_path) == str(template_swift_data_path)
    assert file_path.exists()


def test_get_file_path_failure_alias_not_found_in_map(template_swift_data_path):
    data_alias_map = {
        "test_dataset": template_swift_data_path,
    }
    data_spec = SWIFTBaseDataSpec(alias="non_existent_dataset", filename=None)

    processor = SWIFTProcessor(data_alias_map)

    with pytest.raises(SWIFTDataSpecException) as error:
        get_file_path(data_spec, processor)

    assert "alias not found in dataset" in error.value.detail


def test_get_file_path_failure_filename_and_alias_not_provided():
    data_alias_map = {
        "test_data": "/a/nonexistent/file/path.hdf5",
    }
    data_spec = SWIFTBaseDataSpec(alias=None, filename=None)

    processor = SWIFTProcessor(data_alias_map)

    with pytest.raises(SWIFTDataSpecException) as error:
        get_file_path(data_spec, processor)

    assert "filename or file alias not found" in error.value.detail


def test_get_file_path_failure_bad_filename_provided():
    data_alias_map = {
        "test_data": "/a/nonexistent/file/path.hdf5",
    }
    data_spec = SWIFTBaseDataSpec(alias=None, filename=data_alias_map["test_data"])

    processor = SWIFTProcessor(data_alias_map)

    with pytest.raises(SWIFTDataSpecException) as error:
        get_file_path(data_spec, processor)

    assert "filename not found at the provided path" in error.value.detail


def test_get_masked_array_data_fails_missing_all_required_info(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    # Test if required info beyond the basic spec is missing

    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }

    expected_missing_fields = 3
    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Three compulsory non-filename fields
    assert len(response.json()["detail"]) == expected_missing_fields


def test_get_masked_array_data_fails_missing_field(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "mask_array_json": "[[337.0], [234.1, 233.1], [355.1]]",
            "mask_size": 3,
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert len(response.json()["detail"]) == 1
    assert response.json()["detail"][0]["loc"][-1] == "field"


def test_get_masked_array_data_fails_missing_mask_array(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "gas",
            "mask_size": 3,
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert len(response.json()["detail"]) == 1
    assert response.json()["detail"][0]["loc"][-1] == "mask_array_json"


def test_get_masked_array_data_fails_missing_mask_size(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "gas",
            "mask_array_json": "[[337.0], [234.1, 233.1], [355.1]]",
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert len(response.json()["detail"]) == 1
    assert response.json()["detail"][0]["loc"][-1] == "mask_size"


def test_get_masked_array_data_fails_with_invalid_field_name(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "a_made_up/field",
            "mask_array_json": "[[337.0], [234.1], [355.1]]",
            "mask_size": 3,
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    field = payload["data_spec"]["field"]
    assert f"{field} not found" in response.json()["detail"]


def test_get_masked_array_data_spatial_success(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "PartType0/Coordinates",
            "mask_array_json": "[[0, 334]]",
            "mask_size": 334,
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/masked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["array"], list)
    assert len(response.json()["array"]) == payload["data_spec"]["mask_size"]


def test_get_unmasked_array_data_success_no_columns(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "PartType0/Coordinates",
        },
    }
    expected_array_length = 32382
    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/unmasked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["array"]) == expected_array_length


def test_get_unmasked_array_data_success_columns(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
            "field": "PartType0/Coordinates",
            "columns": 0,
        },
    }
    expected_array_length = 32382
    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/unmasked_dataset",
        json=payload,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["array"]) == expected_array_length


def test_retrieve_metadata(
    template_swift_data_path,
    mock_auth_client_success_jwt_decode,
):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }

    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/metadata",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    retrieved_metadata_object = cloudpickle.loads(response.content)

    assert isinstance(retrieved_metadata_object, SWIFTMetadata)


def test_retrieve_units(template_swift_data_path, mock_auth_client_success_jwt_decode):
    payload = {
        "data_spec": {
            "filename": str(template_swift_data_path),
        },
    }

    expected_time = "977.79 Gyr"
    response = mock_auth_client_success_jwt_decode.post(
        "/swiftdata/units_dict",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK

    assert isinstance(response.json(), dict)
    assert response.json()["time"] == expected_time
