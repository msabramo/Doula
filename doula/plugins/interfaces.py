from zope.interface import Interface
from zope.interface import Attribute
from zig.interfaces import IReceptionRegistry

class IPuller(Interface):
    """
    Our server for talking to bambinos
    """

class IPullActions(IReceptionRegistry):
    """
    A registry for dispatching on received pulls
    """

class ISiteContainer(Interface):
    """
    A mapping container that hold references to registered sites
    """

    def add_site(name, nodes=None):
        """
        :name:  unique key
        :nodes: site nodes 
        """


class ISite(Interface):
    """
    A context object representing a site
    """
    nodes = Attribute("all node that compose a site")
    appenvs = Attribute("all apps that compose a site")
