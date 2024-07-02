from modules.dataProviders.DataProvider import DataProvider
from modules.dataProviders.webDataProvider.useCases.data import (
    get_project_id_list,
    get_project_samples,
)
from modules.dataProviders.webDataProvider.useCases.projects import (
    get_all_projects_from_data_provider,
    get_single_project_from_data_provider,
    delete_project,
)
from modules.dataProviders.webDataProvider.useCases.models import (
    get_model_results,
    get_models_info,
    get_model_result_id,
    delete_model,
)
import modules.dataProviders.webDataProvider.useCases.selections as useCaseSelections
from modules.dataProviders.webDataProvider.http.api import get_info, get_status
from modules.dataProviders.webDataProvider.cache.cache import Cache


# WebDataProvider class, allow to get data from a web data-provider
class WebDataProvider(DataProvider):
    def __init__(self, url, name):
        self.url = url.strip()
        self._name = name
        self.alive = None

        # Check if url is valid
        if not self.url:
            raise ValueError("Url is empty")

        # Remove trailing slash
        self.url = self.url.rstrip("/")

        # Remove empty spaces
        self.url = self.url.removesuffix(" ")

        # Remove trailing slash then space
        self.url = self.url.replace("/ ", "")

        # Remove trailing space then slash
        self.url = self.url.replace(" /", "")

        # Remove trailing slash, sharp then slash
        self.url = self.url.rstrip("/#/")

        # Check if the url is in uppercase
        self.url = self.url.lower()

        # Init cache
        self.cache = Cache()

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return "Web"

    # Todo api call Info (new info)
    def is_alive(self):
        self.alive = True if get_status(self.url) is True else False
        return self.alive

    def get_info(self):
        return get_info(self.url)

    # ==== Projects ====
    def get_projects(self):
        # Request method to get projects overview
        # Return Arr[object{ id, name, nb_samples, nb_models, nb_selections,
        # update_time, creation_time}]
        return get_all_projects_from_data_provider(self.url, self.name)

    def get_project(self, id_project):
        # Request method to get projects overview
        # Return object{ id, name, nb_samples, nb_models, nb_selections,
        # update_time, creation_time}
        return get_single_project_from_data_provider(self.url, self.name, id_project)

    def delete_project(self, project_id):
        return delete_project(self.url, project_id)

    def get_id_list(self, project_id, analysis, _from=None, _to=None):
        # http Request on dp to get id list
        # Return Arr[id]
        return get_project_id_list(
            self.url, self.cache, project_id, analysis, _from, _to
        )

    def get_samples(self, project_id, analysis, id_list):
        # http Request get full sample
        # Return object { id: [data]}
        return get_project_samples(self.url, project_id, analysis, id_list)

    # ==== Selections ====
    def get_selections(self, project_id):
        # Get selections on project
        # Return arr[object{ id, name, creation_time, nb_samples}]
        return useCaseSelections.get_project_selections(self.url, project_id)

    def get_selection_id_list(self, project_id, selection_id):
        return useCaseSelections.get_id_list_from_selection(
            self.url, self.cache, project_id, selection_id
        )

    def create_selection(self, project_id, name, id_list, request_id=None):
        return useCaseSelections.create_selection(
            self.url, project_id, name, id_list, request_id
        )

    def delete_selection(self, project_id, selection_id):
        return useCaseSelections.delete_selection(self.url, project_id, selection_id)

    # ==== Models ====
    def get_models(self, project_id):
        return get_models_info(self.url, project_id)

    def get_model_results_id_list(self, project_id, model_id):
        return get_model_result_id(self.url, self.cache, project_id, model_id)

    def get_model_results(self, project_id, model_id, sample_list):
        return get_model_results(self.url, project_id, model_id, sample_list)

    def delete_model(self, project_id, model_id):
        return delete_model(self.url, project_id, model_id)
