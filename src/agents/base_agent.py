import os
import yaml
import logging
from src.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, github_api, agent_name=None):
        """
        Initialize the BaseAgent.

        Args:
            github_api: GitHubAPI instance for interacting with GitHub.
            agent_name (str): The name of the agent for configuration loading purposes.
        """
        self.github_api = github_api
        self.agent_name = agent_name

        # Load WatsonX configuration from file
        config_loader = ConfigLoader(config_dir="./config")
        common_config = config_loader.get_config().get("models", {})  # Changed from 'watsonx_models' to 'models'

        # Load WatsonX configuration
        watsonx_config = common_config.get("watsonx", {})

        # Set WatsonX API parameters, override with environment variables if set
        self.watsonx_url = os.getenv('WATSONX_URL', watsonx_config.get("api_url"))
        self.watsonx_api_key = os.getenv('WATSONX_APIKEY', watsonx_config.get("access_token"))
        self.watsonx_project_id = os.getenv('WATSONX_PROJECT_ID', watsonx_config.get("project_id"))

        # Check if the required configurations are set properly
        if not (self.watsonx_url and self.watsonx_api_key and self.watsonx_project_id):
            logger.error("Missing WatsonX configuration. Ensure api_url, access_token, and project_id are properly set.")
            raise ValueError("Missing WatsonX configuration parameters.")

        logger.info("WatsonX configuration loaded successfully.")

        # Load agent-specific configuration
        if agent_name:
            agent_config_path = f"./config/agents/{agent_name}.yaml"
            if os.path.exists(agent_config_path):
                with open(agent_config_path, "r") as file:
                    agent_config = yaml.safe_load(file)
                    self.agent_config = agent_config
            else:
                logger.warning(f"Configuration file not found for agent: {agent_name}")
                self.agent_config = {}
        else:
            self.agent_config = {}

    def get_agent_prompt(self):
        """
        Retrieve the prompt from the agent configuration.

        Returns:
            str: The prompt used by the agent.
        """
        return self.agent_config.get("prompt", "")

    def get_model_id(self):
        """
        Retrieve the model ID from the agent configuration.

        Returns:
            str: The model ID used for WatsonX.
        """
        return self.agent_config.get("model_id", "meta-llama/llama-3-70b-instruct")

    def get_model_parameters(self):
        """
        Retrieve model parameters from the agent configuration.

        Returns:
            dict: Model parameters such as temperature, decoding method, etc.
        """
        return self.agent_config.get("parameters", {"decoding_method": "greedy",
                                                    "max_new_tokens": 900,
                                                    "stop_sequences": [],
                                                    "repetition_penalty": 1})
