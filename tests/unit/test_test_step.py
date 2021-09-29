import pytest
from mock import patch

from sattl.test_step import TestStep, TestManifest, TestAssert


@pytest.fixture
def sample_test_step():
    return TestStep(
        prefix="00", manifests=["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"], assertion="00-assert.yaml"
    )


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
         patch.object(TestAssert, "validate") as mock_state:
        sample_test_step.run()

    mock_apply.assert_called_once()
    mock_state.assert_not_called()


def test_step_fails_when_state_fails(sample_test_step):
    with pytest.raises(Exception) as exc, \
         patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "validate", side_effect=Exception) as mock_state:
        sample_test_step.run()

    assert mock_apply.call_count == 2
    mock_state.assert_called_once()


def test_step_fail_as_apply_fails_by_default(sample_test_step):
    with pytest.raises(Exception) as exc:
        sample_test_step.run()
    assert str(exc.value) == "TestManifest failed to apply 00-pa-account-case.yaml"


def test_step_applied_manifests_and_asserted_states(sample_test_step):
    with patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "validate") as mock_state:
        sample_test_step.run()

    assert mock_apply.call_count == 2
    mock_state.assert_called_once()
