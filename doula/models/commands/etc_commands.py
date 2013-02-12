from pyramid.renderers import render
from doula.models.fabric_base import FabricBase
from doula.github import build_url_to_api, post_url, delete_url
from doula.util import pull_json_obj
from requests import HTTPError
import requests
import tempfile
from doula.util_fabric import *
import re
import json
from jinja2 import Environment, PackageLoader
from pyramid import testing
from pyramid_jinja2 import renderer_factory

class WriteTemplates(FabricBase):

    def description(self):
        return "Creating the nginx template."

    def run(self, **args):
        """
        Public: pulls and writes the nginx template
        """
        self.args = args
        self.set_templates()

        nginx = self.put_file('nginx.conf', 
                self.nginx_template).succeeded
        supervisor = self.put_file('supervisor.conf', 
                self.supervisor_template).succeeded
        app = self.put_file('app.ini', 
                self.ini_template).succeeded

        self.is_valid = nginx and supervisor and app
        return self.is_valid

    def put_file(self, path, string):
        with warn_only(self._service_path()):
            with tempfile.NamedTemporaryFile() as f:
                f.write(string)
                return put(f, 'etc/%s' % path)

    def set_templates(self):
        tpl_vars = {'service_name':self.service_name,
                    'paster_command':self.pserve(),
                    'upstream_port_prefix':self.args['upstream_prefix'],
                    'ports':self.ports(),
                    'num_procs': self.args['numprocs'],
                    'proc_len': self.proc_len(),
                    'vip_port': self.args['vip_port']}

        self.nginx_template = render(
                'doula:templates/env_setup/nginx.html', tpl_vars)
        self.supervisor_template = render(
                'doula:templates/env_setup/supervisor.html', tpl_vars)
        self.ini_template = render(
                'doula:templates/env_setup/app.ini.html', tpl_vars)

    def ports(self):
        prefix = str(self.args['upstream_prefix'])
        numprocs = int(self.args['numprocs'])
        return [prefix + str(x).zfill(self.proc_len()) for x in range(numprocs)]

    def proc_len(self):
        return 4 - len(str(self.args['upstream_prefix']))

    def pserve(self):
        if self.args['is_pserve']:
            return "pserve"
        else:
            return "paster serve"

    def error_text(self):
        # not using error_logic because a failed put only returns
        # an empty list
        return "Unable to create nginx file"

class CommitGitRepo(FabricBase):

    def description(self):
        return "Commiting work and creating branches."

    def run(self, **args):
        """
        Public: commits files to all MTs

        """
        self.args = args
        with warn_only(self._choose_path()):
            results = []
            command = "\
                      git add .; \
                      git commit -am 'first commit for new environment'; \
                      "
            result = run(command)

            self.success = result.succeeded
            if not self.success:
                self.errors.append("%s: %s" % (command, result))

            self.errors = []
            mts = ['mt' + str(x) for x in [1, 2, 3, 4, 5]]
            for mt in mts:
                command = "\
                          git checkout -b %(mt)s; \
                          " % {'mt':mt}
                result = run(command)
                self.success = self.success and result.succeeded
                if not self.success:
                    self.errors.append("%s: %s" % (command, result))

        return self.success

    def error_text(self):
        return "The following errors were detected. %s" % ', '.join(self.errors)

class PushGitRepo(FabricBase):

    def description(self):
        return "Pushing the repo"

    def run(self, **args):
        """
        Public: commits files to all MTs

        """
        self.args = args
        with warn_only(self._choose_path()):
            self.success = True
            self.errors = []
            mts = ['mt' + str(x) for x in [1, 2, 3, 4, 5]]
            for mt in mts:
                command = "\
                          git push origin %(mt)s; \
                          " % {'mt':mt}
                result = run(command)
                self.success = self.success and result.succeeded
                if not self.success:
                    self.errors.append("%s: %s" % (command, result))

        return self.success

    def error_text(self):
        return "The following errors were detected. %s" % ', '.join(self.errors)
