# This service is used to cache data from the web data provider
# It's used to avoid multiple requests to the web data provider
# It will mainly save the id list of samples, selections and models results
# The ability to cache and the time to live are configurable in the config file

from backend.config.init_config import get_config
from cacheout import Cache as CacheoutCache


class Cache:
    def __init__(self):
        # Get config
        self.config = get_config()

        self.cache_enabled = self.config["WEB_DATA_PROVIDERS_CONFIG"]["cache"]
        self.cache_ttl = self.config["WEB_DATA_PROVIDERS_CONFIG"]["cache_duration"]

        # Init cache
        self.project_id_list_cache = CacheoutCache(maxsize=256, ttl=self.cache_ttl)
        # <id_project>_<from>_<to>: [...]
        # <id_project>_total: [...]

        self.selection_id_list_cache = CacheoutCache(maxsize=256, ttl=self.cache_ttl)
        # <id_project>_<id_selection>: [...]

        self.model_result_id_list_cache = CacheoutCache(maxsize=256, ttl=self.cache_ttl)
        # <id_project>_<id_model>: [...]

    # Project id list
    def get_key(self, id_project, _from=None, _to=None):
        if _from is None or _to is None:
            return "{}_total".format(id_project)
        else:
            return "{}_{}_{}".format(id_project, _from, _to)

    def get_id_list(self, id_project, _from=None, _to=None):
        if not self.cache_enabled:
            return None

        key = self.get_key(id_project, _from, _to)

        return self.project_id_list_cache.get(key)

    def set_id_list(self, id_project, id_list, _from=None, _to=None):
        if not self.cache_enabled:
            return

        key = self.get_key(id_project, _from, _to)

        self.project_id_list_cache.set(key, id_list)

    # Selection id list
    def get_selection_key(self, id_project, id_selection):
        return "{}_{}".format(id_project, id_selection)

    def get_selection_id_list(self, id_project, id_selection):
        if not self.cache_enabled:
            return None

        key = self.get_selection_key(id_project, id_selection)

        return self.selection_id_list_cache.get(key)

    def set_selection_id_list(self, id_project, id_selection, id_list):
        if not self.cache_enabled:
            return

        key = self.get_selection_key(id_project, id_selection)

        self.selection_id_list_cache.set(key, id_list)

    # Model result id list
    def get_model_result_key(self, id_project, id_model):
        return "{}_{}".format(id_project, id_model)

    def get_model_result_id_list(self, id_project, id_model):
        if not self.cache_enabled:
            return None

        key = self.get_model_result_key(id_project, id_model)

        return self.model_result_id_list_cache.get(key)

    def set_model_result_id_list(self, id_project, id_model, id_list):
        if not self.cache_enabled:
            return

        key = self.get_model_result_key(id_project, id_model)

        self.model_result_id_list_cache.set(key, id_list)
