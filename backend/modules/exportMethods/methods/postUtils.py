from backend.modules.exportMethods.exportClass import ExportType, ExportMethod
import requests

#############################################################################
#
# HTTP - Post export method
#
# Send data through a post request to a server
#
#############################################################################


class PostExportType(ExportType):
    def __init__(self):
        super().__init__()

        self.name = "post"
        self.parameters_definition = ["url"]

        self.export_method_class = PostExportMethod


class PostExportMethod(ExportMethod):
    up = False

    def __init__(self, name, parameters):
        super().__init__(PostExportType(), name, parameters)

        # Expected parameters: [url]
        # Check parameters
        if len(parameters) != 1:
            raise Exception("Post export type requires 1 parameter : the url")

        self.url = parameters[0]

        # Check url
        if not self.url.startswith("http://") and not self.url.startswith("https://"):
            raise Exception(
                "Url '" + self.url + "' must start with http:// or https://"
            )

        self.up = True

    def export(self, data):
        print("Post export method: Sending data to '" + self.url + "'")

        if not self.up:
            raise Exception("Can't send data to '" + self.url + "'")

        try:
            # Send data
            r = requests.post(self.url, json=data)
            r.raise_for_status()
            print("Post export method : Data sent")
        except Exception as e:
            print("Post export method : Error sending post request", e)
            raise Exception(
                "Post export method : Error sending post request on url" + str(e)
            )
