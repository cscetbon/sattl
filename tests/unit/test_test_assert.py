from sattl.test_step import TestAssert
from sattl.salesforce import SalesforceObject

import pytest
from mock import patch, mock_open, MagicMock


def test_assert_succeeds(yaml_with_five_sf_objects, sample_object_content):
    mock_sf_connection = MagicMock()

    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.matches') as mock_so_matches:
        test_assert = TestAssert("00-assert.yaml", sf_connection=mock_sf_connection)
        test_assert.validate()
    assert mock_so_matches.call_count == 5
    mock_so_matches.assert_called_with(SalesforceObject(mock_sf_connection, sample_object_content))


def test_assert_fails(yaml_with_five_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.matches', return_value=False) as mock_so_matches, \
         pytest.raises(Exception) as exc:
        TestAssert("00-assert.yaml", sf_connection=MagicMock()).validate()

    assert mock_so_matches.call_count == 1
    assert str(exc.value) == ("Assert failed: \n"
                              "      type: Account\n"
                              "      externalID:\n"
                              "-       Slug__c: XC-2\n"
                              "?                   ^\n"
                              "+       Slug__c: XC-3\n"
                              "?                   ^\n"
                              "RecordTypeId: 0123t000000FkA9AAK\n"
                              "SIS_Last_Name__c: Coffee\n"
                              "University_Email__c: jdoe@test.com\n")
