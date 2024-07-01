import ujson as json
import os

from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    projects,
    models,
    hash,
)

DATA_PATH = pythonModuleUtils.DATA_PATH
DATA_TYPES = pythonModuleUtils.DATA_TYPES

# def getFirstLevelBlock(projectId, blockId):
#     blockList = os.listdir(DATA_PATH + projectId + '/blocks')

#     if (blockId not in blockList):
#         return -1

#     with open(DATA_PATH + projectId + '/blocks/' + blockId + '/info.json')\
#             as json_file:
#         data = json.load(json_file)

#     return data


# def getBlockTree(projectId, path, depth):

#     childrenBlockNames = utils.listDir(path)
#     childrenInfo = []

#     if depth > 0:
#         # Get the children blocks info
#         for name in childrenBlockNames:
#             childrenInfo.append(getBlockTree(
#                 projectId, path + name + "/", depth - 1))

#     with open(path + 'info.json') as json_file:
#         data = json.load(json_file)
#         data['childrenInfoList'] = childrenInfo

#     return data


def add_block_tree(projectId, data):
    # Loading project block info
    bli = projects.get_project_block_level_info(projectId)

    # going through the tree to check for error, store the block to add
    blockToAdd = []

    try:
        for block in data["blockTree"]:
            addBlockTree(projectId, block, bli, blockToAdd, 0, "")
    except KeyError as e:
        print(str(e))
        print("badInputTree")
        return str(e), 403

    if len(blockToAdd) == 0:
        return "No block added", 201

    # Store the blocks and the hash map
    sampleLevel = len(bli) - 1
    hashToSave = {}
    for block in blockToAdd:
        if block["level"] == sampleLevel:
            # Sample level, creating hash
            sampleHash = hash.hash(block["path"])
            block["id"] = sampleHash
            hashToSave[sampleHash] = block["path"]

        addBlock(projectId, block)

    # Save hashmap
    hash.addToSampleHashmap(projectId, hashToSave)

    projects.update_project(projectId)
    return str(len(blockToAdd)) + " added blocks"


def getBlockInfo(blockLevel, blockInfo):
    """
    Convert the block info to fill the sampleInfo list with a colonName:value dict
    """
    print("get block info")
    print(blockLevel)
    print(blockInfo)
    ret = {}
    ret[blockLevel["name"]] = blockInfo["name"]

    for dataType in pythonModuleUtils.DATA_TYPES:
        if dataType in blockLevel:
            for i, column in enumerate(blockLevel[dataType]):
                ret[column["name"]] = blockInfo[dataType][i]

    return ret


def getBlockTreeFromSamples(projectId, samples: list):
    blocksData = []
    addedBlocks = []

    for samplePath in samples:
        try:
            sampleBlocksData, endLevel = __getBlockTreeFromSample(
                projectId, samplePath, addedBlocks
            )

            if endLevel == 0:
                # root block, should be here after added the first sample
                blocksData.append(sampleBlocksData)
            else:
                # Not a root block, we need to find where to insert it
                # First, find the root
                cur = next(
                    block
                    for block in blocksData
                    if block["path"] in sampleBlocksData["path"]
                )

                # Then, find the level
                for i in range(0, endLevel - 1):
                    cur = next(
                        child
                        for child in cur["childrenInfoList"]
                        if child["path"] in sampleBlocksData["path"]
                    )

                cur["childrenInfoList"].append(sampleBlocksData)
        except StopIteration:
            # TODO : Find why this happens of certain projects
            print("Warning, the sample " + samplePath + " doesn't have a root block")

    return blocksData


def __getBlockTreeFromSample(projectId, blockPath, addedBlocks):
    """
    Go from the bottom to the top of a tree
    if at the top or, if block already added, return

    """
    # Add the block we are in
    addedBlocks.append(blockPath)

    with open(
        DATA_PATH + projectId + "/blocks/" + blockPath + "/info.json"
    ) as sampleData:
        info = json.load(sampleData)

    if info["level"] == 0:
        # Top of the tree, end of the recursively
        return info, 0

    if info["parentPath"] in addedBlocks:
        # The block to the top is already added, there is no need to go further
        return info, info["level"]

    # Climbing up the tree of one level
    parentInfo, endLevel = __getBlockTreeFromSample(
        projectId, info["parentPath"], addedBlocks
    )

    # Let's add our info to the parents
    cur = parentInfo

    for i in range(endLevel, info["level"] - 1):
        cur = cur["childrenInfoList"][0]
    cur["childrenInfoList"] = [info]

    return parentInfo, endLevel


def addResultsToTree(projectId, tree: list, modelIds: list, commonOnly: bool) -> dict:
    """
    Add, in the tree samples, the results from a model id list
    """

    # Load all the model results
    modelResults = {}
    for modelId in modelIds:
        modelResults[modelId] = models.getModelResults(projectId, modelId)

    # Get the project block structure
    proBs = projects.get_project_block_level_info(projectId)
    sampleLevel = len(proBs) - 1

    # Add in the samples the results
    for rootBlock in tree:
        __addResultsToABlock(rootBlock, modelResults, sampleLevel, commonOnly)

    return tree


def __addResultsToABlock(block, modelResults, sampleLevel, commonOnly):
    if block["level"] == sampleLevel:
        # Adding the results to the sample
        block["results"] = {}
        for modelId in modelResults:
            # If no more than 1 model and commonOnly, no need to check if
            # sample exist in tree
            if (
                commonOnly
                or len(modelResults) == 1
                or block["path"] in modelResults[modelId]
            ):
                block["results"][modelId] = modelResults[modelId][block["path"]]
        return

    for child in block["childrenInfoList"]:
        __addResultsToABlock(child, modelResults, sampleLevel, commonOnly)


# Add samples to a tree
def addBlockTree(projectId, block, blockLevelInfo, blockToAdd, level, parentPath):
    __checkBlockCompliant(block, level, blockLevelInfo)

    # check if block exist
    data = findBlockInfo(projectId, parentPath + block["name"])
    if data is None:
        # BLock doesn't exist
        blockToAdd.append(__createBlock(projectId, block, level, parentPath))

    path = parentPath + block["name"] + "/"

    if level < len(blockLevelInfo) - 1:
        for child in block["childrenInfoList"]:
            addBlockTree(projectId, child, blockLevelInfo, blockToAdd, level + 1, path)


def findBlockInfo(projectId, blockPath):
    curPath = DATA_PATH + projectId + "/blocks/" + blockPath

    if not os.path.isdir(curPath):
        return None

    with open(curPath + "/info.json", "r") as json_file:
        data = json.load(json_file)

    return data


def __checkBlockCompliant(block, level, blockLevelInfo):
    # Check if a block is correct (name exist, levelInfo coherence, etc)

    if "name" not in block:
        raise KeyError("A block at level " + str(level) + " is missing his name")

    # TODO check name valid (no / & .)

    if "childrenInfoList" not in block and level < (len(blockLevelInfo) - 1):
        raise KeyError(
            "Block : " + block["name"] + " has no childrenInfoList properties"
        )

    if level < len(blockLevelInfo) - 1 and len(block["childrenInfoList"]) == 0:
        raise KeyError(
            "Block : "
            + block["name"]
            + " has no child block, the tree need to be complete"
        )

    levelInfo = blockLevelInfo[level]

    for type_ in DATA_TYPES:
        if type_ in levelInfo and len(levelInfo[type_]) > 0:
            if type_ not in block:
                raise KeyError(
                    "At least one value of type "
                    + type_
                    + " is required in the block : "
                    + levelInfo["name"]
                )

            if len(block[type_]) != len(levelInfo[type_]):
                raise KeyError(
                    "Exactly "
                    + str(len(levelInfo[type_]))
                    + " "
                    + type_
                    + " required in the block : "
                    + levelInfo["name"]
                )

            # TODO Implement column default

            for i, col in enumerate(levelInfo[type_]):
                if col["type"] == "integer" and type(block[type_][i]) is str:
                    raise KeyError(
                        "Col "
                        + col["name"]
                        + " require an integer in the block : "
                        + levelInfo["name"]
                    )


def __createBlock(projectId, block, level, parentPath):
    blockPath = parentPath + block["name"] + "/"

    debiaiBlock = {
        "id": block["name"],
        "name": block["name"],
        "path": blockPath,
        "parentPath": parentPath,
        "level": level,
        # "creationDate": str(date.today()),
        # "updateDate": str(date.today()),
        # "version": "0.0.0",
        # "metaDataList": {},
    }

    for type_ in DATA_TYPES:
        if type_ in block:
            debiaiBlock[type_] = block[type_]

    return debiaiBlock


def addBlock(projectId, block):
    # create the block folder and his info.json file
    try:
        os.mkdir(DATA_PATH + projectId + "/blocks/" + block["path"])
        pythonModuleUtils.writeJsonFile(
            DATA_PATH + projectId + "/blocks/" + block["path"] + "/info.json", block
        )
    except FileExistsError:
        print(
            "Warning : The block "
            + block["path"]
            + " already exist, this is not supposed to append"
        )
