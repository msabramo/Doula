from contextlib import contextmanager as cm
from prism.resource import BaseResource


def includeme(config):
    pass


def modify_resource_tree(config, app_root, name='sites'):
    name = config.settings.get('doula.sites', name)
    SiteContainer.add_resource_to_tree(app_root, name, **config.settings)
    return app_root


#/sites/nodes/node
#/sites/apps/appenv
#/sites/nodes/node/apps


class FactoryMapResource(BaseResource):
    """
    A base class for easily populating a traversal tree
    """
    def member_factory(self, **kw):
        raise NotImplementedError

    def __init__(self, parent=None, name=None, **sitemap):
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

    def __init__(self, parent=None, name=None, **settings):
        with superinit(self, parent, name):
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
