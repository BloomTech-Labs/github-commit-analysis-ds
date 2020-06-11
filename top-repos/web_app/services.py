import os
from dotenv import load_dotenv
import requests
from pprint import pprint
import base64
import json
from github import Github

load_dotenv()

# only if we invoke this function will these methods be called
# create a function under
# so we can call on it in our routes
def github_api_client():
    """
    If not using personal access token, use username and password
    replace client = Github(USERNAME, PASSWORD)
    USERNAME = os.getenv("USERNAME", default="OOPS")
    PASSWORD = os.getenv("PASSWORD", default="OOPS")
    """
    PAT = os.getenv("PERSONAL_ACCESS_TOKEN", default="OOPS")
    client = Github(PAT)
    return client

if __name__ == "__main__":
    # this is the github api client
    client = github_api_client()