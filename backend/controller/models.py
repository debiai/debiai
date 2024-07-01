#############################################################################
# Imports
#############################################################################

import backend.modules.dataProviders.dataProviderManager as data_provider_manager
from backend.modules.dataProviders.DataProviderException import DataProviderException

#############################################################################
# MODELS Management
#############################################################################


def get_model_id_list(dataProviderId, projectId, modelId):
    """
    Get the list of models for a project
    """
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        return list(data_provider.get_model_results_id_list(projectId, modelId)), 200
    except DataProviderException as e:
        return e.message, e.status_code


def get_results(dataProviderId, projectId, modelId, data):
    """
    Get the model results from a sample list
    """
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        return (
            data_provider.get_model_results(projectId, modelId, data["sampleIds"]),
            200,
        )
    except DataProviderException as e:
        return e.message, e.status_code


def post_model(dataProviderId, projectId, data):
    # Create a new model
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        data_provider.create_model(projectId, data)
        return "model created", 200
    except DataProviderException as e:
        return e.message, e.status_code


def delete_model(dataProviderId, projectId, modelId):
    """
    Delete a model
    """
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        return data_provider.delete_model(projectId, modelId), 200
    except DataProviderException as e:
        return e.message, e.status_code
