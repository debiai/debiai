import os
import shutil
import ujson as json

from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    hash,
)

DATA_PATH = pythonModuleUtils.DATA_PATH


def project_exist(projectId):
    return projectId in os.listdir(DATA_PATH)


def _get_project_info(projectId):
    file_path = DATA_PATH + projectId + "/info.json"
    if not os.path.exists(file_path):
        delete_project(projectId)
        raise Exception("The project info file is missing")

    with open(file_path) as json_file:
        data = json.load(json_file)

    if "name" not in data:
        delete_project(projectId)
        raise Exception("The project name is missing from the info.json file")
    if "creationDate" not in data:
        delete_project(projectId)
        raise Exception("The project creationDate is missing from the info.json file")
    if "updateDate" not in data:
        delete_project(projectId)
        raise Exception("The project updateDate is missing from the info.json file")

    return data


def get_project(projectId):
    try:
        # Get info file
        data = _get_project_info(projectId)
        name = data["name"]
        creationDate = data["creationDate"]
        updateDate = data["updateDate"]

        # Nb models
        if not os.path.exists(DATA_PATH + projectId + "/models/"):
            raise Exception('The "models" folder is missing')

        nbModels = len(os.listdir(DATA_PATH + projectId + "/models/"))

        # Nb selection
        if not os.path.exists(DATA_PATH + projectId + "/selections/"):
            raise Exception('The "selections" folder is missing')

        nbSelection = len(os.listdir(DATA_PATH + projectId + "/selections/"))

        # Nb samples
        if not os.path.exists(DATA_PATH + projectId + "/samplesHashmap.json"):
            raise Exception('The "samplesHashmap.json" file is missing')

        nbSamples = len(hash.getHashmap(projectId))

        # project columns
        projectColumns = get_project_columns(projectId)

        # project block level
        # We still need to get the project block level, the Python module use it
        projectBlockLevel = get_project_block_level_info(projectId)

        projectOverview = {
            "id": projectId,
            "name": name,
            "nbModels": nbModels,
            "nbSelections": nbSelection,
            "nbSamples": nbSamples,
            "creationDate": creationDate,
            "updateDate": updateDate,
            "columns": projectColumns,
            "blockLevelInfo": projectBlockLevel,
        }

    except Exception as e:
        print("Error while getting the project overview: " + projectId)
        print(e)
        projectOverview = {
            "id": projectId,
            "name": projectId,
        }

    return projectOverview


def get_projects():
    project = []

    for projectId in os.listdir(DATA_PATH):
        project.append(get_project(projectId))

    return project


def create_project(projectId, projectName):
    # Create the project files and folders
    os.mkdir(DATA_PATH + projectId)
    os.mkdir(DATA_PATH + projectId + "/blocks")
    os.mkdir(DATA_PATH + projectId + "/models")
    os.mkdir(DATA_PATH + projectId + "/selections")

    now = pythonModuleUtils.timeNow()
    projectInfo = {
        "name": projectName,
        "id": projectId,
        "creationDate": now,
        "updateDate": now,
        "blockLevelInfo": [],
    }

    pythonModuleUtils.writeJsonFile(DATA_PATH + projectId + "/info.json", projectInfo)
    pythonModuleUtils.writeJsonFile(DATA_PATH + projectId + "/samplesHashmap.json", {})

    return projectInfo


def update_project(projectId):
    # Change the update date of the project to now
    pythonModuleUtils.updateJsonFile(
        DATA_PATH + projectId + "/info.json", "updateDate", pythonModuleUtils.timeNow()
    )


def get_project_block_level_info(projectId):

    data = _get_project_info(projectId)
    if "blockLevelInfo" in data:
        return data["blockLevelInfo"]


def get_project_columns(projectId):
    block_level_info = get_project_block_level_info(projectId)

    # Convert the block level info to the new columns format
    #   blockLevelInfo:
    #   [
    #     { "name": "block1" },
    #     {
    #       "name": "block2",
    #       "contexts": [
    #           { "name": "cont1", "type": "text", group:"group_1" },
    #           { "name": "cont2", "type": "text", group:"group_1" },
    #       ]
    #     },
    #     { "name": "block3", "contexts": [
    #           { "name": "cont3", "type": "text", group:"group_1" }
    #        ]
    #     },
    #     {
    #       "name": "block4",
    #       "others": [{ "name": "other1", "type": "number" }],
    #       "groundTruth": [
    #           { "name": "gdt1", "type": "number" },
    #           { "name": "gdt2", "type": "number" },
    #       ],
    #       "inputs": [
    #           { "name": "inp1", "type": "number" }
    #       ]
    #     }
    # ]

    # Goal format:
    # [
    #   { "name": "block1", "category": "other", "type": "auto" },
    #   { "name": "block2", "category": "other", "type": "auto" },
    #   { "name": "cont1", "category": "context", "type": "text", group: "group_1" },
    #   { "name": "cont2", "category": "context", "type": "text", group: "group_1" },
    #   { "name": "cont3", "category": "context", "type": "text", group: "group_1" },
    #   { "name": "block3", "category": "other", "type": "auto" },
    #   { "name": "other1", "category": "other", "type": "number" },
    #   { "name": "block4", "category": "other", "type": "auto" },
    #   { "name": "gdt1", "category": "groundtruth", "type": "number" },
    #   { "name": "gdt2", "category": "groundtruth", "type": "number" },
    #   { "name": "inp1", "category": "input", "type": "number" },
    # ]

    project_columns = []

    def create_column(col, category):
        column = {"name": col["name"], "category": category, "type": col["type"]}

        if "group" in col:
            column["group"] = col["group"]

        return column

    for block in block_level_info:
        block_name = block["name"]
        project_columns.append(
            {"name": block_name, "category": "other", "type": "auto"}
        )

        if "groundTruth" in block:
            for ground_truth in block["groundTruth"]:
                project_columns.append(create_column(ground_truth, "groundtruth"))

        if "contexts" in block:
            for context in block["contexts"]:
                project_columns.append(create_column(context, "context"))

        if "inputs" in block:
            for input in block["inputs"]:
                project_columns.append(create_column(input, "input"))

        if "others" in block:
            for other in block["others"]:
                project_columns.append(create_column(other, "other"))

    return project_columns


def get_result_structure(projectId):
    data = _get_project_info(projectId)
    if "resultStructure" in data:
        return data["resultStructure"]
    else:
        return None


def delete_project(projectId):
    # Delete the project files and folders
    try:
        shutil.rmtree(DATA_PATH + projectId)
    except Exception as e:
        print(e)
        raise "Something went wrong when deleting the project"


def update_block_structure(projectId, blockStructure):
    try:
        pythonModuleUtils.updateJsonFile(
            DATA_PATH + projectId + "/info.json", "blockLevelInfo", blockStructure
        )

        update_project(projectId)
    except Exception as e:
        print(e)
        raise Exception("Something went wrong updating project structure")


def update_results_structure(projectId, resultStructure):
    try:
        # save resultStructure
        pythonModuleUtils.updateJsonFile(
            DATA_PATH + projectId + "/info.json", "resultStructure", resultStructure
        )
        update_project(projectId)
        return resultStructure, 200

    except Exception as e:
        print(e)
        raise "Something went wrong updating project structure"
