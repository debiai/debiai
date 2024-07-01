#############################################################################
# Imports
#############################################################################
from backend.modules.dataProviders.DataProviderException import DataProviderException
import backend.modules.dataProviders.dataProviderManager as data_provider_manager

#############################################################################
# PROJECTS Management
#############################################################################


def ping():
    return "Online", 200


def get_data_providers_project(dataProviderId):
    # Return a list of project overviews for a specific data provider
    data_provider = data_provider_manager.get_single_data_provider(dataProviderId)

    if data_provider is None:
        return "Data provider not found", 404

    try:
        projects = data_provider.get_projects()

        if projects is not None:
            # Adding data provider id to projects
            for project in projects:
                project["dataProviderId"] = data_provider.name

    except DataProviderException as e:
        print("Warning get DP projects : " + e.message)

    return projects, 200


def get_projects():
    # Return a list of project overviews from all the data providers
    data_providers_list = data_provider_manager.get_data_provider_list()
    projectOverviews = []
    for data_provider in data_providers_list:
        try:
            projects = data_provider.get_projects()

            if projects is not None:
                # Adding data provider id to projects
                for project in projects:
                    project["dataProviderId"] = data_provider.name

                projectOverviews.extend(projects)

        except DataProviderException as e:
            print("Warning get DP projects : " + e.message)

    return projectOverviews, 200


def get_project(dataProviderId, projectId):
    # return the info about datasets, models, selections & tags
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)

        project = data_provider.get_project(projectId)

        # Adding data provider id to project
        project["dataProviderId"] = dataProviderId

        return project, 200
    except DataProviderException as e:
        return e.message, e.status_code


def get_data_id_list(dataProviderId, projectId, requestParameters):
    # return the list of data ids
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)

        data_id_list = data_provider.get_id_list(
            projectId,
            requestParameters["analysis"],
            requestParameters["from"],
            requestParameters["to"],
        )

        return data_id_list, 200
    except DataProviderException as e:
        return e.message, e.status_code


def delete_project(dataProviderId, projectId):
    # Delete a project
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)

        data_provider.delete_project(projectId)
        return "Project deleted", 200
    except DataProviderException as e:
        return e.message, e.status_code
