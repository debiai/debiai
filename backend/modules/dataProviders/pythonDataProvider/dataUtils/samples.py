from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    tree,
    hash,
)

DATA_PATH = pythonModuleUtils.DATA_PATH
DATA_TYPES = pythonModuleUtils.DATA_TYPES

# ID list


def get_all_samples_id_list(project_id, _from=None, _to=None):
    """
    Return a list of all samples id in a project
    """
    # Get the hashmap
    hashmap = hash.getHashmap(project_id)

    # Get all samples
    samples = list(hashmap.keys())

    # In case of streaming purpose
    if _from is not None and _to is not None:
        samples = samples[_from : _to + 1]  # noqa

    return samples


# Get data
def get_data_from_sample_id_list(project_id, id_list):
    # Get path of the samples from the hashmap
    sample_path = hash.getPathFromHashList(project_id, id_list)
    data = {}

    # We age going through each samples individually because of a bug
    # (the data aren't aligned with the requested samples id)
    # Because of this bug, we are slowing down the process
    # TODO : fix this bug
    for i in range(len(id_list)):
        # Get tree from samples
        samples_tree = tree.getBlockTreeFromSamples(project_id, [sample_path[i]])

        # Convert tree to array
        data_array = _tree_to_array(samples_tree)

        # Convert array to dict
        data[id_list[i]] = data_array[0]

    return data


def _tree_to_array(tree):
    data_array = []
    for block in tree:
        data_array += _block_to_array_recur(block)
    return data_array


def _get_block_values(block):
    # Adding the block name into the values
    values = [block["name"]]

    # store all key-values into an array
    for data_type in DATA_TYPES:
        if data_type in block:
            for key in range(len(block[data_type])):
                values.append(block[data_type][key])

    return values


def _block_to_array_recur(block):
    # Getting bloc values
    values = _get_block_values(block)
    if "childrenInfoList" not in block or len(block["childrenInfoList"]) == 0:
        return [values]

    else:
        # Getting all child values
        child_values = []
        for child_block in block["childrenInfoList"]:
            child_values += _block_to_array_recur(child_block)
            # child_values.append(_block_to_array_recur(child_block))

        # Child values : [[1,2,3], [4,5,6], [7,8,9]]
        # values : [10, 11, 12]
        # Goal: [[10, 11, 12, 1, 2, 3], [10, 11, 12, 4, 5, 6], [10, 11, 12, 7, 8, 9]]

        # Adding the block name into the values
        ret = [None] * len(child_values)

        # Adding the block values to the children values
        for i in range(len(child_values)):
            ret[i] = values + child_values[i]

        return ret


# def projectSamplesGenerator(projectId):
#     """
#     Generator used to iterate over all samples in a project.
#     Used by the 'createSelectionFromRequest' method
#     """

#     # Get the project block structure
#     projectBlockStructure = projects.get_project_block_level_info(projectId)
#     sampleLevel = len(projectBlockStructure) - 1

#     rootBlocks = utils.listDir(DATA_PATH + projectId + "/blocks/")
#     for rootBlock in rootBlocks:
#         path = DATA_PATH + projectId + "/blocks/" + rootBlock + "/"
#         yield from yieldSample(path,  0, [], sampleLevel, projectBlockStructure)
#     print("end")


# def yieldSample(path, level, sampleInfo, sampleLevel, blockLevelInfo):
#     # TODO : optimizations : add in parameters the block that we need to open
#     blockInfo = utils.readJsonFile(path + "info.json")
#     sampleInfo.append(getBlockInfo(blockLevelInfo[level], blockInfo))

#     if level == sampleLevel:
#         # merge the dict into one
#         yield {k: v for x in sampleInfo for k, v in x.items()}, blockInfo["id"]
#     else:
#         childrenBlockNames = utils.listDir(path)
#         for name in childrenBlockNames:
#             yield from yieldSample(path + name + "/",
#                                    level + 1, sampleInfo, sampleLevel, blockLevelInfo)
#             del sampleInfo[-1]
