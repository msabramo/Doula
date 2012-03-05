from doula.plugins.interfaces import ISite
from doula.plugins.interfaces import ISiteContainer
from gevent.pool import Pool
from prism.resource import BaseResource
from prism.resource import superinit
from zig.server_client import json_endpoint
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
    nodes_default_query = dict(action='node_status')
    endpoint = json_endpoint
    timeout = 1*1000
    def __init__(self, parent=None, name=None, nodes=None):
        self.__parent__ = parent
        self.__name__ = name
        self.node_map = {}
        if not nodes is None:
            for node in nodes:
                self.add_node(node)

    def add_node(self, (name, address)):
        node = self.node_map.get(name)
        if node is None or node.address != address:
            self.node_map[name] = self.endpoint(address)
            self.logger.info("%s registered @ %s as part of %s", name, address, self.__name__)
    
    def query_nodes(self, q=None):
        pool = Pool(self.pool_size)
        if q is None:
            q = self.nodes_default_query
        results_g = [(node, pool.spawn(endpoint.request(q, timeout=self.timeout))) \
                     for node, endpoint in self.node_map.items()]
        pool.join()
        return dict((x, y.get()) for x, y in results_g)

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

    def add_site(self, name, nodes):
        self.site_class.add_resource_to_tree(self, name, nodes)





