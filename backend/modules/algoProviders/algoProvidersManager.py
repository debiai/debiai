from termcolor import colored

from backend.config.init_config import (
    get_config,
    DEBUG_COLOR,
    ERROR_COLOR,
    SUCCESS_COLOR,
)
from backend.modules.algoProviders.AlgoProviderException import (
    AlgoProviderException,
)  # noqa
from backend.modules.algoProviders.AlgoProvider import AlgoProvider
from backend.modules.algoProviders.integratedAlgoProvider.integratedAlgoProvider import (  # noqa
    IntegratedAlgoProvider,
)

algo_providers = []


def setup_algo_providers():
    print("================== ALGO PROVIDERS ==================")
    config = get_config()
    config_algo_providers = config["ALGO_PROVIDERS"]

    keys = list(config_algo_providers.keys())
    values = list(config_algo_providers.values())

    # Add AlgoProviders from config file
    print(" - Loading Algo providers from config file")
    for i in range(len(config_algo_providers)):
        name = keys[i]
        url = values[i]

        # Remove trailing slash
        if url[-1] == "/":
            url = url[:-1]

        print(
            " - Adding AlgoProvider "
            + colored(name, DEBUG_COLOR)
            + " ("
            + colored(url, DEBUG_COLOR)
            + ")"
        )
        try:
            algo_provider = AlgoProvider(url, name)
            algo_providers.append(algo_provider)

            if algo_provider.is_alive():
                print(colored("   [SUCCESS]", SUCCESS_COLOR) + " AlgoProvider ready")
            else:
                raise AlgoProviderException()

        except AlgoProviderException:
            print(
                colored("   [ERROR]", ERROR_COLOR)
                + " AlgoProvider "
                + colored(name, ERROR_COLOR)
                + " is not accessible"
            )

    # Add the integrated algo provider
    enable_integrated = config["ALGO_PROVIDERS_CONFIG"]["enable_integrated"]
    if enable_integrated:
        print(" - Adding integrated AlgoProviders")
        algo_provider = IntegratedAlgoProvider()
        nb_algos = len(algo_provider.get_algorithms())
        algo_providers.append(algo_provider)

        if nb_algos > 0:
            print(
                colored("   [SUCCESS]", SUCCESS_COLOR)
                + " Integrated AlgoProvider ready with "
                + str(nb_algos)
                + " algorithms"
            )
        else:
            print("   No algorithms found")

    if len(algo_providers) == 0:
        print("No Algo providers")


def get_algo_providers():
    return algo_providers


def get_algo_providers_json():
    algo_providers_json = []
    for algo_provider in algo_providers:
        algo_providers_json.append(algo_provider.to_json())

    return algo_providers_json


def algo_provider_exists(name):
    for d in algo_providers:
        if d.name == name:
            return True
    return False


def add(algo_provider):
    algo_providers.append(algo_provider)
    return


def get_single_algo_provider(name):
    # Return the algo provider with the given name
    for d in algo_providers:
        if d.name == name:
            return d

    raise AlgoProviderException("Algo provider not found", 404)


def delete(name):
    for d in algo_providers:
        if d.name == name:
            algo_providers.remove(d)
            return
