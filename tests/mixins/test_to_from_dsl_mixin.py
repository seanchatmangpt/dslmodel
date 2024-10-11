import pytest
import yaml
import json
import toml
from pydantic import BaseModel
from faker import Faker
from dslmodel.mixins.to_from_dsl_mixin import ToFromDSLMixin

# Define a simple model inheriting from BaseModel and ToFromDSLMixin
class MyModel(BaseModel, ToFromDSLMixin):
    name: str
    value: int

# Instantiate Faker for generating random data
fake = Faker()

# Helper function to generate random valid models
def generate_random_model() -> MyModel:
    return MyModel(name=fake.first_name(), value=fake.random_int(min=0, max=100))

# Test to_json and from_json
def test_to_from_json():
    model = generate_random_model()
    json_content = model.to_json()
    loaded_model = MyModel.from_json(json_content)
    assert model == loaded_model  # Ensure round-trip consistency

# Test to_yaml and from_yaml
def test_to_from_yaml():
    model = generate_random_model()
    yaml_content = model.to_yaml()
    loaded_model = MyModel.from_yaml(yaml_content)
    assert model == loaded_model  # Ensure round-trip consistency

# Test to_toml and from_toml
def test_to_from_toml():
    model = generate_random_model()
    toml_content = model.to_toml()
    loaded_model = MyModel.from_toml(toml_content)
    assert model == loaded_model  # Ensure round-trip consistency

# Test all permutations of format conversions
@pytest.mark.parametrize("save_format, load_format", [
    ('json', 'json'),
    ('json', 'yaml'),
    ('json', 'toml'),
    ('yaml', 'json'),
    ('yaml', 'yaml'),
    ('yaml', 'toml'),
    ('toml', 'json'),
    ('toml', 'yaml'),
    ('toml', 'toml'),
])
def test_format_permutations(save_format, load_format):
    """
    Test all permutations of serializing in one format and deserializing in another.
    """
    model = generate_random_model()

    # Serialize based on the save format
    if save_format == 'json':
        content = model.to_json()
        intermediate_model = MyModel.from_json(content)  # Deserialize into model
    elif save_format == 'yaml':
        content = model.to_yaml()
        intermediate_model = MyModel.from_yaml(content)  # Deserialize into model
    elif save_format == 'toml':
        content = model.to_toml()
        intermediate_model = MyModel.from_toml(content)  # Deserialize into model

    # Now serialize again using the new format
    if load_format == 'json':
        final_content = intermediate_model.to_json()
        loaded_model = MyModel.from_json(final_content)
    elif load_format == 'yaml':
        final_content = intermediate_model.to_yaml()
        loaded_model = MyModel.from_yaml(final_content)
    elif load_format == 'toml':
        final_content = intermediate_model.to_toml()
        loaded_model = MyModel.from_toml(final_content)

    # Ensure round-trip consistency across formats
    assert model == loaded_model
