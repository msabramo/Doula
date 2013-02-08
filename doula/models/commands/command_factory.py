from doula.models.commands import *

class CommandFactory(object):
    """
    This is the meat-and-taters of the rule world.
    """
    def __init__(self, 
            service_name,
            node_ip,
            web_app_dir="/opt/webapp",
            keyfile="~/.ssh/id_rsa_doula"):

        self.service_name = service_name
        self.node_ip = node_ip
        self.web_app_dir = web_app_dir
        self.keyfile = keyfile

    def get_one(self, the_type):
        command = the_type(self.service_name,
                self.node_ip,
                self.web_app_dir,
                self.keyfile)
        return command

