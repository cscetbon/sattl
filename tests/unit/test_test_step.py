import pytest
from mock import patch, mock_open, MagicMock, Mock
import yaml

from sattl.test_step import TestStep, TestManifest, TestAssert
from sattl.salesforce import SalesforceObject


@pytest.fixture
def sample_test_step():
    return TestStep(
        prefix="00", manifests=["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"], assertion="00-assert.yaml",
        sf_connection=Mock(),
    )


@pytest.fixture
def sample_object_content():
    return dict(type="Account", externalID=dict(Slug__c="aaa"), name="bbb")


@pytest.fixture
def yaml_content_of_sf_objects(sample_object_content):
    return yaml.dump_all([*(sample_object_content,)*5])


def test_step_fails_if_multiple_assertions(sample_test_step):
    with pytest.raises(Exception) as exc:
        sample_test_step.set_assertion("00-other-assert.yaml")
    assert str(exc.value) == "Assertion already set to 00-assert.yaml. You can't have more than one."


@pytest.mark.parametrize('assertion, manifests', [
    ("00-assert.yaml", ["00-pa-enrollment-case.yaml"]),
    (None, ["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"]),
])
def test_step(assertion, manifests):
    step = TestStep(prefix="00", manifests=None, assertion=assertion)
    assert step.manifests == []
    assert step.assertion == assertion
    for manifest in manifests:
        step.add_manifest(manifest)
    assert step.manifests == manifests


def test_step_fails_when_apply_fails(sample_test_step):
    with pytest.raises(Exception), \
         patch.object(TestManifest, "apply", side_effect=Exception) as mock_apply, \
         patch.object(TestAssert, "validate") as mock_validate:
        sample_test_step.run()

    mock_apply.assert_called_once()
    mock_validate.assert_not_called()


def test_step_fails_when_assert_fails(sample_test_step):
    with pytest.raises(Exception), \
         patch('sattl.test_step.TestManifest') as mock_test_manifest, \
         patch('sattl.test_step.TestAssert') as mock_test_assert:
        mock_test_assert().validate.side_effect = Exception
        sample_test_step.run()
    assert mock_test_manifest().apply.call_count == 2
    mock_test_assert().validate.assert_called_once()


def test_step_manifests_and_asserts(sample_test_step):
    with patch('sattl.test_step.get_sf_connection'), \
         patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "validate") as mock_validate:
        sample_test_step.run()

    assert mock_apply.call_count == 2
    mock_validate.assert_called_once()


def test_assert_succeeds(yaml_content_of_sf_objects, sample_object_content):
    sf_connection = MagicMock()
    with patch("builtins.open", mock_open(read_data=yaml_content_of_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.matches') as mock_so_matches:
        test_assert = TestAssert("00-assert.yaml", sf_connection=sf_connection)
        test_assert.validate()
    assert mock_so_matches.call_count == 5
    mock_so_matches.assert_called_with(SalesforceObject(sf_connection, sample_object_content))


def test_assert_fails(sample_object_content):
    content = yaml.dump_all([*(sample_object_content,)*2])
    with patch("builtins.open", mock_open(read_data=content)), \
         patch('sattl.test_step.SalesforceObject.matches', return_value=False) as mock_so_matches, \
         pytest.raises(Exception) as exc:
        TestAssert("00-assert.yaml", sf_connection=MagicMock()).validate()

    assert mock_so_matches.call_count == 1
    assert str(exc.value) == ("Failed to assert object "
                              "{'externalID': {'Slug__c': 'aaa'}, 'name': 'bbb', 'type': 'Account'}")


def test_manifest_succeeds(yaml_content_of_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_content_of_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.upsert') as mock_so_upsert:
        test_manifest = TestManifest("00-new-account.yaml", sf_connection=Mock())
        test_manifest.apply()
    assert mock_so_upsert.call_count == 5


def test_manifest_fails(yaml_content_of_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_content_of_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.upsert', return_value=False) as mock_so_upsert, \
         pytest.raises(Exception) as exc:
        test_manifest = TestManifest("00-new-account.yaml", sf_connection=Mock())
        test_manifest.apply()
    assert mock_so_upsert.call_count == 1
    assert str(exc.value) == ("Failed to upsert object "
                              "{'externalID': {'Slug__c': 'aaa'}, 'name': 'bbb', 'type': 'Account'}")
