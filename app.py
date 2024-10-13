import os
import logging
from src.github.webhook_handler import app as webhook_app
from src.utils.config_loader import ConfigLoader
from src.github.github_api import GitHubAPI
from src.agents.review_agent import ReviewAgent
import threading

# Load configuration
config_loader = ConfigLoader(config_dir="./config")
config = config_loader.get_config()

# Configure logging
log_level = os.getenv('LOG_LEVEL', config.get('log_level', 'INFO')).upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_github_api(config):
    logger.info("Initializing GitHub API")
    logger.debug(f"Loaded configuration: {config}")  # Debug log for config content

    # Get GitHub configuration details from the config file
    # These values can be set in the config file or as environment variables
    # Environment variables take precedence over config file values
    github_app_id = config.get('github', {}).get('app_id')
    github_installation_id = config.get('github', {}).get('installation_id')
    github_private_key = config.get('github', {}).get('private_key')

    if not (github_app_id and github_installation_id and github_private_key):
        logger.error("Missing GitHub configuration details. Cannot initialize GitHubAPI.")
        exit(1)

    return GitHubAPI(github_app_id, github_installation_id, github_private_key)

def initialize_agents(github_api):
    logger.info("Initializing Agents")
    # Initialize the ReviewAgent
    review_agent = ReviewAgent(github_api)
    return [review_agent]

def run_webhook_server():
    port = config.get('port', 8080)
    logger.info(f"Starting Webhook Server on port {port}")
    webhook_app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Initialize GitHub API
    github_api = initialize_github_api(config)

    # Initialize Agents
    agents = initialize_agents(github_api)

    # Start the webhook server in a separate thread to allow agents to run concurrently
    webhook_thread = threading.Thread(target=run_webhook_server)
    webhook_thread.start()

    # Example placeholder for future loop or trigger mechanism for agents
    logger.info("Application is now running. Waiting for webhook events...")
    webhook_thread.join()