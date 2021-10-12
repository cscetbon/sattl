import yaml
import pytest


@pytest.fixture
def sample_object_content():
    return dict(type="Account", externalID=dict(Slug__c="aaa"), name="bbb")


@pytest.fixture
def yaml_with_five_sf_objects(sample_object_content):
    return yaml.dump_all([*(sample_object_content,)*5])
