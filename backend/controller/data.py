#############################################################################
# Imports
#############################################################################
import backend.modules.dataProviders.dataProviderManager as data_provider_manager
from backend.modules.dataProviders.DataProviderException import DataProviderException

#############################################################################
# Data Management
#############################################################################


def get_data(dataProviderId, projectId, data):
    # return a project data from a list of ids
    sampleIds = data["sampleIds"]
    analysis = data["analysis"]

    try:
        # Find the data provider
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)

        # Ask for the data
        samples = data_provider.get_samples(projectId, analysis, sampleIds)

        if samples is not None:
            return {
                "data": samples,
                "dataMap": True,
            }, 200

        return (
            "Can't find samples for project "
            + projectId
            + " on data provider : "
            + dataProviderId,
            404,
        )
    except DataProviderException as e:
        return e.message, e.status_code
