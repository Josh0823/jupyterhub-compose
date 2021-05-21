from tornado import escape, web
from jupyterhub.services.auth import HubAuthenticated


class APIBaseHandler(HubAuthenticated, web.RequestHandler):
    def initialize(self):
        self.storage = self.settings['storage']

    def verify_user(self, user):
        current_user = self.get_current_user()
        if not current_user.get("admin", False) and current_user["name"] != user:
            raise web.HTTPError(403)


# TODO
# stat conda env to ensure environment is legit
class APIUserSelectionHandler(APIBaseHandler):
    def initialize(self):
        self.storage = self.settings['storage']

    @web.authenticated
    async def get(self, user, type):
        self.verify_user(user)
        info = self.storage.read(user, type)
        print(f'Info fetched for {user}: {info}')

        if info:
            self.write(info)

    @web.authenticated
    async def delete(self, user, type):
        self.verify_user(user)
        self.storage.delete(user, type)
        print(f'Info deleted for {user}')

    # add stat check to confirm path is good
    @web.authenticated
    async def post(self, user, type):
        self.verify_user(user)
        doc = escape.json_decode(self.request.body)

        self.storage.create(user, doc, type)
        print(f'Info set for {user}: {doc}')


class APICondaHandler(APIBaseHandler):
    @web.authenticated
    async def get(self, user, type='conda'):
        self.verify_user(user)
        info = self.storage.read(user, type)
        if info:
            self.write(info)


class APIScriptHandler(APIBaseHandler):
    @web.authenticated
    async def get(self, user, type='script'):
        self.verify_user(user)
        info = self.storage.read(user, type)
        if info:
            self.write(info)
