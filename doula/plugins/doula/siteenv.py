from bambino.resources import BaseResource
from contextlib import contextmanager as cm


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

@cm
def superinit(obj, *args, **kw):
    try:
        yield
    finally:
        super(obj.__class__, obj).__init__(*args, **kw)


class SiteContainer(FactoryMapResource):
    node_container_class = NodeContainer
    appenv_container_class = AppContainer
    
    def member_factory(self, **site_data):
        nodes = self.node_container_class.add_resource_to_tree(self, 'nodes', **site_data)
        yield nodes
        yield self.app_container_class.add_resource_to_tree(self, 'apps', nodes)


