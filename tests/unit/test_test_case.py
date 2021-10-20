from sattl.test_case import TestCase, TestStep
import pytest
from mock import patch


def test_test_case_empty_folder():
    with pytest.raises(AttributeError) as exc, patch('os.access'), patch('os.listdir', return_value=[]):
        TestCase(path="/empty/folder", domain="fake", timeout=7).setup()
    assert str(exc.value) == "path /empty/folder is empty"


def test_test_case():
    files = [
        "01-assert.yaml",
        "00-pa-account0-case.yaml",
        "00-assert.yaml",
        "01-pa-account1-case.yaml",
        "00-pa-enrollment0-case.yaml",
        "01-pa-enrollment1-case.yaml",
        "folder"
    ]

    order_of_call = 0

    class FakeTestStep(TestStep):
        def run(self):
            nonlocal order_of_call
            self.order_of_call = order_of_call
            order_of_call += 1

    with patch('os.access'), \
         patch('os.listdir', return_value=files), \
         patch('os.path.isfile', lambda f: f != "folder"), \
         patch('sattl.test_case.get_sf_connection'), \
         patch('sattl.test_case.TestStep', new=FakeTestStep):
        test_case = TestCase(path="/does/exists", domain="fake", timeout=12)
        test_case.setup()
        test_case.run()

    assert test_case.path == "/does/exists"
    assert test_case.content
    assert ["00", "01"] == list(test_case.content.keys())

    for _id in range(2):
        step_id = f"0{_id}"
        assert step_id in test_case.content
        test_step = test_case.content[step_id]
        prefix = f"{test_case.path}/{step_id}"
        assert test_step.assertion == f"{prefix}-assert.yaml"
        assert test_step.manifests == [
            f"{prefix}-pa-account{_id}-case.yaml",
            f"{prefix}-pa-enrollment{_id}-case.yaml"
        ]
        assert test_step.order_of_call == _id

