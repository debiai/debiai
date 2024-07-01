import hashlib
import ujson as json

from backend.modules.dataProviders.pythonDataProvider.dataUtils import pythonModuleUtils

DATA_PATH = pythonModuleUtils.DATA_PATH


def hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# hash
def __createProjectHashMap(projectId, blockPath, hashmap, sampleLevel, currentLevel):
    blockPath += "/"
    if currentLevel == sampleLevel:
        # We are at the sample level, we can fill the hashmap
        sampleHash = hash(blockPath)
        hashmap[sampleHash] = blockPath

        # Update the sample
        pythonModuleUtils.updateJsonFile(
            DATA_PATH + projectId + "/blocks/" + blockPath + "info.json",
            "id",
            sampleHash,
        )
        return

    for children in pythonModuleUtils.listDir(
        DATA_PATH + projectId + "/blocks/" + blockPath
    ):
        __createProjectHashMap(
            projectId, blockPath + children, hashmap, sampleLevel, currentLevel + 1
        )


def addToSampleHashmap(projectId, hashMap):
    with open(DATA_PATH + projectId + "/samplesHashmap.json") as json_file:
        existingHm = json.load(json_file)

    existingHm.update(hashMap)

    pythonModuleUtils.writeJsonFile(
        DATA_PATH + projectId + "/samplesHashmap.json", existingHm
    )


def getHashmap(projectId):
    with open(DATA_PATH + projectId + "/samplesHashmap.json") as json_file:
        existingHm = json.load(json_file)

    return existingHm


def getPathFromHashList(projectId, hashArray):
    hm = getHashmap(projectId)
    ret = []
    for hash in hashArray:
        ret.append(hm[hash])
    return ret
