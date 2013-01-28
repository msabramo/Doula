from contextlib import contextmanager
from datetime import datetime
from doula.cache import Redis
from doula.cheese_prism import CheesePrism
from doula.config import Config
from doula.github import get_package_github_info
from doula.util import comparable_name
from fabric.api import *
from git import *
from sets import Set
import logging
import os
import pwd
import re
import shutil
import sys

"""
Git-Python makes a call to os.getlogin that fails
in a non-terminal env. This call here patches that error
with a valid call to getlogin
"""
os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]


class Package(object):
    """
    Represents a python package
    """
    def __init__(self, name, version, remote=''):
        self.name = name
        self.comparable_name = comparable_name(name)
        self.version = version
        self.remote = remote
        self.github_info = False

    def get_github_info(self):
        if not self.github_info:
            self.github_info = get_package_github_info(self.name)
        return self.github_info

    def get_versions(self):
        pypackage = CheesePrism.find_package_by_name(self.name)
        versions = []

        if pypackage:
            versions = pypackage.versions

        if not self.version in versions:
            versions.append(self.version)

        # Make sure no duplicates exist
        return [ver for ver in Set(versions)]

    def get_current_version(self):
        """
        Return the current active package version
        """
        versions = self.get_versions()
        versions.sort()

        return versions[len(versions) - 1]

    def distribute(self, branch, new_version):
        with self.repo(branch) as repo:
            # Ensure dev doesn't try to push to github repos.
            if Config.get('env') != 'dev':
                self.update_version(repo, new_version)
                self.commit(repo, ['setup.py'], 'bump version')
                self.tag(repo, new_version)
                self.push(repo, "origin")

            self.upload(repo)

    @staticmethod
    def get_sm_packages():
        """
        Pull all the survey monkey packages
        """
        sm_packages = []
        found_sm_package_names = []
        all_python_packages = CheesePrism.all_packages()

        for python_package in all_python_packages:
            sm_package = Package(python_package.name, python_package.get_last_version())

            if sm_package.get_github_info():
                # Hold onto the comparable name. check later
                # if we already have this name
                found_sm_package_names.append(sm_package.comparable_name)
                sm_packages.append(sm_package)

        # Pull the devmonkey repos. If not a cheese prism package
        # return as an empty cheese prism package
        redis = Redis.get_instance()
        repo_names = redis.smembers("repo.devmonkeys")

        for repo_name in repo_names:
            if not comparable_name(repo_name) in found_sm_package_names:
                sm_package = Package(repo_name, '')
                sm_packages.append(sm_package)

        return sm_packages

    @staticmethod
    def get_sm_package_by_name(package_name):
        package = False

        for pckg in Package.get_sm_packages():
            if pckg.comparable_name == comparable_name(package_name):
                package = pckg
                break

        return package

    @contextmanager
    def repo(self, branch):
        repo = None

        try:
            # Where all of the cloned repos are placed
            if not os.path.exists('repos'):
                os.mkdir('repos')
            repo_path = os.path.join('repos', self.name)

            # Make sure the repo dir does not exist
            self.rm_repo_dir(repo_path)

            # Clone specified service's repo
            # alextodo, look at cleaning up the end of the repo path
            # the directory itself should be lowercased. we want to move to
            # to standardized packages. or maybe we just handle on front end.
            repo = Repo.clone_from(self.remote, repo_path)

            # Pull the latest changes from the branch the user selected
            vals = (repo_path, branch)

            os.system('cd %s && git checkout -b %s' % vals)
            os.system('cd %s && git fetch origin %s' % vals)
            os.system('cd %s && git reset --hard origin/%s' % vals)

            # Use the newest branch and commit as the newest repo
            repo = Repo.init(repo_path)

            yield repo
        finally:
            self.rm_repo_dir(repo_path)

    def rm_repo_dir(self, repo_path):
        # Clean up repo directory
        if os.path.isdir(repo_path):
            shutil.rmtree(repo_path)

    def update_version(self, repo, new_version):
        """
        Update the setup.py with a new version, parent sha, branch and author
        """
        logging.info('Updating the version to %s' % new_version)
        setup_dot_py = None

        try:
            setup_py_path = os.path.join(repo.working_dir, 'setup.py')

            setup_dot_py = open(setup_py_path, 'r')
            lines = setup_dot_py.readlines()
            setup_dot_py.close()

            updated_setup_dot_py = self.get_updated_setup_dot_py(
                lines, new_version, repo.active_branch.name,
                repo.remotes.origin.url, repo.head.commit.hexsha)

            setup_dot_py = open(setup_py_path, 'w')
            setup_dot_py.write(updated_setup_dot_py)
            setup_dot_py.close()
        finally:
            logging.info('Updated the version.')
            if setup_dot_py:
                setup_dot_py.close()

    def get_updated_setup_dot_py(self, lines, version, branch, remote_url, parent_sha, user=''):
        """
        Update the setup.py values (version number, branch, parent sha and user)
        before we push up the latest commit. Here we simply roll through the current
        lines in the setup.py and return a list with the updated lines
        """
        updated_lines = []

        for line in lines:
            if re.match(r'(version\s+=\s(\'|")(.+)(\'|"))', line.strip(), re.I):
                updated_lines.append("version = '%s'" % version)
            else:
                updated_lines.append(line.rstrip())

        return "\n".join(updated_lines)

    def commit(self, repo, files, msg):
        # Commit change to repo
        logging.info('Committing to code.corp.surveymonkey.com')
        index = repo.index
        index.add(files)
        index.commit(msg)

    def tag(self, repo, version):
        # Tag a version
        logging.info('Tagging the new version.')
        version = re.sub(r'^v', '', str(version))
        repo.create_tag('v' + version)

    def push(self, repo, remote_name):
        # Push changes
        logging.info('Pushing to code.corp.surveymonkey.com')
        remote = repo.remotes[remote_name]
        remote.push()
        remote.push(tags=True)

    def upload(self, repo):
        # Call `python setup.py sdist upload` to put upload to cheeseprism
        logging.info('Releasing to cheeseprism.')

        try:
            with lcd(repo.working_dir):
                url = Config.get('doula.cheeseprism_url') + '/simple'
                command = 'python setup.py sdist upload -r ' + url
                logging.info("command: %s" %  command)
                result = local(command, capture=True)

                logging.info(result)

                # Check for a 200 success
                if not re.search(r'server\s+response\s+\(200\)', result, re.I):
                    logging.error("Error building new package")
                    raise Exception("Error building new package")
        except:
            # We make sure that the result always runs. sometimes we error out
            # and the call is killed, catch all for errors
            logging.error(sys.exc_info())
            raise Exception('Error uploading ' + self.name + ' to Cheese Prism.')
