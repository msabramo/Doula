from contextlib import contextmanager
from doula.github.github import get_package_github_info
from doula.services.cheese_prism import CheesePrism
from fabric.api import *
from git import *
from tempfile import TemporaryFile
import os
import shutil


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
        versions = pypackage.get_versions() if pypackage else []

        if not self.version in versions:
            versions.append(self.version)

        return versions

    def distribute(self, branch, new_version):
        with self.repo() as repo:
            self.update_version(repo, new_version)
            self.commit(repo, ['setup.py'], 'DOULA: Updating Version.')
            self.push(repo, "origin")
            self.upload(repo)

    @contextmanager
    def repo(self):
        repo = None
        try:
            # Where all of the cloned repos are placed
            if not os.path.exists('repos'):
                os.mkdir('repos')
            repo_path = os.path.join('repos', self.name)

            # Clone specified service's repo
            repo = Repo.clone_from(self.remote, repo_path)
            yield repo
        finally:
            # Clean up repo directory
            if repo:
                shutil.rmtree(repo.working_dir)

    def update_version(self, repo, new_version):
        # Alter setup.py to match the new version
        setup_py_path = os.path.join(repo.working_dir, 'setup.py')
        with open(setup_py_path, 'r+') as f:
            tmp = TemporaryFile()

            for line in f.readlines():
                if line.startswith("version"):
                    line = "version = '%s'\n" % new_version
                tmp.write(line)

            # Go back to the beginning of each file
            tmp.seek(0)
            f.seek(0)

            f.write(tmp.read())

    def commit(self, repo, files, msg):
        # Commit change to repo
        index = repo.index
        index.add(files)
        index.commit(msg)

    def push(self, repo, remote_name):
        # Push changes
        remote = repo.remotes[remote_name]
        remote.pull()
        remote.push()

    def upload(self, repo):
        # Call `python setup.py sdist upload` to put upload to cheeseprism
        with lcd(repo.working_dir):
            # joetodo, read this value from redis
            # key is redis doula.cheeseprism_url
            # doula.cheeseprism_url = http://mtclone.corp.surveymonkey.com:6543/simple
            url = 'http://mtclone.corp.surveymonkey.com:6543/simple'
            local('python setup.py sdist upload -r ' + url)
