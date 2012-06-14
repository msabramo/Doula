import os
import os.path
import shutil
from fabric.api import *
from tempfile import TemporaryFile
from git import *


def distribute(service, branch, new_version):
    # Where all of the cloned repos are placed
    if not os.path.exists('repos'):
        os.mkdir('repos')
    repo_path = os.path.join('repos', service)

    # Clone specified service's repo
    repo = Repo.clone_from("git@code.corp.surveymonkey.com:joed/%s.git" % service,
                           repo_path)

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

    # Commit change to repo
    index = repo.index
    index.add(['setup.py'])
    index.commit("DOULA: Updated Version Number")

    # Push changes
    origin = repo.remotes.origin
    origin.pull()
    origin.push()

    # Call `python setup.py sdist upload` to put upload to cheeseprism
    with lcd(repo.working_dir):
        local('python setup.py sdist upload')

    # Clean up repo directory
    shutil.rmtree(repo.working_dir)


if __name__ == "__main__":
    distribute("BillWeb", "master", "1.3.2")
