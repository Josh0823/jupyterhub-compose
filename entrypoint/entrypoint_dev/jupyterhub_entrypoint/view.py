from tornado import web
from jinja2 import Environment
from jupyterhub.utils import url_path_join
from jupyterhub.services.auth import HubAuthenticated

# TODO Move call for envs/images/scripts to index.html

class ViewHandler(HubAuthenticated, web.RequestHandler):
    def initialize(self, loader):
        super().initialize()
        
        self.loader = loader
        self.env = Environment(loader = self.loader)
        self.template = self.env.get_template('index.html')

    # eventually transition to read from datastore/file
    @web.authenticated
    async def get(self):
        prefix = self.hub_auth.hub_prefix
        logout_url = url_path_join(prefix, 'logout')

        envs = ["myenv", "test-env"]
        scripts = ["myscript", "test-script"]


        self.write(self.template.render(user=self.get_current_user(),
            login_url = self.hub_auth.login_url,
            logout_url = logout_url,
            base_url = prefix,
            no_spawner_check = True,
            static_url=self.static_url,
            envs = envs,
            scripts = scripts))
