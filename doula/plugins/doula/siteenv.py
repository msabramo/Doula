from bambino.resources import BaseResource
from contextlib import contextmanager as cm

def includeme(config):
    pass


def modify_resources(settings, app, name='sites'):
    name = settings.get('doula.plugins.siteenvs', name)
    SiteContainer.add_resource_to_tree(app, name, settings)
    return app

#/sites/nodes/node
#/sites/apps/appenv
#/sites/nodes/node/apps


class FactoryMapResource(BaseResource):

    def member_factory(self, **kw):
        raise NotImplementedError

    def __init__(self, parent=None, name=None, **sitemap):
        with superinit(self, parent, name, **sitemap):
            for key, item in sitemap:
                self.member_factory(self, key, **item)


class Node(BaseResource):
    def __init__(self, parent, name, address, **kw):
        with superinit(name, parent,**kw):
            self.address = self.address


class NodeContainer(FactoryMapResource):
    """
    A box that serves part of a site.

    Usually hidden by a facade
    """
    member_factory = staticmethod(Node.add_resource_to_tree)



class AppContainer(BaseResource):
    """
    An application on a node
    """    

    def __init__(self, parent, name, nodes, **kw):
        with superinit(name, parent, nodes, **kw):
            self.nodes = nodes



class SiteContainer(FactoryMapResource):
    node_container_class = NodeContainer
    appenv_container_class = AppContainer

    def __init__(self, parent=None, name=None, settings=None, **sites):
        self.settings = settings
        with superinit(self, parent, name, **sites):
            self.settings=settings
    
    def member_factory(self, **site_data):
        nodes = self.node_container_class.add_resource_to_tree(self, 'nodes', **site_data)
        yield nodes
        yield self.app_container_class.add_resource_to_tree(self, 'apps', nodes)

    populate = member_factory
        







        
@cm
def superinit(obj, *args, **kw):
    try:
        yield
    finally:
        super(obj.__class__, obj).__init__(*args, **kw)
