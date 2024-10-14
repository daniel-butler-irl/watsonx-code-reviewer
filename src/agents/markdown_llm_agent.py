import logging
import requests
from src.agents.base_agent import BaseAgent
from src.utils.ibm_cloud_auth import get_ibm_bearer_token

logger = logging.getLogger(__name__)

class MarkdownLLMAgent(BaseAgent):
    def __init__(self, github_api):
        """
        Initialize the MarkdownLLMAgent, inheriting from BaseAgent.

        Args:
            github_api: GitHubAPI instance for interacting with GitHub.
        """
        super().__init__(github_api, agent_name="markdown_llm_agent")

    def review(self, full_text, changed_text, existing_comments):
        """
        Use WatsonX LLM to review a markdown file, analyzing both the changed and full text for context.

        Args:
            full_text (str): The full content of the markdown file.
            changed_text (str): The changed content for the current pull request.
            existing_comments (list): List of existing comments to provide context to WatsonX.

        Returns:
            list: A list of review comments returned by the LLM.
        """
        logger.info("Reviewing markdown file with LLM.")

        # Prepare the prompt
        prompt = self.get_agent_prompt()
        input_text = f"{prompt}\n\nFull file content:\n{full_text}\n\nChanged content:\n{changed_text}\n\nExisting comments:\n{existing_comments}"

        # Prepare the request payload
        payload = {
            "input": input_text,
            "parameters": self.get_model_parameters(),
            "model_id": self.get_model_id(),
            "project_id": self.watsonx_project_id
        }

        # Set headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_ibm_bearer_token(self.watsonx_api_key)}"
        }

        try:
            # Make the request to WatsonX LLM API
            response = requests.post(self.watsonx_url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"WatsonX API returned non-200 response: {response.status_code}, {response.text}")
                return []

            # Parse the response from WatsonX
            data = response.json()
            comments = data.get("output", [])

            # Extract comments and structure them as needed
            review_comments = []
            for comment in comments:
                review_comments.append({
                    "line": comment.get("line"),
                    "comment": comment.get("text")
                })

            return review_comments

        except Exception as e:
            logger.error(f"Exception occurred while invoking WatsonX LLM: {str(e)}")
            return []