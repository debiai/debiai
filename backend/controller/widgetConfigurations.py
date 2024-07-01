#############################################################################
# Imports
#############################################################################
import backend.utils.widgetConfigurations.widgetConfigurations as widgetConfUtils

#############################################################################
# Widget configuration Management
#############################################################################


def get_all_configurations():
    configurations_overview = widgetConfUtils.get_configurations_overview()
    return configurations_overview, 200


def get_widget_configurations(widgetKey):
    configurations = widgetConfUtils.get_configurations(widgetKey)
    return configurations, 200


def post_configuration(widgetKey, data):
    widgetConfUtils.add_configuration(widgetKey, data)
    return None, 204


def delete_configuration(widgetKey, id):
    widgetConfUtils.delete_configuration(widgetKey, id)
    return None, 204
