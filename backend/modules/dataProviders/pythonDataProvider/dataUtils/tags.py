import os
from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    hash,
)

DATA_PATH = pythonModuleUtils.DATA_PATH


def getTagsIds(projectId):
    try:
        return os.listdir(DATA_PATH + projectId + "/tags")
    except FileNotFoundError:
        os.mkdir(DATA_PATH + projectId + "/tags")
        return []


def getTags(projectId):
    tagIds = getTagsIds(projectId)
    tags = []
    for tagId in tagIds:
        tag = getTagById(projectId, tagId)
        # Get the number of sample tagged
        tag["nbSamples"] = len(tag["tags"].keys())
        # remove the tag values
        tag.pop("tags", None)
        tags.append(tag)
    return tags


def getTagById(projectId, tagId):
    if tagId not in getTagsIds(projectId):
        return None

    return pythonModuleUtils.readJsonFile(
        DATA_PATH + projectId + "/tags/" + tagId + "/info.json"
    )


def getTagByName(projectId, tagName):
    for tagId in getTagsIds(projectId):
        tag = getTagById(projectId, tagId)
        if tag["name"] == tagName:
            return tag
    return None


def updateTag(projectId, tagName, tagHash):
    # TODO change to tagId
    # ParametersCheck
    projectHashMap = hash.getHashmap(projectId)

    for sampleHash in tagHash.keys():
        if sampleHash not in projectHashMap:
            return "SampleHash not found in the project samples", 404

    tag = getTagByName(projectId, tagName)
    if tag:
        # Update tag
        for sampleHash in tagHash.keys():
            if tagHash[sampleHash] == 0:
                tag["tags"].pop(sampleHash, None)
            else:
                tag["tags"][sampleHash] = tagHash[sampleHash]

        tag["updateDate"] = pythonModuleUtils.timeNow()
        pythonModuleUtils.writeJsonFile(
            DATA_PATH + projectId + "/tags/" + tag["id"] + "/info.json", tag
        )
        return tag, 200
    else:
        # Create tag
        # tag ID
        tagId = pythonModuleUtils.clean_filename(tagName)
        if len(tagId) == 0:
            tagId = pythonModuleUtils.timeNow()

        nbTag = 1
        while tagId in getTagsIds(projectId):
            tagId = pythonModuleUtils.clean_filename(tagName) + "_" + str(nbTag)
            nbTag += 1

        # Save tag
        os.mkdir(DATA_PATH + projectId + "/tags/" + tagId)
        now = pythonModuleUtils.timeNow()
        tagInfo = {
            "id": tagId,
            "name": tagName,
            "tags": tagHash,
            "creationDate": now,
            "updateDate": now,
        }

        pythonModuleUtils.writeJsonFile(
            DATA_PATH + projectId + "/tags/" + tagId + "/info.json", tagInfo
        )

        return tagInfo, 200


def deleteTag(projectId, tagId):
    pythonModuleUtils.deleteDir(DATA_PATH + projectId + "/tags/" + tagId)


def getSamplesHash(projectId, tagId, tagValue):
    tag = getTagById(projectId, tagId)
    hash = []
    for sampleHash in tag["tags"].keys():
        if tag["tags"][sampleHash] == tagValue:
            hash.append(sampleHash)

    return hash
