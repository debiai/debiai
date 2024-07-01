from backend.config.init_config import get_config
import backend.modules.dataProviders.dataProviderManager as data_provider_manager
from backend.modules.dataProviders.DataProviderException import DataProviderException
import time

from backend.modules.exportMethods.methods.kafkaUtils import KafkaExportType
from backend.modules.exportMethods.methods.postUtils import PostExportType

#############################################################################
#
# Export utils
#
# DebiAI allows to export data or selections to other services with
# different methods.
# This utils load and store the methods for all the projects
#
#############################################################################

# The export types are the different types of export methods that we can create
# They are used to create the export methods
export_types = [KafkaExportType(), PostExportType()]

# The export methods are the different methods created from the types
# They we can used to export data
export_methods = []


# Export types
def get_export_type(typeName):
    return [type for type in export_types if type.name == typeName][0]


def type_exist(typeName):
    return typeName in [type.name for type in export_types]


# Export utils
def get_export_methods():
    # Return all the export methods as a list of dictionaries
    return [method.to_dict() for method in export_methods]


def get_export_method(methodId):
    # Check the method id
    if not method_exist(methodId):
        raise Exception("Export method " + methodId + " not found")

    return [method for method in export_methods if method.id == methodId][0]


def method_exist(methodId):
    return methodId in [method.id for method in export_methods]


def load_export_methods():
    global export_methods
    print("================== EXPORT METHODS ==================")

    # Load the export methods from the config file
    config = get_config()

    if "EXPORT_METHODS_LIST" in config:
        print(" - Loading export methods from config file")
        config_export_methods = config["EXPORT_METHODS_LIST"]

        for method in config_export_methods:
            print(
                "     Adding method " + method, "[", config_export_methods[method], "]"
            )

            try:
                parameters = config_export_methods[method].split(",")
                if len(parameters) == 0:
                    raise "method " + method + " has no parameters, aborting"

                # Trim parameters
                for i in range(len(parameters)):
                    parameters[i] = "".join(parameters[i].rstrip().lstrip())

                export_type_name = parameters[0]
                export_method = create_export_method(
                    method, export_type_name, parameters[1:]
                )

                if config["EXPORT_METHODS_CONFIG"]["deletion"]:
                    # The export method created from the config file are deletable
                    export_method.deletable = True

                export_methods.append(export_method)
            except Exception as e:
                print("Error while configuring method " + method + ": " + str(e))

    if len(export_methods) == 0:
        print("   No export method configured")


def add_export_method(data):
    # Check the method type
    if not type_exist(data["type"]):
        raise Exception("Method type " + data["type"] + " not found")

    export_method = create_export_method(data["name"], data["type"], data["parameters"])

    config = get_config()
    if config["EXPORT_METHODS_CONFIG"]["deletion"]:
        # The export method created from the config file are deletable
        export_method.deletable = True

    export_methods.append(export_method)

    return export_method.to_dict()


def create_export_method(name, type, parameters):
    # Check the method type
    if not type_exist(type):
        raise Exception(
            "Export type '"
            + type
            + "' isn't supported, only "
            + str([type.name for type in export_types])
            + " are supported"
        )

    # Get the export type
    export_type = get_export_type(type)

    # Create the method
    return export_type.export_method_class(name, parameters)


def delete_export_method(method_id):
    global export_methods

    # Check the method id
    if not method_exist(method_id):
        raise Exception("The export method wasn't found")

    # Delete the method
    export_methods = [method for method in export_methods if method.id != method_id]
    return "method " + method_id + " deleted"


# Export data
def exportSelection(dataProviderId, projectId, data):
    method_id = data["exportMethodId"]

    # Check the method id
    if not method_exist(method_id):
        raise Exception("method " + method_id + " not found")

    export_method = get_export_method(method_id)

    # Creation of the data selection to export
    try:
        data_provider = data_provider_manager.get_single_data_provider(dataProviderId)
        project = data_provider.get_project(projectId)
    except DataProviderException as e:
        return e.message, e.status_code

    id_list = []

    for id in data["sampleHashList"]:
        id_list.append({"id": id})

    data_to_export = {
        "origin": "DebiAI",
        "type": "selection",
        "projectId": projectId,
        "data_provider_id": dataProviderId,
        "selection_name": data["selectionName"],
        "date": time.time(),
        "sample_ids": id_list,
    }

    # Project name
    if "name" in project:
        data_to_export["project_name"] = project["name"]

    # Annotation extra value
    if "annotationValue" in data and data["annotationValue"] != "":
        data_to_export["value"] = data["annotationValue"]

    # Export the data
    export_method.export(data_to_export)

    return "data exported"


def exportData(method_id, data):
    # Check the method id
    if not method_exist(method_id):
        raise Exception("method " + method_id + " not found")

    export_method = get_export_method(method_id)

    # Export the data
    export_method.export(data)

    return "data exported"
