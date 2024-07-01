import time
import yaml
from yaml.loader import SafeLoader
from urllib.parse import urlparse


def get_app_version():
    # Read the version from the API YAML file
    try:
        with open("backend/swagger.yaml") as f:
            data = yaml.load(f, Loader=SafeLoader)
            return data["info"]["version"]
    except Exception as e:
        print(e)
        return "?.?.?"


# Date
def timeNow():
    return time.time() * 1000


# Url
def is_url_valid(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# Name
def is_valid_name(name):
    # /, &, | are not allowed in data-providers & algo-providers names
    if (
        "/" in name
        or "&" in name
        or "|" in name
        or len(name) == 0
        or len(name) > 50
        or name[0] == " "
        or name[-1] == " "
    ):
        return False

    return True
