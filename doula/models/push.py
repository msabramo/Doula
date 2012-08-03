import os
from fabric.api import *
from fabric.context_managers import cd
from fabric.context_managers import prefix
from fabric.context_managers import settings
from fabric.context_managers import hide
from contextlib import contextmanager

@contextmanager
def debuggable(debug=False):
    if debug:
        yield
    else:
        with hide('warnings', 'running', 'stdout', 'stderr'):
            yield

class Push(object):

    def __init__(self, web_app_dir, cheeseprism_url, keyfile, node_dns_name_or_ip, debug=False):
        self.web_app_dir = web_app_dir
        self.cheeseprism_url = cheeseprism_url
        self.keyfile = keyfile
        env.host_string = node_dns_name_or_ip
        env.user = 'root'
        env.key_filename = self.keyfile

    def packages(self, service_name, packages):
        self.service_name = service_name
        self.packages = packages

        failures = []
        successes = []
        with cd(os.path.join(self.web_app_dir, self.service_name)):
            with debuggable(debug):
                with prefix('source bin/activate'):
                    with settings(warn_only=True):
                        for package in packages:
                            result = run('pip install -i %s %s' % (self.cheeseprism_url, package))
                            if result.failed:
                                failures.append({'package': package, 'error': str(result).replace('\n', ', ')})
                            else:
                                successes.append(package)
        self._chown(debug)
        return (failures, successes)


    """
    This call does the following:
        * gets the branch name
        * removes any untracked files and directories (http://stackoverflow.com/a/4779723/182484)
        * resets the repo
        * pulls the changes

    We do all this to avoid merge conflicts
    """
    def config(self, service_name, debug=False):
        self.service_name = service_name
        with cd(os.path.join(self.web_app_dir, self.service_name, 'etc')):
            with debuggable(debug):
                result = self._pull_config()

        if result.failed: raise Exception(str(result).replace('\n', ', '))
        self._chown(debug)
        return result


    def _pull_config(self):
        branch = run('git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3')
        result = run('git clean -f -d')
        if result.succeeded:
            result = run('git reset --hard HEAD')
            if result.succeeded:
                result = run('git pull origin %s' % branch)
        return result


    def _chown(self, debug=False):
        with debuggable(debug):
            result = sudo('chown -R %suser:sm_users %s' % (self.service_name, os.path.join(self.web_app_dir, self.service_name)))
        if result.failed: raise Exception(str(result).replace('\n', ', '))


    def commit(self, packages, debug=False):
        with cd(os.path.join(self.web_app_dir, self.service_name)):
            with debuggable(debug):
                branch = run('git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3')
                result = run('git add -a .')
                if result.succeeded:
                    result = run('git commit -am "Pushed packages: %s"' % ",".join(packages))
                    if result.succeeded:
                        result = run('git push origin %s' % branch)
        if result.failed:
            raise Exception(str(result))