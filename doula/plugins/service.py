from .interfaces import IPullActions
from .interfaces import IPuller
from .interfaces import ISiteContainer
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from zig.dispatch import ReceptionRegistry
from zig.interfaces import IReceptionRegistry
from zig.dispatch import action as base_action
from zig.recv import Receiver
from zope.interface import implementer
import logging
import zig


here = __name__

logger = logging.getLogger(here)


def includeme(config):
    config.include('zig.context')
    puller = Puller.create(config)
    config.registry.registerUtility(puller, IPuller)
    config.scan(here)

class action(base_action):
    iface = IReceptionRegistry

@implementer(IPuller)
class Puller(Receiver):
    handler_iface = IPullActions
    handler_class = ReceptionRegistry

    @classmethod
    def create(cls, config):
        address = config.settings['doula.pull']
        ctx = zig.cfr(config.registry)
        sock = ctx.pull(bind=address)
        handler = cls.handler_class(config.registry)
        config.registry.registerUtility(handler, cls.handler_iface)
        puller = cls(sock.recv_json, handler)
        puller.sock = sock
        puller.address = address
        return puller


@action('doula.register')
def register(payload, registry):
    """
    Register a bambino node with a doula
    """
    address = payload['address']
    sitename = payload['site']
    node = payload['node']
    sc = registry.queryUtility(ISiteContainer)
    site = sc.get(sitename, None)
    if site is None:
        sc.add_site(sitename, ((node, address),))
    else:
        # attempt match before write
        site.add_node((node, address))
    return dict(status='added')


@action('doula.sites')
def sites(payload, registry):
    """
    Return registered sites
    """
    sc = registry.queryUtility(ISiteContainer)
    return dict(status='ok', sites=sc.keys())



@action('default')
def default(payload, registry):
    return dict(status='ok', pong=True)



@subscriber(ApplicationCreated)
def launch_server(event):
    sink = event.app.registry.getUtility(IPuller)
    logger.info("launch pull server: %s\n" %sink.address)
    sink.run()

