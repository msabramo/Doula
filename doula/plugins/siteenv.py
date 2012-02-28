from doula.plugins.interfaces import ISite
from doula.plugins.interfaces import ISiteContainer
from gevent.pool import Pool
from prism.resource import BaseResource
from prism.resource import superinit
from zig.server_client import SimpleRRClient
from zope.interface import implementer
import logging

logger = logging.getLogger(__name__)


def includeme(config):
    pass
    

def modify_resource_tree(config, app_root, name='sites'):
    name = config.settings.get('doula.sites', name)
    sc = SiteContainer.add_resource_to_tree(app_root, name, **config.settings)
    config.registry.registerUtility(sc, ISiteContainer)
    return app_root


@implementer(ISite)
class Site(BaseResource):
    logger = logger
    pool_size = 10
    nodeclient_class = SimpleRRClient
    nodes_default_query = dict(action='node_status')

    def __init__(self, parent=None, name=None, address=None):
        self.__parent__ = parent
        self.__name__ = name
        self.node_clients = {}
        if not address is None:
            self.add_node(address)

    def add_node(self, node_address):
        self.node_clients[node_address] = self.nodeclient_class(node_address)
        self.logger.info("%s registered as part of %s", node_address, self.__name__)
    
    def query_nodes(self, q=None):
        pool = Pool(self.pool_size)
        if q is None:
            q = self.nodes_default_query
        results = ((address, pool.spawn(client.send(q)).get()) for address, client in self.node_clients)
        pool.join()
        return dict(results)

    @property
    def nodes(self):
        return self.node_clients.keys()

    @property
    def apps(self):
        q = dict(action='appenv')
        return self.query_nodes(q)


@implementer(ISiteContainer)
class SiteContainer(BaseResource):
    site_class = Site
    def __init__(self, parent=None, name=None, **settings):
        with superinit(self, parent, name):
            self.settings=settings


    def add_site(self, name, address):
        self.site_class.add_resource_to_tree(self, name, address)





