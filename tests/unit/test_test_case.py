from sattl.test_case import TestCase
import pytest
from mock import patch


def test_test_case_fail():
    with pytest.raises(AttributeError) as exc:
        TestCase("/does/not/exists")
    assert str(exc.value) == "path /does/not/exists is not readable"


def test_test_case_empty_folder():
    with pytest.raises(AttributeError) as exc, patch('os.access'), patch('os.listdir', return_value=[]):
        TestCase("/empty/folder").setup()
    assert str(exc.value) == "path /empty/folder is empty"


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
    assert set0._asserts == '00-assert.yaml'
    assert set0.manifests == ['00-pa-account0-case.yaml', '00-pa-enrollment0-case.yaml']

    assert "01" in test_case.content
    set1 = test_case.content["01"]
    assert set1._asserts == '01-assert.yaml'
    assert set1.manifests == ['01-pa-enrollment1-case.yaml', '01-pa-enrollment1-case.yaml']
