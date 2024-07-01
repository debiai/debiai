from backend.config.init_config import get_config
from backend.modules.dataProviders.DataProvider import DataProvider
from backend.modules.dataProviders.DataProviderException import DataProviderException
from backend.modules.dataProviders.pythonDataProvider.dataUtils import (
    pythonModuleUtils,
    projects,
    samples,
    selections,
    models,
    tree,
)

from backend.utils.utils import get_app_version

PYTHON_DATA_PROVIDER_ID = "Python module Data Provider"


# Wrappers
def project_must_exist(func):
    def wrapper(*args, **kwargs):
        if len(args) < 2:
            raise Exception("Project id must be provided as first argument")

        project_id = args[1]

        if not projects.project_exist(project_id):
            raise DataProviderException("Project " + project_id + " not found", 404)

        return func(*args, **kwargs)

    return wrapper


class PythonDataProvider(DataProvider):
    # Generic functions
    def __init__(self):
        pythonModuleUtils.init()
        nb_projects = len(projects.get_projects())
        print(
            "   Python module Data Provider initialized with "
            + str(nb_projects)
            + " projects"
        )

    @property
    def name(self):
        return PYTHON_DATA_PROVIDER_ID

    @property
    def type(self):
        return PYTHON_DATA_PROVIDER_ID

    def is_alive(self):
        return True

    def get_info(self):
        # Request method to get info on data Provider
        # return Object { version, dp_name, nb_Sample_max(to load)}
        return {
            "version": get_app_version(),
            "maxSampleIdByRequest": 10000,
            "maxSampleDataByRequest": 2000,
            "maxResultByRequest": 5000,
            "canDelete": {
                "projects": True,
                "selections": True,
                "models": True,
            },
        }

    # Projects
    def get_projects(self):
        # Request method to get projects overview
        # Return Arr[object{ id, name, nb_samples, nb_models, nb_selections,
        # update_time, creation_time}]
        return projects.get_projects()

    def create_project(self, name):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_create_projects"]
        if not creation_allowed:
            raise DataProviderException("Project creation is not allowed", 403)

        # Project must not already exist
        if projects.project_exist(name):
            raise DataProviderException("Project already exists", 400)

        return projects.create_project(name, name)

    @project_must_exist
    def get_project(self, project_id):
        # Request method to get projects overview
        # Return object{ id, name, nb_samples, nb_models, nb_selections,
        # update_time, creation_time}

        project_base_info = projects.get_project(project_id)
        project_base_info["selections"] = selections.get_selections(project_id)
        project_base_info["resultStructure"] = projects.get_result_structure(project_id)
        project_base_info["models"] = models.get_models(project_id)
        return project_base_info

    @project_must_exist
    def delete_project(self, project_id):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_delete_projects"]
        if not creation_allowed:
            raise DataProviderException("Project deletion is not allowed", 403)

        # Request method to delete project
        projects.delete_project(project_id)

    # Id list
    @project_must_exist
    def get_id_list(self, project_id, analysis, _from=None, _to=None):
        # Get id list
        # Return Arr[id]
        return samples.get_all_samples_id_list(project_id, _from, _to)

    @project_must_exist
    def get_samples(self, project_id, analysis, id_list):
        # Get full data from id list
        # Return object { id: [data]}
        return samples.get_data_from_sample_id_list(project_id, id_list)

    # Selections
    @project_must_exist
    def get_selections(self, project_id):
        # Get selections on project
        # Return arr[object{ id, name, creation_time, nb_samples}]
        return selections.get_selections(project_id)

    @project_must_exist
    def get_selection_id_list(self, project_id, selection_id):
        # Get selections id for a project
        # Return selection ID list
        return selections.get_selection_id_list(project_id, selection_id)

    @project_must_exist
    def create_selection(self, project_id, name, id_list, request_id=None):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_create_selections"]
        if not creation_allowed:
            raise DataProviderException("Selection creation is not allowed", 403)

        # Selection creation
        return selections.create_selection(project_id, name, id_list, request_id)

    @project_must_exist
    def delete_selection(self, project_id, selection_id):
        # Check config
        config = get_config()
        deletion_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_delete_selections"]
        if not deletion_allowed:
            raise DataProviderException("Selection deletion is not allowed", 403)

        # Selection deletion
        return selections.delete_selection(project_id, selection_id)

    # Models
    @project_must_exist
    def get_models(self, project_id):
        return models.get_models(project_id)

    @project_must_exist
    def get_model_results_id_list(self, project_id, model_id):
        return models.get_model_id_list(project_id, model_id)

    @project_must_exist
    def get_model_results(self, project_id, model_id, id_list):
        return models.get_model_results(project_id, model_id, id_list)

    # Python module specific functions

    @project_must_exist
    def update_block_structure(self, project_id, blockStructure):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_create_projects"]
        if not creation_allowed:
            raise DataProviderException("Project creation is not allowed", 403)

        # Update block structure
        projects.update_block_structure(project_id, blockStructure)

    @project_must_exist
    def add_block_tree(self, project_id, data):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_insert_data"]
        if not creation_allowed:
            raise DataProviderException("Data insertion is not allowed", 403)

        # Insert data
        return tree.add_block_tree(project_id, data)

    @project_must_exist
    def update_results_structure(self, project_id, resultsStructure):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_insert_results"]
        if not creation_allowed:
            raise DataProviderException("Results insertion is not allowed", 403)

        # TODO : check resultStructure (type and default type ==)
        existing_result_structure = projects.get_result_structure(project_id)
        if existing_result_structure is not None:
            raise DataProviderException(
                "project " + project_id + " already have a results structure", 403
            )

        projects.update_results_structure(project_id, resultsStructure)

    @project_must_exist
    def create_model(self, project_id, data):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_create_models"]
        if not creation_allowed:
            raise DataProviderException("Model creation is not allowed", 403)

        models.create_model(
            project_id, data["name"], data["metadata"] if "metadata" in data else None
        )

    @project_must_exist
    def delete_model(self, project_id, model_id):
        # Check config
        config = get_config()
        deletion_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_delete_models"]
        if not deletion_allowed:
            raise DataProviderException("Model deletion is not allowed", 403)

        # Check if model exist
        if not models.model_exist(project_id, model_id):
            raise DataProviderException("Model does not exist", 404)

        models.delete_model(project_id, model_id)

    @project_must_exist
    def add_results_dict(self, project_id, model_id, data):
        # Check config
        config = get_config()
        creation_allowed = config["INTEGRATED_DATA_PROVIDER"]["allow_insert_results"]
        if not creation_allowed:
            raise DataProviderException("Results insertion is not allowed", 403)

        models.add_results_dict(project_id, model_id, data)
