from doula.models.fabric_base import FabricBase
from doula.github import build_url_to_api
from doula.util import pull_json_obj
from requests import HTTPError
import requests
from doula.util_fabric import *
import re

class ConfigRepoExists(FabricBase):

    def description(self):
        return "Checking if the git config repo exists."

    def run(self, **args):
        """
        Public: Checks that a repo exists.

        org - the organization
        repo - the repo
        """
        self.exists = True
        self.args = args
        try:
            url = build_url_to_api(
                "%(domain)s/repos/%(org)s/%(repo)s?access_token=%(token)s",
                {'org':args['org'], 'repo':args['repo']})
            result = pull_json_obj(url)
        except HTTPError as e:
            self.exists = False
        self.is_valid = self.exists
        return self.exists

    def error_text(self):
        return "The repo '%s/%s' does not exist." % (self.args['org'], self.args['repo'])


class ConfigFilesAbsent(FabricBase):

    def description(self):
        return "Checking that supervisor.conf and nginx.conf are absent."

    def run(self, **args):
        """
        Public: Checks for the absense of supervisor and nginx files in the config repo.

        org - the organization
        repo - the repo
        """
        self.args = args
        self.errors = self.conf_files_absent()
        if len(self.errors) > 0:
            self.is_valid = False
        return self.is_valid

    def conf_files_absent(self):
        errors = []
        for file_name in ['nginx.conf', 'supervisor.conf']:
            for branch in range(5):
                branch_name = 'mt%s' % str(branch)
                if self.is_present(file_name, branch_name):
                    errors.append('%s exists on %s for service %s/%s' % (file_name, branch_name, self.args['org'], self.service_name))
        return errors

    def is_present(self, file_name, branch):
        present = True
        try:
            # /repos/:owner/:repo/contents/:path
            url = build_url_to_api(
                "%(domain)s/repos/%(org)s/%(repo)s/contents/%(file_name)s?access_token=%(token)s&ref=%(ref)s",
                {'org':self.args['org'], 'repo':self.args['repo'], 'file_name':file_name, 'ref':branch})
            result = pull_json_obj(url)
        except HTTPError as e:
            present = False
        return present

    def error_text(self):
        return ',\n'.join(self.errors)


class ServiceRootDirectoryAbsent(FabricBase):

    def description(self):
        return "Checking that the root directory for the service is absent."

    def run(self, **args):
        """
        Public: Checks that the root directory, i.e.: /opt/webapp/{{service}} is absent

        service_name - the service we're testing for
        """
        self.args = args
        with warn_only(self._service_path()):
            self.result = run("if [ -d /opt/webapp/%s ]; then echo 'yep'; fi" % self.service_name)
        return self.validate_logic(self.result != 'yep')

    def error_text(self):
        output = "The root directory /opt/webapp/%s already exists." % self.service_name
        return self.error_logic(output)

class AppEnvRepoAbsent(FabricBase):

    def description(self):
        return "Checking that the appenv for the service does not exist."

    def run(self, **args):
        """
        Public: Checks that the appenv in github is not present
        """
        self.args = args
        try:
            # /repos/:owner/:repo/contents/:path
            url = build_url_to_api(
                "%(domain)s/repos/%(org)s/%(repo)s/?access_token=%(token)s",
                {'org':self.args['org'], 'repo':self.args['repo']})
            result = pull_json_obj(url)
            self.is_valid = False
        except HTTPError as e:
            self.is_valid = True
        return self.is_valid

    def error_text(self):
        return "The appenv %s/%s cannot exist." % (self.args['org'], self.args['repo'])


class PythonPackagePresent(FabricBase):

    def description(self):
        return "Checking that the package exsits in CheesePrism"

    def run(self, package_url):
        """
        Public: Calls cheeseprism, asking for package

        package_url = the url to the package in cheeseprism
        """
        self.package_url = package_url

        requests.get(package_url)
        if requests.ok:
            self.is_valid = True
        else:
            self.is_valid = False

    def error_text(self):
        return "Can find the package '%s' on yorick." % self.package_url


