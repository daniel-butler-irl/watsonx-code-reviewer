import requests
import logging

logger = logging.getLogger(__name__)

def get_ibm_bearer_token(api_key):
    """
    Get a bearer token from IBM Cloud using the provided API key.

    Args:
        api_key (str): The IBM Cloud API key.

    Returns:
        str: The bearer token, if successful.
    """
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            logger.error(f"Failed to get IBM Cloud bearer token: {response.status_code}, {response.text}")
            raise Exception("Unable to obtain bearer token from IBM Cloud.")

        return response.json()["access_token"]

    except Exception as e:
        logger.error(f"Exception occurred while getting IBM Cloud bearer token: {str(e)}")
        raise
