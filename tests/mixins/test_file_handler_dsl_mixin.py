import pytest
import os
import tempfile
import yaml
import json
import toml
from pydantic import BaseModel
from faker import Faker
from dslmodel.mixins.to_from_dsl_mixin import ToFromDSLMixin
from dslmodel.mixins.file_handler_dsl_mixin import FileHandlerDSLMixin

# Define a simple model inheriting from BaseModel, ToFromDSLMixin, and FileHandlerDSLMixin
class MyModel(BaseModel, ToFromDSLMixin, FileHandlerDSLMixin):
    name: str
    value: int

    def generate_filename(self, ext: str = "yaml", add_timestamp: bool = False) -> str:
        return f"temp_2024.{ext}"

# Instantiate Faker for generating random data
fake = Faker()

# Helper function to generate random valid models
def generate_random_model() -> MyModel:
    return MyModel(name=fake.first_name(), value=fake.random_int(min=0, max=100))

@pytest.fixture
def temp_file():
    """Fixture that provides a temporary file path for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    os.remove(tmp.name)

def test_save_yaml(temp_file: str):
    model = generate_random_model()
    file_path = model.save(file_path=temp_file + ".yaml", file_format="yaml")

    # Verify that the YAML file was saved and contains valid data
    with open(file_path, "r") as f:
        content = yaml.safe_load(f)
        assert content["name"] == model.name
        assert content["value"] == model.value

def test_save_json(temp_file: str):
    model = generate_random_model()
    file_path = model.save(file_path=temp_file + ".json", file_format="json")

    # Verify that the JSON file was saved and contains valid data
    with open(file_path, "r") as f:
        content = json.load(f)
        assert content["name"] == model.name
        assert content["value"] == model.value

def test_save_toml(temp_file: str):
    model = generate_random_model()
    file_path = model.save(file_path=temp_file + ".toml", file_format="toml")

    # Verify that the TOML file was saved and contains valid data
    with open(file_path, "r") as f:
        content = toml.load(f)
        assert content["name"] == model.name
        assert content["value"] == model.value

def test_load_yaml(temp_file: str):
    model = generate_random_model()
    model.save(file_path=temp_file + ".yaml", file_format="yaml")

    # Load the model from the saved YAML file
    loaded_model = MyModel.load(file_path=temp_file + ".yaml")

    # Verify that the loaded model matches the original model
    assert loaded_model == model

def test_load_json(temp_file: str):
    model = generate_random_model()
    model.save(file_path=temp_file + ".json", file_format="json")

    # Load the model from the saved JSON file
    loaded_model = MyModel.load(file_path=temp_file + ".json")

    # Verify that the loaded model matches the original model
    assert loaded_model == model

def test_load_toml(temp_file: str):
    model = generate_random_model()
    model.save(file_path=temp_file + ".toml", file_format="toml")

    # Load the model from the saved TOML file
    loaded_model = MyModel.load(file_path=temp_file + ".toml")

    # Verify that the loaded model matches the original model
    assert loaded_model == model

def test_save_invalid_format(temp_file: str):
    model = generate_random_model()
    with pytest.raises(ValueError, match="Unsupported file format"):
        model.save(file_path=temp_file + ".xml", file_format="xml")


def test_generate_filename():
    model = generate_random_model()

    # Test YAML filename generation
    yaml_filename = model.generate_filename(ext="yaml")
    assert yaml_filename.endswith(".yaml")

    # Test JSON filename generation
    json_filename = model.generate_filename(ext="json")
    assert json_filename.endswith(".json")

    # Test TOML filename generation
    toml_filename = model.generate_filename(ext="toml")
    assert toml_filename.endswith(".toml")

    # Test timestamped filename generation
    timestamped_filename = model.generate_filename(ext="yaml", add_timestamp=True)
    assert timestamped_filename.endswith(".yaml")
    assert len(timestamped_filename.split("_")) > 1  # Check if timestamp is appended
