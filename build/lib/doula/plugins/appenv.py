from doula.resources import BaseResource
from path import path


class VenvContainer(BaseResource):
    __name__ = 'appenvs'

    @staticmethod
    def venv_check(vpath):
        """
        is it a appenv
        """
        return (vpath / '.git').exists() or (vpath / 'bin/activate').exists()
    
    def __init__(self, name, parent, directory, ignored=None, venv_check=None):
        self.__name__ = name
        self.__parent__ = parent
        self.directory = path(directory)
        self.ignored = ignored and set(ignored) or set()

    def __getitem__(self, key):
        try:
            return super(VenvContainer, self).__getitem__(key)
        except KeyError:
            self.load()
            return super(VenvContainer, self).__getitem__(key)

    def load(self):
        self.clear()
        self.update((x.name, self.venv_factory(self, x)) \
                    for x in self.directory.dirs() \
                    if not x.name in self \
                    or not x.name in self.ignored)

        
class ApplicationEnvironment(BaseResource):
    """
    A virtualenv dedicated to running a service 
    """
    def __init__(self, parent, path):
        self.__name__ = path.name
        self.__parent__ = parent
        self.path = path


# eventually make this a scan
def modify_resourcetree(resource_tree, settings):
    name = settings['doula.plugins.appenv.name']
    directory = settings['doula.plugins.appenv.workonhome']
    resource_tree[name] = VenvContainer(name, resource_tree, directory)
    


def includeme(config):
    config.scan(__name__)
