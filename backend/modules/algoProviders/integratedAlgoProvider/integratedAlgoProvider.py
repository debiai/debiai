import os
from termcolor import colored

from backend.config.init_config import DEBUG_COLOR
from backend.modules.algoProviders.AlgoProvider import AlgoProvider
from backend.modules.algoProviders.AlgoProviderException import AlgoProviderException


def _get_algorithm_python(algorithm_name):
    """Get the python file of the algorithm

    Args:
        algorithm_name (str): Name of the algorithm

    Returns:
        module: Python module of the algorithm
    """

    # Get the algorithm file
    algorithm_file = None
    for file in os.listdir(os.path.dirname(__file__) + "/algorithms"):
        if file.endswith(".py") and file[:-3] == algorithm_name:
            algorithm_file = file[:-3]
            break

    # Check if the file exists
    if algorithm_file is None:
        raise ValueError("Algorithm " + algorithm_name + " does not exists")

    # Import the algorithm
    algorithm_python = __import__(
        "backend.modules.algoProviders.integratedAlgoProvider.algorithms."
        + algorithm_file,
        fromlist=["*"],
    )

    return (algorithm_name, algorithm_python)


class IntegratedAlgoProvider(AlgoProvider):
    # Integrated AlgoProvider
    # Used to expose the algorithms that are integrated
    # directly in DebiAI
    def __init__(self):
        self.url = "/app/algo-provider"
        self.name = "Integrated Algo-provider"
        self.alive = True

    def is_alive(self):
        return True

    def get_algorithms(self):
        """Get all algorithms that DebiAI can provide
        Returns:
            list: List of algorithms
        """

        # List the .py files if the algorithms folder
        algorithm_files = []
        for file in os.listdir(os.path.dirname(__file__) + "/algorithms"):
            if file.endswith(".py") and file != "__init__.py":
                algorithm_files.append(file[:-3])

        # Import the algorithms
        algorithms_python = []
        for file in algorithm_files:
            print("   Importing " + colored(file, DEBUG_COLOR))
            try:
                algorithms_python.append(_get_algorithm_python(file))
            except ModuleNotFoundError as e:
                print("Error importing " + file)
                print(e)

        # Get the algorithms (call the get_algorithm_details() function)
        algorithms = []
        for algorithm in algorithms_python:
            algorithm_details = algorithm[1].get_algorithm_details()
            # Add the id as the file name
            algorithm_details["id"] = algorithm[0]
            algorithms.append(algorithm_details)

        return algorithms

    def use_algorithm(self, algorithm_id, data):
        try:
            print("Using integrated algo-provider")
            print("Using algorithm: " + algorithm_id)
            algorithm = _get_algorithm_python(algorithm_id)

            # Use the algorithm
            outputs = algorithm[1].use_algorithm(data["inputs"])

            return outputs

        except TypeError as e:
            print("The integrated algo-provider returned an error")
            print(e)
            raise AlgoProviderException(
                algorithm_id + " returned an error: " + str(e), 400
            )
        except Exception as e:
            print("The integrated algo-provider returned an error")
            print(e)
            raise AlgoProviderException("AlgoProvider internal server error", 500)
