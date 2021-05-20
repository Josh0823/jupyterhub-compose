import json
from tornado import escape, web
from jupyterhub.services.auth import HubAuthenticated

# TODO
# stat conda env to ensure environment is legit
# Add validation to POST request
class APIUserSelectionHandler(HubAuthenticated, web.RequestHandler):    
    def initialize(self):
        self.storage = self.settings['storage']
        self.service_prefix = self.settings['service_prefix']

    @web.authenticated
    async def get(self, user):
        info = await self.storage.read(user)
        print(f'Info fetched for {user}: {info}')

        if info:
            self.write(info)
    
    @web.authenticated
    async def delete(self, user):
        await self.storage.delete(user)
        print(f'Info deleted for {user}')
        
    # add stat check to confirm path is good
    @web.authenticated
    async def post(self, user):
        doc = escape.json_decode(self.request.body)
        
        await self.storage.create(user, doc)
        print(f'Info set for {user}: {doc}')
        
    def write_to_json(self, doc):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(escape.utf8(json.dumps(doc)))