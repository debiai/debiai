#############################################################################
# Imports
#############################################################################
import backend.utils.layouts.layouts as layoutsUtils

#############################################################################
# Analysis dashboard layout Management
#############################################################################


def get_layouts():
    layouts_overview = layoutsUtils.get_layouts()
    return layouts_overview, 200


def post_layout(data):
    layoutsUtils.add_layout(data)
    return None, 204


def delete_layout(id):
    layoutsUtils.delete_layout(id)
    return None, 204
