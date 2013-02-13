from doula.models.fabric_base import FabricBase
from doula.github import build_url_to_api, post_url, delete_url
from doula.util import pull_json_obj
from requests import HTTPError
import requests
from doula.util_fabric import *
import re
import json

class InstallPackage(FabricBase):

    def description(self):
        return "Installing the package."

    def run(self, package_url):
        """
        Public: installs the package from pip

        package_url - the url on yorick of the package you wish to install
        """
        with workon(self._service_path(), self.debug):
            command = "\
                    pip install %s \
                    " % package_url

            import ipdb; ipdb.set_trace()
            self.result = run(command)

        return self.validate_logic(self.result.succeeded)

    def error_text(self):
        output = "Could not install package."
        return self.error_logic(output)

class CommitAppEnvRepo(FabricBase):

    def description(self):
        return "Committing the appenv repo"

    def run(self, branch):
        """
        Public: commits files to all MTs
        args['branch'] = the branch

        """
        with warn_only(self._service_path()):
            results = []
            command = "\
                      git add .; \
                      git commit -am 'first commit for new environment'; \
                      git checkout -b %(branch)s \
                      git push origin %(branch)s;\
                      " % {'branch': branch}

            self.result = run(command)

            return self.validate_logic(self.result.succeeded)

    def error_text(self):
        return "Could not commit the git repo."
        return self.error_logic(output)


