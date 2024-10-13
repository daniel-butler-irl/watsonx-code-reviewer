import os
import pytest
from ruamel.yaml import YAML
from src.utils.config_loader import ConfigLoader

yaml = YAML()

@pytest.fixture
def config_loader():
    # Fixture to create an instance of ConfigLoader for testing
    return ConfigLoader(config_dir="tests/test_data/")

def test_load_yaml(config_loader):
    # Load the valid db config file and test the values
    result = config_loader.load_yaml("valid_db_config.yaml")
    assert result['postgres']['user'] == 'test_user'
    assert result['postgres']['password'] == 'test_password'
    assert result['elasticsearch']['host'] == 'localhost'
    assert result['elasticsearch']['port'] == 9200

def test_environment_variable_override_postgres(config_loader, mocker):
    # Load the valid db config file
    mocker.patch("builtins.open", mocker.mock_open(read_data=open("tests/test_data/valid_db_config.yaml").read()))

    # Set environment variables to override the YAML values
    mocker.patch.dict(os.environ, {"DB_USER": "override_user", "DB_PASSWORD": "override_password"})

    config = config_loader.get_config()
    assert config['db']['postgres']['user'] == "override_user"
    assert config['db']['postgres']['password'] == "override_password"

def test_environment_variable_override_elasticsearch(config_loader, mocker):
    # Load the valid db config file
    mocker.patch("builtins.open", mocker.mock_open(read_data=open("tests/test_data/valid_db_config.yaml").read()))

    # Set environment variables to override the YAML values
    mocker.patch.dict(os.environ, {
        "ELASTIC_HOST": "override_host",
        "ELASTIC_PORT": "9300",
        "ELASTIC_USER": "override_user",
        "ELASTIC_PASSWORD": "override_password"
    })

    config = config_loader.get_config()
    assert config['db']['elasticsearch']['host'] == "override_host"
    assert config['db']['elasticsearch']['port'] == 9300
    assert config['db']['elasticsearch']['user'] == "override_user"
    assert config['db']['elasticsearch']['password'] == "override_password"

def test_missing_file(config_loader):
    # Test behavior when a configuration file is missing
    with pytest.raises(FileNotFoundError):
        config_loader.load_yaml("non_existent.yaml")

def test_invalid_yaml_file(config_loader, mocker):
    # Mock the open function to simulate reading an invalid YAML file
    invalid_yaml = """
    postgres:
      host: localhost
      port: not_a_port
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=invalid_yaml))

    with pytest.raises(ValueError):
        config_loader.get_config()
