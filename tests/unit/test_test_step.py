import pytest
from mock import patch, mock_open, Mock

from sattl.test_step import TestStepElement, TestStep, TestManifest, TestAssert, TestDelete


@pytest.fixture
def sample_test_step():
    return TestStep(
        prefix="00", assert_timeout=10, manifests=["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"],
        assertion="00-assert.yaml", delete="00-delete.yaml", sf_connection=Mock(),
    )


def test_step_element_caches_file_access():
    with patch("builtins.open", mock_open(read_data="")) as m_open:
        test_step_element = TestStepElement("00-assert-not-used.yaml", sf_connection=Mock())
        assert test_step_element.sf_objects == test_step_element.sf_objects

    assert m_open.call_count == 1


def test_step_fails_if_multiple_assertions(sample_test_step):
    with pytest.raises(Exception) as exc:
        sample_test_step.set_assertion("00-other-assert.yaml")
    assert str(exc.value) == "Assertion already set to 00-assert.yaml. You can't have more than one."


def test_step_fails_if_multiple_deletes(sample_test_step):
    with pytest.raises(Exception) as exc:
        sample_test_step.set_delete("00-other-delete.yaml")
    assert str(exc.value) == "Delete already set to 00-delete.yaml. You can't have more than one."


@pytest.mark.parametrize('delete, assertion, manifests', [
    ("00-delete.yaml", "00-assert.yaml", ["00-pa-enrollment-case.yaml"]),
    (None, None, ["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"]),
])
def test_step(delete, assertion, manifests):
    step = TestStep(prefix="00", assert_timeout=10, manifests=None, assertion=assertion, delete=delete)
    assert step.manifests == []
    assert step.assertion == assertion
    assert step.delete == delete
    for manifest in manifests:
        step.add_manifest(manifest)
    assert step.manifests == manifests


def test_step_run(sample_test_step):
    with patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "validate") as mock_validate, \
         patch.object(TestDelete, "apply") as mock_delete:
        sample_test_step.run()

    assert mock_apply.call_count == 2
    mock_validate.assert_called_once()
    mock_delete.assert_called_once()


def test_step_fails_when_apply_fails(sample_test_step):
    sample_test_step.assertion = None

    with pytest.raises(Exception), patch.object(TestManifest, "apply", side_effect=Exception) as mock_apply:
        sample_test_step.run()

    mock_apply.assert_called_once()

    sample_test_step.manifests = []

    with pytest.raises(Exception), patch.object(TestDelete, "apply", side_effect=Exception) as mock_apply:
        sample_test_step.run()

    mock_apply.assert_called_once()


def test_step_fails_when_assert_always_fails(sample_test_step):
    with pytest.raises(Exception), \
         patch('sattl.test_step.RetryWithTimeout', side_effect=lambda func, timeout: func()), \
         patch('sattl.test_step.TestManifest') as mock_test_manifest, \
         patch('sattl.test_step.TestAssert') as mock_test_assert:
        mock_test_assert().validate.side_effect = Exception
        sample_test_step.run()

    assert mock_test_manifest().apply.call_count == 2
    mock_test_assert().validate.assert_called_once()


def test_step_retries_asserts(sample_test_step):
    with patch.object(TestManifest, "apply") as mock_apply, \
         patch('time.sleep'), \
         patch.object(TestAssert, "validate", side_effect=[Exception, Exception, 1]) as mock_validate, \
         patch.object(TestDelete, "apply") as mock_delete:
        sample_test_step.manifests.pop()
        sample_test_step.run()

    mock_apply.assert_called_once()
    mock_delete.assert_called_once()
    assert mock_validate.call_count == 3


def test_manifest_succeeds(yaml_with_five_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.upsert') as mock_so_upsert:
        test_manifest = TestManifest("00-new-account.yaml", sf_connection=Mock())
        test_manifest.apply()
    assert mock_so_upsert.call_count == 5


def test_manifest_fails(yaml_with_five_sf_objects, sample_object_content):
    with patch("builtins.open", mock_open(read_data=yaml_with_five_sf_objects)), \
         patch('sattl.test_step.SalesforceObject.upsert', return_value=False) as mock_so_upsert, \
         pytest.raises(Exception) as exc:
        test_manifest = TestManifest("00-new-account.yaml", sf_connection=Mock())
        test_manifest.apply()
    assert mock_so_upsert.call_count == 1
    assert str(exc.value) == ("Failed to upsert object "
                              "{'externalID': {'Slug__c': 'aaa'}, 'name': 'bbb', 'type': 'Account'}")
