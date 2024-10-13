import os
from ruamel.yaml import YAML

class ConfigLoader:
    def __init__(self, config_dir="config/"):
        self.config_dir = config_dir
        self.yaml = YAML()  # Create an instance of the YAML class from ruamel.yaml

    def load_yaml(self, filename):
        file_path = os.path.join(self.config_dir, filename)
        with open(file_path, 'r') as file:
            return self.yaml.load(file)

    def get_config(self):
        config = self.load_yaml("config.yaml")
        db_config = self.load_yaml("db_config.yaml")
        models_config = self.load_yaml("watsonx_models.yaml")

        # Convert the returned structure to a regular dict for easier manipulation
        config = dict(config)
        db_config = dict(db_config)
        models_config = dict(models_config)

        try:
            # Override PostgreSQL settings with environment variables
            db_config['postgres']['user'] = os.getenv('DB_USER', db_config.get('postgres', {}).get('user', ''))
            db_config['postgres']['password'] = os.getenv('DB_PASSWORD', db_config.get('postgres', {}).get('password', ''))

            # Override Elasticsearch settings with environment variables
            db_config['elasticsearch']['host'] = os.getenv('ELASTIC_HOST', db_config.get('elasticsearch', {}).get('host', 'localhost'))
            db_config['elasticsearch']['port'] = int(os.getenv('ELASTIC_PORT', db_config.get('elasticsearch', {}).get('port', 9200)))
            db_config['elasticsearch']['user'] = os.getenv('ELASTIC_USER', db_config.get('elasticsearch', {}).get('user', ''))
            db_config['elasticsearch']['password'] = os.getenv('ELASTIC_PASSWORD', db_config.get('elasticsearch', {}).get('password', ''))

        except KeyError as e:
            raise ValueError(f"Missing expected configuration key: {e}")

        config['db'] = db_config
        config['models'] = models_config
        return config

# Example usage:
if __name__ == "__main__":
    config_loader = ConfigLoader()
    config = config_loader.get_config()
    print(config)
