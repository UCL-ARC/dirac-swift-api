import json

import pytest
from api.processing import units
from unyt import unyt_quantity


def test_unyt_encoder():
    test_unyt_dict = {
        "test_quantity": unyt_quantity(5, "Mpc"),
    }

    expected = '{"test_quantity": "5 Mpc"}'
    assert expected == json.dumps(test_unyt_dict, cls=units.UnytEncoder)


def test_convert_swift_units_dict_types_success():
    test_units_dict = {
        "filename": "/a/test/file/path",
        "units": {
            "Unit current in cgs (U_I)": unyt_quantity(1.0, "statA"),
            "Unit length in cgs (U_L)": unyt_quantity(1e24, "cm"),
            "Unit mass in cgs (U_M)": unyt_quantity(1.9e43, "g"),
            "Unit temperature in cgs (U_T)": unyt_quantity(1.0, "K"),
            "Unit time in cgs (U_t)": unyt_quantity(1.09e19, "s"),
        },
        "mass": unyt_quantity(1.0e10, "Msun"),
        "length": unyt_quantity(1.0, "Mpc"),
        "time": unyt_quantity(1000.0, "Gyr"),
        "current": unyt_quantity(1.0, "statA"),
        "temperature": unyt_quantity(1.0, "K"),
    }

    retrieved_dict = units.convert_swift_units_dict_types(test_units_dict)

    for key, value in retrieved_dict.items():
        if isinstance(value, dict):
            for _subkey, subvalue in retrieved_dict[key].items():
                assert isinstance(subvalue, str)
        else:
            assert isinstance(value, str)


def test_convert_swift_units_dict_types_failure():
    test_units_dict = {
        "filename": "/a/test/file/path",
        "mass": unyt_quantity(1.0e10, "Msun"),
        "length": unyt_quantity(1.0, "Mpc"),
        "time": unyt_quantity(1000.0, "Gyr"),
        "current": unyt_quantity(1.0, "statA"),
        "temperature": unyt_quantity(1.0, "K"),
    }

    with pytest.raises(units.SWIFTUnytException):
        units.convert_swift_units_dict_types(test_units_dict)


def test_retrieve_units_json_compatible():
    pass


def test_retrieve_swiftunits_dict():
    pass


def test_create_unyt_quantities():
    pass
