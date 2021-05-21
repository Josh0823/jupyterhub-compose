import json
from pathlib import Path


class Storage:

    async def create(self, user, incoming):
        raise NotImplementedError

    async def read(self, user):
        raise NotImplementedError

    async def update(self, user, incoming):
        raise NotImplementedError

    async def delete(self, user):
        raise NotImplementedError


class FileStorage(Storage):

    def __init__(self, template="/data/{user[0]}/{user}.{type}.json"):
        self.template = template

    def doc_path(self, user, type):
        return Path(self.template.format(user=user, type=type))

    def create(self, user, incoming, ty):
        # add path to {user}.{type}.json file if its not there
        doc_path = self.doc_path(user, ty)
        print(doc_path)
        exists = doc_path.is_file()
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            infile = open(doc_path, 'r')
            data = json.loads(infile.read())
            infile.close
            with open(doc_path, "w") as stream:
                new_data = list(data[f'{user}'])
                new_data.append(incoming)

                new_data = list(
                    {e['entrypoint']: e for e in new_data}.values())
                json.dump({user: new_data}, stream)
        except:
            with open(doc_path, 'w') as stream:
                json.dump({user: [incoming]}, stream)

        # update current selected entrypoint
        doc_path = self.doc_path(user, 'current')
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(doc_path, 'w') as stream:
            json.dump({user: incoming}, stream)
        return dict(updated=1) if exists else dict(created=1)

    def read(self, user, type):
        doc_path = self.doc_path(user, type)
        try:
            infile = open(doc_path, 'r').read()
            return json.loads(infile)
        except:
            return None

    def update(self, user, incoming):
        return self.create(user, incoming)

    def delete(self, user, type):
        doc_path = self.doc_path(user, type)
        try:
            doc_path.unlink()
            return dict(deleted=1)
        except:
            return None
