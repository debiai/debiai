from configparser import ConfigParser
from termcolor import colored

import os

config_path = "backend/config/config.ini"
config_parser = ConfigParser()

DEBUG_COLOR = "light_blue"
DEBUG_SECONDARY_COLOR = "blue"
ERROR_COLOR = "light_red"
SUCCESS_COLOR = "green"

# Default config
config = {
    "DATA_PROVIDERS_CONFIG": {
        "creation": True,
        "deletion": True,
    },
    "INTEGRATED_DATA_PROVIDER": {
        "enabled": True,
        "allow_create_projects": True,
        "allow_delete_projects": True,
        "allow_insert_data": True,
        "allow_create_selections": True,
        "allow_delete_selections": True,
        "allow_create_models": True,
        "allow_delete_models": True,
        "allow_insert_results": True,
    },
    "WEB_DATA_PROVIDERS_CONFIG": {
        "cache": True,
        "cache_duration": 120,
    },
    "WEB_DATA_PROVIDERS": {
        # "name": "url"
    },
    "ALGO_PROVIDERS_CONFIG": {
        "enable_integrated": True,
        "creation": True,
        "deletion": True,
    },
    "ALGO_PROVIDERS": {
        # "name": "url"
    },
    "EXPORT_METHODS_CONFIG": {
        "creation": True,
        "deletion": True,
    },
    "EXPORT_METHODS": {
        # "name": "type, param1, param2, ..."
    },
}

# Env vars mapping
ENV_VAR_MAPPING = {
    "DATA_PROVIDERS_CONFIG": {
        "creation": "DEBIAI_DATA_PROVIDERS_ALLOW_CREATION",
        "deletion": "DEBIAI_DATA_PROVIDERS_ALLOW_DELETION",
    },
    "INTEGRATED_DATA_PROVIDER": {
        "enabled": "DEBIAI_INTEGRATED_DATA_PROVIDER_ENABLED",
        "allow_create_projects": "DEBIAI_INTEGRATED_DP_ALLOW_CREATE_PROJECTS",
        "allow_delete_projects": "DEBIAI_INTEGRATED_DP_ALLOW_DELETE_PROJECTS",
        "allow_insert_data": "DEBIAI_INTEGRATED_DP_ALLOW_INSERT_DATA",
        "allow_create_selections": "DEBIAI_INTEGRATED_DP_ALLOW_CREATE_SELECTIONS",
        "allow_delete_selections": "DEBIAI_INTEGRATED_DP_ALLOW_DELETE_SELECTIONS",
        "allow_create_models": "DEBIAI_INTEGRATED_DP_ALLOW_CREATE_MODELS",
        "allow_delete_models": "DEBIAI_INTEGRATED_DP_ALLOW_DELETE_MODELS",
        "allow_insert_results": "DEBIAI_INTEGRATED_DP_ALLOW_INSERT_RESULTS",
    },
    "WEB_DATA_PROVIDERS_CONFIG": {
        "cache": "DEBIAI_WEB_DATA_PROVIDERS_CACHE_ENABLED",
        "cache_duration": "DEBIAI_WEB_DATA_PROVIDERS_CACHE_DURATION",
    },
    "ALGO_PROVIDERS_CONFIG": {
        "enable_integrated": "DEBIAI_ALGO_PROVIDERS_ENABLE_INTEGRATED",
        "creation": "DEBIAI_ALGO_PROVIDERS_ALLOW_CREATION",
        "deletion": "DEBIAI_ALGO_PROVIDERS_ALLOW_DELETION",
    },
    "EXPORT_METHODS_CONFIG": {
        "creation": "DEBIAI_EXPORT_METHODS_ALLOW_CREATION",
        "deletion": "DEBIAI_EXPORT_METHODS_ALLOW_DELETION",
    },
}

# List of list based config sections + their env var mapping
LIST_CONFIG_SECTIONS = {
    "WEB_DATA_PROVIDERS": "DEBIAI_WEB_DATA_PROVIDER_",
    "ALGO_PROVIDERS": "DEBIAI_ALGO_PROVIDER_",
    "EXPORT_METHODS": "DEBIAI_EXPORT_METHOD_",
}

changes_made = False


def get_config_value(section, key, config_parser):
    # Return the value of the key in the section of the config_parser
    # Or return the ENV_VAR if it exists

    value = None
    ENV_VAR = ENV_VAR_MAPPING[section][key]

    # Get the value from the config file
    if section in config_parser and key in config_parser[section]:
        value = str.lower(config_parser[section][key])

    # Get the value from the environment variables
    if ENV_VAR in os.environ:
        value = str.lower(os.environ[ENV_VAR])

    if value is None:
        print(
            " - Missing "
            + colored(section, DEBUG_SECONDARY_COLOR)
            + " / "
            + colored(key, DEBUG_SECONDARY_COLOR)
            + " in config or in "
            + colored(ENV_VAR, DEBUG_SECONDARY_COLOR)
            + " env var, using default"
        )
        return None

    return value


def get_config_values(section, config_parser):
    # Return a dict of the values of the section of the config_parser
    # Or return the ENV_VAR if it exists

    values = {}
    ENV_VAR = LIST_CONFIG_SECTIONS[section]

    # Get the value from the config file
    if section in config_parser:
        for key in config_parser[section]:
            values[key] = str.lower(config_parser[section][key])

    # Get the value from the environment variables
    # iterate over the keys of the env var
    for key in os.environ.keys():
        if key.startswith(ENV_VAR):
            # Get the key name without the env var prefix
            key_name = key[len(ENV_VAR) :]  # noqa
            values[key_name] = str.lower(os.environ[key])

    return values


def set_config_value(section, key, value):
    global config, changes_made

    if section in config and key in config[section]:
        if config[section][key] != value:
            # The default value is different from the one in the config file
            config[section][key] = value
            changes_made = True

            print(
                " - Overriding "
                + colored(section, DEBUG_COLOR)
                + " / "
                + colored(key, DEBUG_COLOR)
                + " with value "
                + colored(str(value), DEBUG_COLOR)
            )


def init_config():
    global config

    print("===================== CONFIG =======================")

    # Read the config file
    config_parser.read(config_path)

    for section in config.keys():
        # Deal with boolean, integer and string values
        for key in config[section].keys():
            # Get the value from the config file or the environment variables
            value = get_config_value(section, key, config_parser)

            if value is None:
                continue

            # Deal with booleans
            if type(config[section][key]) is bool:
                if value == "false":
                    set_config_value(section, key, False)
                elif value == "true":
                    set_config_value(section, key, True)
                else:
                    print(
                        colored("   [ERROR]", ERROR_COLOR)
                        + " Invalid boolean value for "
                        + colored(key, DEBUG_COLOR)
                        + ", using default value"
                    )
                    continue

            # Deal with integers
            elif type(config[section][key]) is int:
                try:
                    set_config_value(section, key, int(value))
                except ValueError:
                    print(
                        colored("   [ERROR]", ERROR_COLOR)
                        + " Invalid integer value for "
                        + colored(key, DEBUG_COLOR)
                        + ", using default value"
                    )
                    continue

            # Deal with strings
            elif type(config[section][key]) is str:
                set_config_value(section, key, str(value))

        # Deal with list based config elements
        if section in LIST_CONFIG_SECTIONS:
            elements = get_config_values(section, config_parser)

            for element_name in elements:
                print(
                    " - Adding "
                    + section.lower().replace("_", "-")[0:-1]
                    + " "
                    + colored(element_name, DEBUG_COLOR)
                    + " ("
                    + colored(elements[element_name], DEBUG_COLOR)
                    + ")"
                )

                config[section][element_name] = elements[element_name]

    if not changes_made:
        print("   Default config used")


def get_config():
    return config
