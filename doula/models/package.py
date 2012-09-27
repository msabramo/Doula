from contextlib import contextmanager
from datetime import datetime
from doula.config import Config
from doula.github import get_package_github_info
from doula.cheese_prism import CheesePrism
from fabric.api import *
from git import *
from sets import Set
import logging
import os
import pwd
import re
import shutil

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
    def __init__(self, name, version, remote):
        self.name = name
        self.version = version
        self.remote = remote
        self.github_info = False

    def get_github_info(self):
        if not self.github_info:
            self.github_info = get_package_github_info(self.name)
        return self.github_info

    def get_versions(self):
        pypackage = CheesePrism.find_package_by_name(self.name)
        versions = pypackage.versions

        if not self.version in versions:
            versions.append(self.version)

        # Make sure no duplicates exist
        return [ver for ver in Set(versions)]

    def distribute(self, branch, new_version):
        with self.repo(branch) as repo:
            self.update_version(repo, new_version)
            self.commit(repo, ['setup.py'], 'bump version')
            self.tag(repo, new_version)
            self.push(repo, "origin")
            self.upload(repo)

    @contextmanager
    def repo(self, branch):
        repo = None

        try:
            # Where all of the cloned repos are placed
            if not os.path.exists('repos'):
                os.mkdir('repos')
            repo_path = os.path.join('repos', self.name)

            # Clone specified service's repo
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
            # Clean up repo directory
            if repo and os.path.isdir(repo.working_dir):
                shutil.rmtree(repo.working_dir)

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
            if re.match(r'^\*\* Copyright', line.strip(), re.I):
                new_line = "** Copyright SurveyMonkey %s **" % datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
                updated_lines.append(new_line)
            elif re.match(r'(version\s+=\s(\'|")(.+)(\'|"))', line.strip(), re.I):
                updated_lines.append("version = '%s'" % version)
            elif re.match(r'^Source: ', line.strip(), re.I):
                # remote_url takes format: git@github.com:Doula/Doula.git
                org_and_proj = remote_url.split(':')[1].replace('.git', '')
                vals = (org_and_proj, branch, parent_sha[:7])
                new_line = 'Source:      %s *%s %s' % vals
                updated_lines.append(new_line)
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

        with lcd(repo.working_dir):
            url = Config.get('doula.cheeseprism_url') + '/simple'
            s = local('python setup.py sdist upload -r ' + url, capture=True)
            logging.info(s)
