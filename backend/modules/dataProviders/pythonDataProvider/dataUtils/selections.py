import os
import ujson as json

from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    projects,
)

DATA_PATH = pythonModuleUtils.DATA_PATH

# Selections


def create_selection(project_id, selection_name, sample_ids, request_id=None):
    selection_id = pythonModuleUtils.clean_filename(selection_name)
    if len(selection_id) == 0:
        selection_id = pythonModuleUtils.timeNow()

    nbS = 1
    while selection_exist(project_id, selection_id):
        selection_id = pythonModuleUtils.clean_filename(selection_name) + "_" + str(nbS)
        nbS += 1

    # Save the selection
    selectionInfoFilePath = (
        DATA_PATH + project_id + "/selections/" + selection_id + "/info.json"
    )
    now = pythonModuleUtils.timeNow()

    selectionInfo = {
        "id": selection_id,
        "name": selection_name,
        "filePath": selectionInfoFilePath,
        "creationDate": now,
        "updateDate": now,
        "samples": sample_ids,
    }

    if request_id is not None:
        selectionInfo["requestId"] = request_id

    os.mkdir(DATA_PATH + project_id + "/selections/" + selection_id)
    pythonModuleUtils.writeJsonFile(selectionInfoFilePath, selectionInfo)
    projects.update_project(project_id)
    return selectionInfo


def get_selections(project_id):
    # Get selections
    selections = []
    for selection_id in get_selection_ids(project_id):
        selections.append(get_selection(project_id, selection_id))
    return selections


def get_selection_ids(project_id):
    return os.listdir(DATA_PATH + project_id + "/selections/")


def selection_exist(project_id, selectionId):
    return os.path.exists(DATA_PATH + project_id + "/selections/" + selectionId)


def get_selection(project_id, selectionId):
    with open(
        DATA_PATH + project_id + "/selections/" + selectionId + "/info.json"
    ) as json_file:
        data = json.load(json_file)
        ret = {
            "id": data["id"],
            "name": data["name"],
            "filePath": data["filePath"],
            "creationDate": data["creationDate"],
            "updateDate": data["updateDate"],
            "nbSamples": len(data["samples"]),
        }

        # Add the request Id if it exist
        if "requestId" in data:
            ret["requestId"] = data["requestId"]

        return ret


def get_selection_id_list(project_id, selectionId):
    if not selection_exist(project_id, selectionId):
        raise Exception("Selection " + selectionId + " doesn't exist")

    with open(
        DATA_PATH + project_id + "/selections/" + selectionId + "/info.json"
    ) as json_file:
        data = json.load(json_file)
        return data["samples"]


# def getSelectionsSamples(project_id, selectionIds: list, intersection: bool) -> set:
#     if len(selectionIds) == 0:
#         return []

#     samples = set(get_selection_id_list(project_id, selectionIds[0]))
#     for selectionId in selectionIds[1:]:
#         if intersection:  # intersection of the selections samples
#             samples.intersection_update(
#                 get_selection_id_list(project_id, selectionId))

#             if len(samples) == 0:
#                 return []
#         else:  # Union of the model results samples
#             samples = samples.union(
#                 get_selection_id_list(project_id, selectionId))

#     return samples


def delete_selection(project_id, selection_id):
    pythonModuleUtils.deleteDir(DATA_PATH + project_id + "/selections/" + selection_id)
    projects.update_project(project_id)
