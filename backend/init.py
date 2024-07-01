# import backend.modules.dataProviders.dataProviderManager as dataProviderManager
# import backend.modules.exportMethods.exportUtils as exportUtils
# import backend.modules.algoProviders.algoProvidersManager as algoProvidersManager
# import backend.utils.widgetConfigurations.widgetConfigurations as widgetConfUtils
# import backend.utils.layouts.layouts as layoutsUtils
# import config.init_config as config

from backend.modules.dataProviders import (
    dataProviderManager,
)
from backend.modules.exportMethods import (
    exportUtils,
)
from backend.modules.algoProviders import (
    algoProvidersManager,
)
from backend.utils.widgetConfigurations import (
    widgetConfigurations as widgetConfUtils,
)
from backend.utils.layouts import (
    layouts as layoutsUtils,
)
from backend.config import (
    init_config as config,
)


def init():
    # Init config file
    config.init_config()

    # Init data providers
    dataProviderManager.setup_data_providers()

    # Init AlgoProviders
    algoProvidersManager.setup_algo_providers()

    # Init export methods
    exportUtils.load_export_methods()

    # Init widget configurations
    widgetConfUtils.setup_widget_configurations()

    # Init layouts
    layoutsUtils.setup_layouts()
