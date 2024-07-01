#############################################################################
# Imports
#############################################################################
from backend.config.init_config import get_config
from backend.utils.utils import is_url_valid, is_valid_name
import backend.modules.algoProviders.algoProvidersManager as algo_provider_manager
from backend.modules.algoProviders.AlgoProviderException import AlgoProviderException
from backend.modules.algoProviders.AlgoProvider import AlgoProvider

#############################################################################
# Algo providers Management
#############################################################################


def get_algo_providers():
    algorithms = algo_provider_manager.get_algo_providers_json()
    return algorithms, 200


def post_algo_provider(data):
    # Check if we are allowed to add AlgoProviders from the config file
    config = get_config()
    creation_allowed = config["ALGO_PROVIDERS_CONFIG"]["creation"]
    if not creation_allowed:
        return "AlgoProvider creation is not allowed", 403

    # Check if algoProviders already exists
    if algo_provider_manager.algo_provider_exists(data["name"]):
        return "AlgoProvider '" + data["name"] + "' already exists", 400

    # Check if algoProviders name is valid
    if not is_valid_name(data["name"]):
        return "Invalid algoProviders name", 400

    # Add the algoProvider
    # Check if url is valid
    if not is_url_valid(data["url"]):
        return "Invalid url", 400

    algo_provider_manager.add(AlgoProvider(data["url"], data["name"]))

    return None, 204


def use_algo(algoProviderName, algoId, data):
    # Check if algoProviders exists
    if not algo_provider_manager.algo_provider_exists(algoProviderName):
        return "AlgoProvider " + algoProviderName + " does not exists", 404

    try:
        # Use algoProviders
        algo_provider = algo_provider_manager.get_single_algo_provider(algoProviderName)
        return algo_provider.use_algorithm(algoId, data), 200
    except AlgoProviderException as e:
        return e.message, e.status_code


def delete_algo_provider(name):
    # Check if we are allowed to add AlgoProviders from the config file
    config = get_config()
    deletion_allowed = config["ALGO_PROVIDERS_CONFIG"]["deletion"]
    if not deletion_allowed:
        return "AlgoProvider deletion is not allowed", 403

    # Delete the algoProvider
    try:
        algo_provider_manager.delete(name)
        return None, 204
    except AlgoProviderException as e:
        return e.message, e.status_code
