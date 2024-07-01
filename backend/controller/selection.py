#############################################################################
# Imports
#############################################################################

import backend.modules.dataProviders.dataProviderManager as data_provider_manager
from backend.modules.dataProviders.DataProviderException import DataProviderException

#############################################################################
# Selections Management
#############################################################################


def get_selections(dataProviderId, projectId):
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        return data_provider.get_selections(projectId), 200
    except DataProviderException as e:
        return e.message, e.status_code


def get_selection_id_list(dataProviderId, projectId, selectionId):
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        return data_provider.get_selection_id_list(projectId, selectionId), 200
    except DataProviderException as e:
        return e.message, e.status_code


def post_selection(dataProviderId, projectId, data):
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        data_provider.create_selection(
            projectId,
            data["selectionName"],
            data["sampleHashList"],
            data["requestId"] if "requestId" in data else None,
        )
        return "Selection added", 200
    except DataProviderException as e:
        return e.message, e.status_code


def delete_selection(dataProviderId, projectId, selectionId):
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        data_provider.delete_selection(projectId, selectionId)
        return "Selection deleted", 200
    except DataProviderException as e:
        return e.message, e.status_code
