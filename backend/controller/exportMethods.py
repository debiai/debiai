from backend.config.init_config import get_config
import backend.modules.exportMethods.exportUtils as exportUtils

#############################################################################
# Export API Management
#############################################################################


def get_export_methods():
    # ParametersCheck
    return exportUtils.get_export_methods(), 200


def post_export_method(data):
    # Check if the creation of export methods is allowed
    config = get_config()
    creation_allowed = config["EXPORT_METHODS_CONFIG"]["creation"]
    if not creation_allowed:
        return "Export method creation is not allowed", 403

    try:
        return exportUtils.add_export_method(data), 200
    except Exception as e:
        return str(e), 400


def delete_export_method(exportMethodId):
    # Check if the deletion of export methods is allowed
    config = get_config()
    deletion_allowed = config["EXPORT_METHODS_CONFIG"]["deletion"]
    if not deletion_allowed:
        return "Export method deletion is not allowed", 403

    try:
        return exportUtils.delete_export_method(exportMethodId), 200
    except Exception as e:
        return str(e), 400


def exportSelection(dataProviderId, projectId, data):
    try:
        return exportUtils.exportSelection(dataProviderId, projectId, data), 200
    except Exception as e:
        return str(e), 400


def exportData(exportMethodId, data):
    try:
        return exportUtils.exportData(exportMethodId, data), 200
    except Exception as e:
        return str(e), 400
