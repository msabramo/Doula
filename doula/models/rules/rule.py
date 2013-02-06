from doula.util_fabric import *
import os

class Rule(object):

    def __init__(self,
            service_name,
            node_ip,
            web_app_dir,
            keyfile,
            debug=False):

        self.service_name = service_name
        self.web_app_dir = web_app_dir

        env.host_string = node_ip
        env.key_filename = keyfile

    def validate_logic(self, test):
        if self.result.succeeded == True and test:
            self.is_valid = True
        else:
            self.is_valid = False
        return self.is_valid


    def error_logic(self, output):
        if not self.result.succeeded:
            output = self.result
        return output

    def _service_path(self):
            return os.path.join(self.web_app_dir, self.service_name)


    #override for testing
    def fabric_user(self):
        return 'doula'

    def _etc_path(self):
        return os.path.join(self.web_app_dir, self.service_name, 'etc')


