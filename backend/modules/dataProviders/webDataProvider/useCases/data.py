import backend.modules.dataProviders.webDataProvider.http.api as api

#
# UseCase folder role is the middleware between class methods and http requests
# It's used to make all changes in data we took from DP and send it back to
# the class/controller
#


def get_project_id_list(url, cache, id_project, analysis, _from=None, _to=None):
    id_list = cache.get_id_list(id_project, _from, _to)

    if id_list is None:
        id_list = api.get_id_list(url, id_project, analysis, _from, _to)
        cache.set_id_list(id_project, id_list, _from, _to)

    return id_list


def get_project_samples(url, id_project, analysis, id_list):
    data = api.get_samples(url, id_project, analysis, id_list)

    return data
