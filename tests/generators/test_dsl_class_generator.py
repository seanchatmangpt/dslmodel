import pytest

from dslmodel.generators.dsl_class_generator import DSLClassGenerator


@pytest.fixture
def temp_directory(tmp_path):
    """
    Fixture to provide a temporary directory for test files.
    """
    return tmp_path


@pytest.fixture
def temp_directory(tmp_path):
    """
    Fixture to provide a temporary directory for test files.
    """
    return tmp_path


def test_file_creation_with_auto_naming(temp_directory):
    """
    Test that a file is correctly auto-named and created in a specified directory
    with 2 fields.
    """
    from dslmodel import init_instant

    init_instant()
    model_prompt = "I need a UserModel with 2 fields"
    file_path = temp_directory  # Provide directory only

    # Create an instance of DSLClassGenerator
    dsl_generator = DSLClassGenerator(model_prompt, file_path)

    # Generate and save the class
    generated_class_path = dsl_generator.forward()

    # Check if the file was correctly generated and auto-named
    expected_file = file_path / "user_model.py"
    assert generated_class_path == expected_file
    assert expected_file.exists()

    # Check the content of the file for the 2 fields
    with open(expected_file) as f:
        content = f.read()
        assert "class UserModel" in content


def test_file_creation_with_specific_name(temp_directory):
    """
    Test that a file is created with a specified file name.
    """
    from dslmodel import init_instant

    init_instant()

    model_prompt = "I need a verbose contact model named ContactModel from the friend of a friend ontology with 20 fields"
    file_path = temp_directory / "specific_model.py"  # Provide full path with specific file name

    # Create an instance of DSLClassGenerator
    dsl_generator = DSLClassGenerator(model_prompt, file_path)

    # Generate and save the class
    generated_class_path = dsl_generator.forward()

    # Check if the file was correctly generated with the specified name
    assert generated_class_path == file_path
    assert file_path.exists()

    # Check the content of the file
    with open(file_path) as f:
        content = f.read()
        assert "class ContactModel" in content
        assert "from pydantic import Field" in content  # Check that imports are included
