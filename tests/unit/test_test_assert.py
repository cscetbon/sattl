from sattl.test_step import TestAssert
from sattl.salesforce import SalesforceObject

import pytest
from mock import patch, mock_open, MagicMock, Mock, PropertyMock


def test_assert_succeeds(yaml_with_five_sf_objects, sample_object_content):
    mock_sf_connection = MagicMock()

    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.differences', return_value=None) as mock_so_differences:
        test_assert = TestAssert("00-assert.yaml", sf_connection=mock_sf_connection)
        test_assert.validate()
    assert mock_so_differences.call_count == 5
    mock_so_differences.assert_called_with(SalesforceObject(mock_sf_connection, sample_object_content))


def test_assert_fails_because_cannot_load_it(yaml_with_five_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.load', return_value=False) as mock_so_differences, \
         pytest.raises(Exception) as exc:
        TestAssert("00-assert.yaml", sf_connection=MagicMock()).validate()

    mock_so_differences.assert_called_once()
    assert str(exc.value) == "Assert failed because the object can't be found in SF"


def test_assert_fails_because_it_is_different(yaml_with_five_sf_objects, sample_object_content):
    sf_object = Mock()
    sf_object.differences.return_value = "expected_output"
    with pytest.raises(Exception) as exc, \
         patch("sattl.test_step.TestStepElement.sf_objects", new_callable=PropertyMock) as mock_sf_objects:
        mock_sf_objects.return_value = [sf_object]
        TestAssert("00-assert.yaml", sf_connection=MagicMock()).validate()

    sf_object.differences.assert_called_once_with(sf_object)
    assert str(exc.value) == "Assert failed because there are differences:\nexpected_output"
