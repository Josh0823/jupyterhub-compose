import os

from jinja2 import ChoiceLoader, FileSystemLoader, PrefixLoader

from tornado import web
from tornado import ioloop

from traitlets.config import Application, Configurable
from traitlets import List, Unicode, Integer, default

from jupyterhub.utils import url_path_join

from jupyterhub._data import DATA_FILES_PATH
from jupyterhub.handlers.static import LogoHandler

from .api import APIUserSelectionHandler, APICondaHandler, APIScriptHandler
from .ssl import SSLContext
from .view import ViewHandler
from .storage import FileStorage
from .images import APIShifterImageHandler


class EntrypointService(Application, Configurable):
    data_files_path = Unicode(
        DATA_FILES_PATH,
        help="Location of JupyterHub data files"
    )

    service_prefix = Unicode(
        os.environ.get("JUPYTERHUB_SERVICE_PREFIX",
                       '/services/entrypoint/'),
        help="Entrypoint service prefix"
    ).tag(config=True)

    service_url = Unicode(
        os.environ.get('JUPYTERHUB_SERVICE_URL',
                       '/services/entrypoint/'),
        help="Entrypoint service url"
    )

    template_paths = List(
        help="Search paths for jinja templates, coming before default ones"
    ).tag(config=True)

    port = Integer(
        8888,
        help="Port this service will listen on"
    ).tag(config=True)

    logo_file = Unicode(
        "",
        help="Logo path, can be used to override JupyterHub one",
    ).tag(config=True)

    storage_path = Unicode(
        os.environ.get("STORAGE_PATH", "/data"),
        help="Location for file storage"
    )

    shifter_api_token = Unicode(
        os.environ.get("SHIFTER_API_TOKEN"),
        help="Secret token to access shifter api"
    )

    shifter_api_host = Unicode(
        os.environ.get("SHIFTER_API_HOST"),
        help="Hostname of the shifter api"
    )

    @default('logo_file')
    def _logo_file_default(self):
        return os.path.join(
            self.data_files_path, 'static', 'images', 'jupyterhub-80.png'
        )

    @default('template_paths')
    def _template_paths_default(self):
        return ['templates',
                os.path.join(self.data_files_path, 'templates')]

    def initialize(self, argv=None):
        super().initialize(argv)

        self.init_ssl_context()

        base_path = self._template_paths_default()[0]
        if base_path not in self.template_paths:
            self.template_paths.append(base_path)
        print("Base Path " + base_path)
        print('Data Path ' + DATA_FILES_PATH)
        loader = ChoiceLoader(
            [
                PrefixLoader(
                    {'templates': FileSystemLoader([base_path])}, '/'),
                FileSystemLoader(self.template_paths),
            ]
        )

        self.settings = {
            "service_prefix": self.service_prefix,
            "static_path": os.path.join(self.data_files_path, "static"),
            "static_url_prefix": url_path_join(self.service_prefix, "static/"),
            "storage": FileStorage(os.path.join(self.storage_path, "{user[0]}/{user}.{type}.json"))
        }

        self.app = web.Application([
            # (self.service_prefix, ViewHandler, dict(loader=loader), "view")
            (self.service_prefix, ViewHandler, dict(loader=loader)),
            (self.service_prefix + r"update", APIUserSelectionHandler),
            (self.service_prefix + r"user/(.+)/(.+)", APIUserSelectionHandler),
            (self.service_prefix + r"envs/user/(.+)", APICondaHandler),
            (self.service_prefix + r"scripts/user/(.+)", APIScriptHandler),
            (self.service_prefix + r"static/(.*)", web.StaticFileHandler,
             dict(path=self.settings["static_path"])),
            (self.service_prefix + r"logo",
             LogoHandler, {"path": self.logo_file}),
            (self.service_prefix + r"images/user/(.+)", APIShifterImageHandler,
             dict(shifter_api_token=self.shifter_api_token, shifter_api_host=self.shifter_api_host))
        ], **self.settings)

    def init_ssl_context(self):
        self.ssl_content = SSLContext().ssl_context()

    def start(self):
        self.app.listen(self.port)

        ioloop.IOLoop.current().start()


def main():
    app = EntrypointService()
    app.initialize()
    app.start()


if __name__ == '__main__':
    main()
