from sattl.test_case import TestCase, StepType, Step
from collections import OrderedDict
import pytest
from mock import patch


@pytest.mark.parametrize('step_type, elements', [
    (StepType.Assert, ["00-assert.yaml", "00-pa-enrollment-case.yaml"]),
    (StepType.Manifest, ["00-pa-account-case.yaml", "00-pa-enrollment-case.yaml"]),
])
def test_step(step_type, elements):
    step = Step(step_type)
    assert step._type == step_type
    assert step.content == []
    for element in elements:
        step.append(element)
    assert step.content == elements


def test_test_case_fail():
    with pytest.raises(AttributeError) as exc:
        TestCase("/does/not/exists")
    str(exc.value) == "path /does/not/exists is not readable"


def test_test_case():
    files = [
        "01-assert.yaml",
        "00-pa-account0-case.yaml",
        "00-assert.yaml",
        "01-pa-enrollment1-case.yaml",
        "00-pa-enrollment0-case.yaml",
        "01-pa-enrollment1-case.yaml",
        "folder"
    ]
    with patch('os.access'), \
         patch('os.listdir', return_value=files), \
         patch('os.path.isfile', lambda f: f != "folder"):
        test_case = TestCase("/does/exists")
        test_case.setup()
    assert test_case.path == "/does/exists"
    assert len(test_case.content) == 2

    assert "00" in test_case.content
    set0 = test_case.content["00"]
    assert len(set0) == 2
    assert set0[StepType.Assert] == Step(StepType.Assert, ['00-assert.yaml'])
    assert set0[StepType.Manifest] == Step(StepType.Manifest,
                                           ['00-pa-account0-case.yaml', '00-pa-enrollment0-case.yaml'])

    assert "01" in test_case.content
    set1 = test_case.content["01"]
    assert len(set1) == 2
    assert set1[StepType.Assert] == Step(StepType.Assert, ['01-assert.yaml'])
    assert set1[StepType.Manifest] == Step(StepType.Manifest,
                                           ['01-pa-enrollment1-case.yaml', '01-pa-enrollment1-case.yaml'])
