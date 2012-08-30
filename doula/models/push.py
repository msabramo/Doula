from contextlib import contextmanager
from doula.models.user import User
from fabric.api import *
from fabric.context_managers import cd
from fabric.context_managers import hide
from fabric.context_managers import prefix
from fabric.context_managers import settings
import os

import logging


@contextmanager
def debuggable(debug=False):
    if debug:
        yield
    else:
        with hide('warnings', 'running', 'stdout', 'stderr'):
            yield


@contextmanager
def workon(path, debug):
    with cd(path):
        if 'etc' in path:
            source = '. ../bin/activate'
        else:
            source = '. bin/activate'
        with prefix(source):
            with debuggable(debug):
                with settings(warn_only=True):
                    yield


class Push(object):

    def __init__(self, service_name, username, web_app_dir, 
            cheeseprism_url, keyfile, site_name_or_node_ip, user_id, debug=False):

        self.service_name = service_name
        self.username = username

        user = User.find(username)
        self.email = user['email']

        self.web_app_dir = web_app_dir
        self.cheeseprism_url = os.path.join(cheeseprism_url, 'index')
        print 'url:', self.cheeseprism_url
        self.keyfile = keyfile
        env.host_string = site_name_or_node_ip
        self.debug = debug
        env.user = 'doula'
        env.key_filename = self.keyfile
        self.pip_freeze = ''
        logging.getLogger().setLevel(logging.INFO)

    def packages(self, packages, action='install'):
        assert(action in ['install', 'uninstall'])
        self.packages = packages

        failures = []
        successes = []

        #for safety, on systems that don't have group write permissions
        self._chown()

        with workon(self._webapp(), self.debug):
            for package in packages:
                with prefix('. bin/activate'):
                    if action == 'install':
                        result = run('pip install -i %s %s' % (self.cheeseprism_url, package))
                    else:
                        #the -y flag automatically says yes to confirmation prompts
                        result = run('pip uninstall %s -y' % package)
                if result.succeeded:
                    successes.append(package)
                else:
                    failures.append({'package': package, 'error': str(result).replace('\r\n', ', ')})

        if not failures:
            #set a nice commit message
            message = "%s %sed %s package(s):\n%s\n\n" % \
                    (self.username, action, len(packages), \
                    "\n".join(["%sed: %s" % (action, x) for x in packages]))
            message = message + self.get_pip_freeze()
            self.commit(message)

        self.config()
        if failures:
            print 'failing!', failures
            raise Exception(failures)

        return successes, failures
    """
    This call does the following:
        * gets the branch name
        * removes any untracked files and directories (http://stackoverflow.com/a/4779723/182484)
        * resets the repo
        * pulls the changes

    We do all this to avoid merge conflicts
    """
    def config(self):
        with workon(self._etc(), self.debug):
            result = run('git clean -f -d')
            if result.succeeded:
                result = run('git reset --hard HEAD')
                if result.succeeded:
                    result = run('git pull origin %s' % self._branch())
                else:
                    raise Exception(str(result).replace('\n', ', '))

        self._chown()
        return result

    def _chown(self):
        with debuggable(self.debug):
            path = os.path.join(self.web_app_dir, self.service_name)
            result = sudo('chown -R %suser:sm_users %s' % (self.service_name, path))
            if result.succeeded:
                sudo('chmod -R g+rwx %s' % path)
        if result.failed:
            raise Exception(str(result).replace('\n', ', '))

    def commit(self, message):
        with workon(self._webapp(), self.debug):
            result = run('git add -A .')
            if result.succeeded:
                changes = run("git status --porcelain 2> /dev/null | sed -e 's/ M etc//g' | sed '/^$/d'")
                if changes:
                    author = "%s <%s>" % (self.username, self.email)
                    result = run('git commit --author="%s" -am "%s"' % (author, message))
                    if result.succeeded:
                        result = run('git push origin %s' % self._branch())

            if result.failed:
                raise Exception(str(result))

    def get_pip_freeze(self):
        with workon(self._webapp(), self.debug):
            # pip freeze's standard out is weird, so we do the following
            # * create temp file var $f
            # * pip pip freeze to $f
            # * cat $f
            # * delete $f, sending stdout to dev null, so it does not show up on output
            freeze = run('f="/tmp/$RANDOM.txt" && pip freeze -l ./ > $f && cat $f && rm -rf $f > /dev/null 2>&1')
            hashes = "#################\n"
            freeze = "%s%s%s%s" % (hashes, "pip freeze:\n", hashes, freeze)
            return freeze

    def _branch(self):
        return run('git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3')

    def _webapp(self):
        return os.path.join(self.web_app_dir, self.service_name)

    def _etc(self):
        return os.path.join(self.web_app_dir, self.service_name, 'etc')


def get_test_obj(service):
    return Push(service, 'tbone', '/opt/webapp/', 'http://mtclone:6543/index', '/Users/timsabat/.ssh/id_rsa_doula_user', 'mt-99', True)
