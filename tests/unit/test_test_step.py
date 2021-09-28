import pytest
from mock import patch

from sattl.test_step import TestStep, TestManifest, TestAssert


@pytest.mark.parametrize('_assert, manifests', [
    ("00-assert.yaml", ["00-pa-enrollment-case.yaml"]),
    (None, ["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"]),
])
def test_step(_assert, manifests):
    step = TestStep(prefix="00", manifests=None, _assert=_assert)
    assert step.manifests == []
    assert step._assert == _assert
    for manifest in manifests:
        step.append(manifest)
    assert step.manifests == manifests


def test_step_fail():
    step = TestStep(
        prefix="00", manifests=["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"], _assert="00-assert.yaml"
    )

    with pytest.raises(Exception), \
         patch.object(TestManifest, "apply", side_effect=Exception) as mock_apply, \
         patch.object(TestAssert, "state") as mock_state:
        step.run()

    assert mock_apply.call_count == 1
    assert mock_state.call_count == 0

    with pytest.raises(Exception) as exc, \
         patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "state", side_effect=Exception) as mock_state:
        step.run()

    assert mock_apply.call_count == 2
    assert mock_state.call_count == 1

    with pytest.raises(Exception) as exc:
        step.run()
    assert str(exc.value) == "TestManifest failed to apply 00-pa-account-case.yaml"

    with patch.object(TestManifest, "apply") as mock_apply, \
         patch.object(TestAssert, "state") as mock_state:
        step.run()

    assert mock_apply.call_count == 2
    assert mock_state.call_count == 1
