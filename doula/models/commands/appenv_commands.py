from doula.models.fabric_base import FabricBase
from doula.github import build_url_to_api, post_url, delete_url
from doula.util import pull_json_obj
from requests import HTTPError
import requests
from doula.util_fabric import *
import re
import json

class CreateAppenvRepo(FabricBase):

    def description(self):
        return "Creating the appenv repo"

    def run(self, org):
        """
        Public: Calls git and creates the repo

        org - the organization
        repo - the repo to create
        """
        self.is_valid = True
        self.org = org
        try:
            url = build_url_to_api(
                "%(domain)s/orgs/%(org)s/repos?access_token=%(token)s",
                {'org':self.org})
            self.result = post_url(url, json.dumps({'name':self.service_name}))
        except HTTPError as e:
            if re.match('422 Client', str(e)):
                self.error_string = " It already exists."
            else:
                self.error_string = str(e)
            self.is_valid = False

        return self.is_valid

    def error_text(self):
        return "The repo '%s/%s' cannot be created. %s" % (
                self.org, self.service_name, self.error_string)


class DeleteAppenvRepo(FabricBase):

    def description(self):
        return "Creating the appenv repo"

    def run(self, org):
        """
        Public: Calls git and creates the repo

        org - the organization
        repo - the repo to create
        """
        self.is_valid = True
        self.org = org
        try:
            url = build_url_to_api(
                "%(domain)s/repos/%(org)s/%(repo)s?access_token=%(token)s",
                {'org':self.org, 'repo':self.service_name})
            self.result = delete_url(url)
        except HTTPError as e:
            if re.match('422 Client', str(e)):
                self.error_string = " It already exists."
            else:
                self.error_string = str(e)
            self.is_valid = False

        return self.is_valid

    def error_text(self):
        return "The repo '%s/%s' cannot be deleted. %s" % (
                self.org, self.service_name, self.error_string)

class CreateServiceFolder(FabricBase):

    def description(self):
        return "Creating the root directory for the app in /opt/webapp"

    def run(self, **args):
        """
        Public: Checks that the root directory, i.e.: /opt/webapp/{{service}} is absent

        service_name - the service we're testing for
        """
        self.args = args
        with warn_only('/tmp'):
            command = "if ! [ -d %(dir)s ] ;\
                    then mkdir -p %(dir)s; fi; \
                    echo 'yep'" % {'dir':self._service_path()}

            self.result = run(command)
        return self.validate_logic(self.result == 'yep')

    def error_text(self):
        output = "Could not create the directory for service '%s'" % self.service_name
        return self.error_logic(output)

class InitGitRepo(FabricBase):

    def description(self):
        return "Creating the root directory for the app in /opt/webapp"

    def run(self, **args):
        """
        Public: Checks that the root directory, i.e.: /opt/webapp/{{service}} is absent

        service_name - the service we're testing for
        """
        self.args = args
        with warn_only(self._service_path()):
            command = "git init; echo 'yep'"
            self.result = run(command)
        import ipdb; ipdb.set_trace()
        return self.validate_logic(self.result == 'yep' or re.match("Reinitialized", self.result))

    def error_text(self):
        output = "Could not init the git repo '%s'" % self.service_name
        return self.error_logic(output)
