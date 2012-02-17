from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from pyramid import threadlocal 
from zig.server_client import Client
from zig.server_client import Server
from zope.interface import Interface
from zope.interface import implementer


def includeme(config):
    dzs = DoulaZMQServer.create(config)
    config.registry.registerUtility(dzs, IDoulaZMQServer)


class IDoulaZMQServer(Interface):
    """
    """


@implementer(IDoulaZMQServer)
class DoulaZMQServer(Server):
    handler_factory = BambinoHandler
    @classmethod
    def create(cls, config):
        server_address = config.settings['doula.server_address']
        siteskey = config.settings.get('doula.plugins.siteenvs', 'sites')
        handler = cls.handler_factory(config, config.approot[siteskey])
        return cls(handler, server_address)


def get_dzs():
    reg = threadlocal.get_current_registry()
    return reg.queryUtility(IDoulaZMQServer)


@subscriber(ApplicationCreated)
def launch_server(event):
    dzs = get_dzs()
    dzs.run()
