from contextlib import contextmanager
from doula.models.user import User
from doula.models.release_dal import ReleaseDAL
from doula.models.release import Release
from fabric.api import *
from fabric.context_managers import cd
from fabric.context_managers import hide
from fabric.context_managers import prefix
from fabric.context_managers import settings
import os
import time
import json
import logging
import re


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
            source = 'source %s/../bin/activate' % path
        else:
            source = 'source %s/bin/activate' % path
        with prefix(source):
            with debuggable(debug):
                with settings(warn_only=True):
                    yield


class Push(object):

    def __init__(self,
            service_name,
            node_ip,
            username,
            web_app_dir,
            cheeseprism_url,
            keyfile,
            outdir,
            site,
            debug=False):

        self.service_name = service_name
        self.username = username
        self.outdir = outdir
        self.site = site

        if debug:
            self.email = 'tims@surveymonkey.com'
        else:
            user = User.find(username)
            self.email = user['email']

        self.web_app_dir = web_app_dir
        self.cheeseprism_url = os.path.join(cheeseprism_url, 'index')
        self.keyfile = keyfile

        env.host_string = node_ip
        self.debug = debug
        env.key_filename = self.keyfile
        self.pip_freeze = ''
        logging.getLogger().setLevel(logging.ERROR)

    #override for testing
    def fabric_user(self):
        return 'doula'

    def packages(self, manifest):
        env.user = self.fabric_user()
        self.packages = ['%s==%s' % (x, y) for x, y in manifest['pip_freeze'].iteritems()]
        self.manifest = manifest

        failures = []
        successes = []

        #pull latest config
        self.config()

        #for safety, on systems that don't have group write permissions
        self._chown()

        with workon(self._webapp(), self.debug):
            if self.manifest['is_rollback']:
                self.rollback(self._etc_sha1())

            for package in self.packages:
                result = run('pip install -i %s %s' % (self.cheeseprism_url, package))
                if result.succeeded:
                    successes.append(package)
                else:
                    failures.append({'package': package, 'error': str(result).replace('\r\n', ', ')})

        #assets like css, js
        success, result = self.install_assets()

        if not success:
            logging.error("Unable to install assets for %s" % self.service_name)
            failures.append({'service': self.service_name, 'error': str(result).replace('\r\n', ', ')})

        if not failures:
            #set a nice commit message
            message = "%s installed %s package(s):\n%s\n\n" % \
                    (self.username, len(self.packages), \
                    "\n".join(["installed: %s" % x for x in self.packages]))

            freeze_text = self._freeze()
            manifest = self._manifest(freeze_text)
            self.write_manifest(manifest)

            message = message + self.pretty_pip(freeze_text)
            self.commit(message)

        if failures:
            print 'Failed to Push', failures

            logging.error("Failed to push %s" % self.service_name)
            logging.error(failures)

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

    def rollback(self, etc_sha1):
        with workon(self._webapp(), self.debug):
            run('pip freeze | xargs pip uninstall -y')

        with workon(self._etc(), self.debug):
            etc_remote = run("git remote -v | awk '{print $2}' | head -n 1")
            run('rm -rf /tmp/%s' % self.service_name)
            run('git clone %s /tmp/%s' % (etc_remote, self.service_name))

            with cd('/tmp/%s' % self.service_name):
                result = run('git checkout %s' % self.manifest['etc_sha1'])
                if result.succeeded:
                    result = run('find /tmp/%s/* -maxdepth 1 -type f -exec cp {} /opt/webapp/%s/etc \;' % (self.service_name, self.service_name))
                    if result.succeeded:
                        return

            raise Exception("Rollback Failed: %s" % result)

    def install_assets(self):
        try:
            with workon(self._webapp(), self.debug):
                # We use error instead of info to log because
                # setting the logging status to info would fill up our logs
                # with lots of logging information from Fabric
                logging.error('Running asset check.')

                result = run('asset_check %s' % self.service_name)

                if result.succeeded:
                    logging.error('Assets detected.  gonna bake them up nice and hot')
                    result = sudo('paster --plugin=smlib.assets bake etc/app.ini %s' % self.outdir)

                    logging.error('Asset push completed. Output follows:')
                    logging.error(result)

                    if result.succeeded:
                        return (True, True)
                    else:
                        logging.error("Unable to install assets")
                        raise Exception(result)
                else:
                    #a non-success means that the plugin does not exist
                    #which means we do nothing, so we return success
                    return (True, True)

            return (False, result)
        except:
            raise Exception('Error installing assets for ' + self.service_name)
        finally:
            logging.error("Done running install asset")

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

    def pretty_pip(self, freeze_text):
        with workon(self._webapp(), self.debug):
            # pip freeze's standard out is weird, so we do the following
            # * create temp file var $f
            # * pip pip freeze to $f
            # * cat $f
            # * delete $f, sending stdout to dev null, so it does not show up on output
            hashes = "#################\n"
            freeze = "%s%s%s%s" % (hashes, "pip freeze:\n", hashes, freeze_text)
            return freeze

    def write_manifest(self, manifest):
        path = os.path.join(self.web_app_dir, self.service_name, 'doula.manifest')
        with open(path, 'w') as f:
            f.write(json.dumps(manifest, sort_keys=True,
                    indent=2, separators=(',', ': ')))

    def _manifest(self, freeze_text):
        return {
            'sha1_etc':self._etc_sha1(),
            'doula_release_number':self._get_next_release(),
            'site': self.site,
            'service': self.service_name,
            'pip_freeze': self._freeze_list(freeze_text),
            'is_rollback': self.manifest['is_rollback'],
            'date': int(time.time()),
            'author': self.username
        }

    def _freeze_list(self, freeze_text):
        packages = {}
        for line in freeze_text.splitlines():
            line = line.strip()

            m = re.match(r'(.+)==(.+)', line)

            if m:
                packages[m.group(1)] = m.group(2)

        return packages

    def _get_next_release(self):
        dal = ReleaseDAL()
        return dal.next_release(self.site, self.service_name)

    def _freeze(self):
        with workon(self._webapp(), self.debug):
            return run('f="/tmp/$RANDOM.txt" && pip freeze -l ./ > $f && cat $f && rm -rf $f > /dev/null 2>&1')


    def _branch(self):
        with workon(self._webapp(), self.debug):
            return run('git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3')


    def _etc_sha1(self):
        with cd(self._etc()):
            return run('git rev-parse --verify HEAD')


    def _webapp(self):
        return os.path.join(self.web_app_dir, self.service_name)

    def _etc(self):
        return os.path.join(self.web_app_dir, self.service_name, 'etc')


def get_test_obj(service):
    return Push(service, 'tbone', '/opt/webapp/', 'http://mtclone:6543/index', '/Users/timsabat/.ssh/id_rsa_doula_user', 'mt-99', '/opt/smassets', True)
