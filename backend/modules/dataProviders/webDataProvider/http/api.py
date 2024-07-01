import requests
import json
from backend.modules.dataProviders.DataProviderException import DataProviderException


# Todo : change info if in not alive anymore
def get_status(url):
    try:
        r = requests.get(url + "/info")

        if r.status_code != 200:
            return False

        # Check content type
        content = get_http_response(r)

        if content is None:
            return False  # we are expecting a dict

        return True

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
    except requests.exceptions.InvalidURL:
        raise DataProviderException("Invalid URL", 400)


def get_info(url):
    try:
        r = requests.get(url + "/info")
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


# ==== Projects ====
def get_projects(url):
    try:
        r = requests.get(url + "/projects")
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def get_project(url, id_project):
    try:
        r = requests.get(url + "/projects/" + id_project)
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def get_id_list(url, id_project, analysis, _from=None, _to=None):
    try:
        if _from is not None and _to is not None:
            url = (
                url
                + "/projects/"
                + id_project
                + "/data-id-list?from={}&to={}&analysisId={}".format(
                    _from, _to, analysis["id"]
                )
            )
        else:
            url = (
                url
                + "/projects/"
                + id_project
                + "/data-id-list?analysisId={}".format(analysis["id"])
            )

        if analysis["start"]:
            url += "&analysisStart={}".format(str(analysis["start"]).lower())
        if analysis["end"]:
            url += "&analysisEnd={}".format(str(analysis["end"]).lower())

        r = requests.get(url)

        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print(
            "Error getting data id list from {} on project {}".format(url, id_project)
        )
        return []


def get_samples(url, id_project, analysis, id_list):
    try:
        rurl = (
            url
            + "/projects/{}/data?analysisId={}&analysisStart={}&analysisEnd={}".format(
                id_project,
                analysis["id"],
                str(analysis["start"]).lower(),
                str(analysis["end"]).lower(),
            )
        )

        r = requests.post(rurl, json=id_list)
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise Exception(
            "Could not get the data provider {} data for project {}".format(
                url, id_project
            )
        )


def delete_project(url, id_project):
    try:
        r = requests.delete(url + "/projects/" + id_project)
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


# ==== Selections ====
def get_selections(url, id_project):
    try:
        r = requests.get(url + "/projects/{}/selections".format(id_project))
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def post_selection(url, id_project, data):
    try:
        r = requests.post(url + "/projects/{}/selections".format(id_project), json=data)
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def get_selection_id(url, id_project, id_selection):
    try:
        r = requests.get(
            url
            + "/projects/{}/selections/{}/selected-data-id-list".format(
                id_project, id_selection
            )
        )

        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def delete_selection(url, id_project, id_selection):
    try:
        r = requests.delete(
            url + "/projects/{}/selections/{}".format(id_project, id_selection)
        )

        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


# ==== Models ====
def get_models(url, id_project):
    try:
        r = requests.get(url + "/projects/{}/models".format(id_project))
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def get_model_result_id_list(url, project_id, model_id):
    try:
        r = requests.get(
            url
            + "/projects/{}/models/{}/evaluated-data-id-list".format(
                project_id, model_id
            )
        )
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def get_model_result(url, id_project, id_model, id_sample_list):
    try:
        r = requests.post(
            url + "/projects/{}/models/{}/results".format(id_project, id_model),
            json=id_sample_list,
        )
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


def delete_model(url, id_project, id_model):
    try:
        r = requests.delete(url + "/projects/{}/models/{}".format(id_project, id_model))
        return get_http_response(r)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None


# ==== Utils ====
def get_http_response(response):
    try:
        if response.raise_for_status() is None:
            return get_valid_response(response)
    except requests.exceptions.HTTPError:
        return get_error_response(response)


def get_valid_response(response):
    if response.status_code == 204:
        return True
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        return


def get_error_response(response):
    if response.status_code == 500:
        raise DataProviderException("Data Provider unexpected Error", 500)

    raise DataProviderException(response.text, response.status_code)
