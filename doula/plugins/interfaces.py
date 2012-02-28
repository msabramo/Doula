from zope.interface import Interface
from zope.interface import Attribute

class IDoulaZMQServer(Interface):
    """
    Our server for talking to bambinos
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
