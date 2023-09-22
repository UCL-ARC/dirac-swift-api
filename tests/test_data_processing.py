import json
from pathlib import Path

import numpy as np
import pytest
from api.processing.data_processing import SWIFTProcessor, SWIFTProcessorError


def test_retrieve_filename_failure(template_dataset_alias_map):
    processor = SWIFTProcessor(template_dataset_alias_map)

    with pytest.raises(SWIFTProcessorError):
        processor.retrieve_filename("a_nonexistant_alias")


def test_retrieve_filename_success(template_dataset_alias_map):
    processor = SWIFTProcessor(template_dataset_alias_map)

    expected_filename = "cosmo_volume_example.hdf5"
    filename = processor.retrieve_filename("test_file")

    assert Path(filename).name == expected_filename  # type: ignore


def test_load_ndarray_from_json_success():
    test_mask_array_json = "[[0, 334], [334, 734], [734, 883]]"
    test_mask_data_type = "int64"

    output_array = SWIFTProcessor.load_ndarray_from_json(
        test_mask_array_json,
        test_mask_data_type,
    )

    assert isinstance(output_array, np.ndarray)
    assert str(output_array.dtype) == test_mask_data_type


def test_load_ndarray_from_json_failure_dtype():
    test_mask_array_json = "[[0, 334], [334, 734], [734, 883]]"
    test_mask_data_type = "nt64"

    with pytest.raises(SWIFTProcessorError) as error:
        SWIFTProcessor.load_ndarray_from_json(test_mask_array_json, test_mask_data_type)
    assert "Invalid data type" in str(error.value)


def test_load_ndarray_from_json_failure_invalid_array():
    test_mask_array_json = '{"a": null, "b": [2, "3"]}'
    test_mask_data_type = "float32"

    with pytest.raises(SWIFTProcessorError) as error:
        SWIFTProcessor.load_ndarray_from_json(test_mask_array_json, test_mask_data_type)

    assert "Invalid data type provided" in str(error.value)


def test_load_ndarray_from_json_failure_inhomogeneous_shape():
    test_mask_array_json = "[[337.0], [234.1, 233.1], [355.1]]"
    test_mask_data_type = "float32"
    with pytest.raises(SWIFTProcessorError) as error:
        SWIFTProcessor.load_ndarray_from_json(test_mask_array_json, test_mask_data_type)

    assert "Invalid array data" in str(error.value)


def test_generate_dict_from_ndarray_object_array():
    test_mask_array_json = '[{"a": null, "b": [2, "3"]}, 3]'
    test_numpy_array = np.asarray(json.loads(test_mask_array_json))

    output_dict = SWIFTProcessor.generate_dict_from_ndarray(test_numpy_array)

    assert isinstance(output_dict, dict)
    assert isinstance(output_dict["array"], list)
    assert output_dict["array"][-1] == test_numpy_array[-1]
    assert output_dict["dtype"] == "|O"


def test_generate_dict_from_ndarray_float32_little_endian():
    test_mask_array_json = "[[337.0], [234.1], [355.1]]"
    test_mask_data_type = "<f4"
    test_numpy_array = np.asarray(
        json.loads(test_mask_array_json),
        dtype=test_mask_data_type,
    )

    output_dict = SWIFTProcessor.generate_dict_from_ndarray(test_numpy_array)

    assert isinstance(output_dict, dict)
    assert isinstance(output_dict["array"], list)
    assert output_dict["dtype"] == "<f4"


def test_generate_dict_from_ndarray_float32_big_endian():
    test_mask_array_json = "[[337.0], [234.1], [355.1]]"
    test_mask_data_type = ">f4"
    test_numpy_array = np.asarray(
        json.loads(test_mask_array_json),
        dtype=test_mask_data_type,
    )

    output_dict = SWIFTProcessor.generate_dict_from_ndarray(test_numpy_array)

    assert isinstance(output_dict, dict)
    assert isinstance(output_dict["array"], list)
    assert output_dict["dtype"] == ">f4"


def test_get_array_unmasked_no_columns(
    template_dataset_alias_map,
    template_swift_data_path,
):
    test_field = "PartType0/DiffusionParameters"
    test_columns = None
    processor = SWIFTProcessor(template_dataset_alias_map)

    expected_shape = (261992,)
    expected_first_element_6dp = "6.377697e-06"
    expected_final_element_6dp = "1.192093e-06"

    output = processor.get_array_unmasked(
        template_swift_data_path,
        test_field,
        test_columns,
    )

    assert output.shape == expected_shape
    assert f"{output[0]:.6e}" == expected_first_element_6dp
    assert f"{output[-1]:.6e}" == expected_final_element_6dp


def test_get_array_unmasked_columns(
    template_dataset_alias_map,
    template_swift_data_path,
):
    test_field = "PartType0/SmoothedElementMassFractions"
    test_columns = 0
    processor = SWIFTProcessor(template_dataset_alias_map)

    expected_shape = (261992,)
    expected_first_element_col0 = "0.75200003"
    expected_final_element_col0 = "0.75200033"
    expected_first_element_col1 = "0.24800000"
    expected_final_element_col1 = "0.24800017"

    output = processor.get_array_unmasked(
        template_swift_data_path,
        test_field,
        test_columns,
    )

    assert output.shape == expected_shape
    assert f"{output[0]:.8f}" == expected_first_element_col0
    assert f"{output[-1]:.8f}" == expected_final_element_col0

    test_columns = 1
    output = processor.get_array_unmasked(
        template_swift_data_path,
        test_field,
        test_columns,
    )
    assert output.shape == expected_shape
    assert f"{output[0]:.8f}" == expected_first_element_col1
    assert f"{output[-1]:.8f}" == expected_final_element_col1


def test_get_array_unmasked_field_keyerror_yields_none(
    template_dataset_alias_map,
    template_swift_data_path,
):
    test_field = "PartType0/NotARealField"
    test_columns = None
    processor = SWIFTProcessor(template_dataset_alias_map)

    output = processor.get_array_unmasked(
        template_swift_data_path,
        test_field,
        test_columns,
    )
    assert not output


def test_get_array_spatial_masked_no_columns(
    template_dataset_alias_map,
    template_swift_data_path,
):
    test_mask_array_json = "[[0, 334]]"
    test_mask_data_type = "int64"
    test_mask_size = 334
    test_field = "PartType0/DiffusionParameters"
    test_columns = None
    test_filename = str(template_swift_data_path)

    processor = SWIFTProcessor(template_dataset_alias_map)

    expected_first_element = "6.37769699e-06"
    expected_final_element = "8.94069672e-07"

    masked_array = processor.get_array_masked(
        test_filename,
        test_field,
        test_mask_array_json,
        test_mask_data_type,
        test_mask_size,
        test_columns,
    )
    assert masked_array
    assert masked_array.shape == (test_mask_size,)
    assert f"{masked_array[0]:.8e}" == expected_first_element
    assert f"{masked_array[-1]:.8e}" == expected_final_element


def test_get_array_spatial_masked_columns(
    template_dataset_alias_map,
    template_swift_data_path,
):
    test_mask_array_json = "[[0, 334]]"
    test_mask_data_type = "int64"
    test_mask_size = 334
    test_field = "PartType0/SmoothedElementMassFractions"
    test_columns = 0
    test_filename = str(template_swift_data_path)

    processor = SWIFTProcessor(template_dataset_alias_map)

    expected_first_element = "0.75200003"
    expected_final_element = "0.75199974"

    masked_array = processor.get_array_masked(
        test_filename,
        test_field,
        test_mask_array_json,
        test_mask_data_type,
        test_mask_size,
        test_columns,
    )
    assert masked_array
    assert masked_array.shape == (test_mask_size,)
    assert f"{masked_array[0]:.8f}" == expected_first_element
    assert f"{masked_array[-1]:.8f}" == expected_final_element
