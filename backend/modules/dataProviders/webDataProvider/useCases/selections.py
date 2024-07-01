import backend.modules.dataProviders.webDataProvider.http.api as api
from backend.modules.dataProviders.DataProviderException import DataProviderException


def get_project_selections(url, project_id):
    try:
        selections = api.get_selections(url, project_id)

        if selections is None:
            print(f"Error: No selections found for project {project_id} on {url}")
            raise DataProviderException("No selections found", 404)

        debiai_selections = []
        for selection in selections:
            if "id" not in selection or selection["id"] is None:
                print(f"Error: No id for selection: {selection}")
                raise DataProviderException(
                    "An id is missing in the given selection", 400
                )

            selection_to_add = {
                "name": selection["name"] if "name" in selection else selection["id"],
                "id": selection["id"],
            }

            if "nbSamples" in selection:
                selection_to_add["nbSamples"] = selection["nbSamples"]
            if "creationDate" in selection:
                selection_to_add["creationDate"] = selection["creationDate"]
            if "updateDate" in selection:
                selection_to_add["updateDate"] = selection["updateDate"]
            if "metadata" not in selection:
                selection_to_add["metadata"] = None
            else:
                selection_to_add["metadata"] = selection["metadata"]

            debiai_selections.append(selection_to_add)
        return debiai_selections

    except DataProviderException:
        # The route may not be implemented in the data provider
        return []


def get_id_list_from_selection(url, cache, project_id, selection_id):
    id_list = cache.get_selection_id_list(project_id, selection_id)

    if id_list is None:
        id_list = api.get_selection_id(url, project_id, selection_id)
        cache.set_selection_id_list(project_id, selection_id, id_list)

    return id_list


def create_selection(url, project_id, name, id_list, request_id):
    data = {"idList": id_list, "name": name}

    if request_id is not None:
        data["request"]: request_id

    return api.post_selection(url, project_id, data)


def delete_selection(url, project_id, selection_id):
    return api.delete_selection(url, project_id, selection_id)
