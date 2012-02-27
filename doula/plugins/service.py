from .interfaces import IDoulaZMQServer
from .interfaces import ISiteContainer
from pyramid import threadlocal 
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from zig.dispatch import ActionRegistry
from zig.dispatch import IActionRegistry
from zig.dispatch import action
from zig.server_client import RepServer
from zope.interface import implementer
import logging

here = __name__

logger = logging.getLogger(here)


def includeme(config):
    dzs = DoulaZMQServer.create(config)
    config.registry.registerUtility(dzs, IDoulaZMQServer)
    config.scan(here)


@implementer(IDoulaZMQServer)
class DoulaZMQServer(RepServer):
    handler_iface = IActionRegistry
    handler_class = ActionRegistry

    @classmethod
    def create(cls, config):
        server_address = config.settings['doula.server_address']
        handler = cls.handler_class(config.registry)
        config.registry.registerUtility(handler, cls.handler_iface)
        server = cls(handler, server_address)
        return server


@action('doula.register')
def register(payload, registry):
    """
    Register a bambino node with a doula
    """
    address = payload['address']
    sitename = payload['site']
    sc = registry.queryUtility(ISiteContainer)
    site = sc.get(sitename, None)
    if site is None:
        sc.add_site(sitename, address)
    else:
        site.add_node(address)
    return dict(status='added')


@action('doula.sites')
def sites(payload, registry):
    """
    Register a bambino node with a doula
    """
    sc = registry.queryUtility(ISiteContainer)
    return dict(status='ok', sites=sc.keys())


@action('default')
def default(payload, registry):
    return dict(status='ok', pong=True)


def get_dzs():
    reg = threadlocal.get_current_registry()
    return reg.queryUtility(IDoulaZMQServer)


@subscriber(ApplicationCreated)
def launch_server(event):
    dzs = event.app.registry.getUtility(IDoulaZMQServer)
    logger.info("launch server: %s" %dzs.address)
    dzs.run()

