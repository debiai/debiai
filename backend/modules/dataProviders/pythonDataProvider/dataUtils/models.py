import os
import ujson as json
from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    projects,
    tree,
)
from backend.modules.dataProviders.DataProviderException import DataProviderException

DATA_PATH = pythonModuleUtils.DATA_PATH


#  Models
def get_model_ids(project_id):
    return os.listdir(DATA_PATH + project_id + "/models/")


def get_models(project_id):
    ret = []
    for model in os.listdir(DATA_PATH + project_id + "/models/"):
        with open(
            DATA_PATH + project_id + "/models/" + model + "/info.json"
        ) as json_file:
            info = json.load(json_file)
            ret.append(
                {
                    "name": model,
                    "id": model,
                    "creationDate": info["creationDate"],
                    "updateDate": info["updateDate"],
                    "version": "0.0.0",
                    "metadata": info["metadata"],
                    "nbResults": info["nbResults"],
                }
            )

    return ret


def model_exist(project_id, model_id):
    return model_id in get_model_ids(project_id)


def create_model(project_id, model_name, metadata=None):
    # ParametersCheck
    if not pythonModuleUtils.is_filename_clean(model_name):
        raise DataProviderException("Model name contain invalid characters", 402)

    model_id = model_name

    if model_exist(project_id, model_id):
        raise DataProviderException("Model " + model_id + " already exists", 409)

    if metadata is None:
        metadata = {}

    # model
    modelFolderPath = DATA_PATH + project_id + "/models/" + model_id
    os.mkdir(modelFolderPath)

    now = pythonModuleUtils.timeNow()

    model_info = {
        "name": model_id,
        "id": model_id,
        "creationDate": now,
        "updateDate": now,
        "metadata": metadata,
        "nbResults": 0,
    }

    pythonModuleUtils.writeJsonFile(modelFolderPath + "/info.json", model_info)

    # Add 0 results to init the file
    write_model_results(project_id, model_id, {})


def delete_model(project_id, model_id):
    pythonModuleUtils.deleteDir(DATA_PATH + project_id + "/models/" + model_id)


def write_model_results(project_id, model_id, results):
    pythonModuleUtils.writeJsonFile(
        DATA_PATH + project_id + "/models/" + model_id + "/results.json", results
    )
    projects.update_project(project_id)


def get_model_results(project_id, model_id, sample_ids):
    # Check parameters
    if not projects.project_exist(project_id):
        raise ("Project '" + project_id + "' doesn't exist")
    if not model_exist(project_id, model_id):
        raise ("Model " + model_id + " does not exist")

    # Get model results
    with open(
        DATA_PATH + project_id + "/models/" + model_id + "/results.json", "r"
    ) as jsonFile:
        model_results = json.load(jsonFile)

    # if not selection_id:
    # return d
    # else:
    # selectionSamples = set(
    #     selections.getSelectionSamples(project_id, selection_id))
    # return selectionSamples.intersection_update(d)
    #     model_results = getModelResults(project_id, model_id)

    ret = {}
    for sample_id in sample_ids:
        if sample_id in model_results:
            ret[sample_id] = model_results[sample_id]
        # Not sending error if sample not found in model results at the moment
        # else:
        #     raise ValueError("Sample " + sample_id +
        #                      " not found in model results")
    return ret


def get_model_id_list(project_id, model_id) -> list:
    # Get model results
    with open(
        DATA_PATH + project_id + "/models/" + model_id + "/results.json", "r"
    ) as jsonFile:
        model_results = json.load(jsonFile)
        return dict.keys(model_results)


# def get_model_list_results(project_id, model_ids: list, common: bool) -> list:
#     samples = set(get_model_results(project_id, model_ids[0]))

#     for model_id in model_ids[1:]:
#         if common:  # Common samples between models
#             samples.intersection_update(
#                 get_model_results(project_id, model_id))
#         else:  # Union of the model results samples
#             samples = samples.union(get_model_results(project_id, model_id))

#     return list(samples)


def add_results_dict(project_id, modelId, data):
    tree = data["results"]

    # Check parameters
    if not projects.project_exist(project_id):
        raise "Project '" + project_id + "' doesn't exist"

    if not model_exist(project_id, modelId):
        raise (
            "Model '" + modelId + "' in project : '" + project_id + "' doesn't exist"
        )

    # Get resultStructure & project_block_structure
    result_structure = projects.get_result_structure(project_id)
    if result_structure is None:
        raise (
            "The project expected results need to be specified before adding results"
        )

    if "expected_results_order" in data:
        expected_results_order = data["expected_results_order"]
    else:
        expected_results_order = list(map(lambda r: r["name"], result_structure))

    project_block_structure = projects.get_project_block_level_info(project_id)
    sampleIndex = len(project_block_structure) - 1

    # Check the given expected_results_order
    for expected_result in result_structure:
        if expected_result["name"] not in expected_results_order:
            raise (
                "The expected result '"
                + expected_result["name"]
                + "' is missing from the expected_results_order Array"
            )

    giv_exp_res = {}
    for given_expected_result in expected_results_order:
        result_expected = False
        for i, expected_result in enumerate(result_structure):
            if given_expected_result == expected_result["name"]:
                result_expected = True

                # Map the expected_results_order indexes to result_structure
                giv_exp_res[given_expected_result] = i

        if not result_expected:
            return (
                "The given expected result '"
                + given_expected_result
                + "' is not an expected result",
                403,
            )

    #  Check if all blocks referenced in the result tree exists
    resultsToAdd = {}

    for blockKey in tree:
        ok, msg = __check_blocks_of_tree_exists(
            project_id,
            result_structure,
            giv_exp_res,
            tree[blockKey],
            0,
            sampleIndex,
            blockKey,
            resultsToAdd,
        )
        if not ok:
            print(msg)
            return msg, 403

    # The given tree is compliant, let's add the results
    newResults = pythonModuleUtils.addToJsonFIle(
        DATA_PATH + project_id + "/models/" + modelId + "/results.json", resultsToAdd
    )

    pythonModuleUtils.addToJsonFIle(
        DATA_PATH + project_id + "/models/" + modelId + "/info.json",
        {"nbResults": len(newResults), "updateDate": pythonModuleUtils.timeNow()},
    )
    projects.update_project(project_id)
    return 200


def __check_blocks_of_tree_exists(
    project_id: str,
    result_structure: list,
    giv_exp_res: dict,
    block: dict,
    level: int,
    sampleIndex: int,
    path: str,
    resultsToAdd: dict,
):
    # Check block exist in the data
    blockInfo = tree.findBlockInfo(project_id, path)
    if not blockInfo:
        return (
            False,
            "Error while adding the results : block '" + path + "' doesn't exist",
        )

    if level == sampleIndex:
        path += "/"
        resultsToAdd[blockInfo["id"]] = []
        #  Sample level : the results : they need to be verified
        if len(block) != len(giv_exp_res):
            raise ValueError(
                "in : "
                + path
                + ", "
                + str(len(block))
                + " value where given but "
                + str(len(giv_exp_res))
                + "where expected"
            )

        for result in result_structure:
            resultsToAdd[blockInfo["id"]].append(block[giv_exp_res[result["name"]]])
            # TODO Deal with defaults results and check type

        return True, None

    for subBlockKey in block:
        ok, msg = __check_blocks_of_tree_exists(
            project_id,
            result_structure,
            giv_exp_res,
            block[subBlockKey],
            level + 1,
            sampleIndex,
            path + "/" + str(subBlockKey),
            resultsToAdd,
        )
        if not ok:
            return False, msg

    return True, ""
