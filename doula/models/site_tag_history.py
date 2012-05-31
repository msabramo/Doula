import json
import os

from git import Git
from git import Repo
from git import Submodule
from doula.models.sites import Application
from doula.util import git_dirify


class SiteTagHistory(object):
    """
    Site tag manages the Site Tag History Repo that keeps track of
    the applications tagged together for deployment.
    """
    def __init__(self, path, remote, branch):
        self.path = path
        self.remote = remote
        self.branch = git_dirify(branch)
        self.repo = self._checkout_repo(path, remote)

    def tag_site(self, tag, apps):
        """ 
        Tag every app with the new tag. Then tag the sitetaghistory repo
        with the tag and every repo as a submodule for that branch. The branch
        will always be equal to the site.

        The tag is a simple string
        The branch is the name of the site
        The apps is a dictionary of Application objects. {'app name': application object}
        """
        tag = git_dirify(tag)

        self._tag_applications(tag, apps)
        self._add_apps_as_submodules(apps, tag)
        self._add_and_commit_submodules(apps)
        self._tag_site_tag_history(tag)

    def _tag_applications(self, tag, apps):
        """Tag every application. Push those changes now."""
        # check if the directory exist for each app below the path dir
        # if it does not check it out at the branch
        # then check if the tag exist if it does not tag it
        # push change to server
        for app_name, app in apps.iteritems():
            path_to_app = self.path + '/' + app.name
            app.repo = self._checkout_repo(path_to_app, app.remote)
            self._tag_repo(app.repo, tag)

    def _add_apps_as_submodules(self, apps, tag):
        for name, app in apps.iteritems():
            path_to_app = self.path + '/' + app.name
            # remove dir if it exist. we'll check it out again.
            os.system('rm -rf ' + path_to_app)

            # Gitpython was corrupting tree. Going with old school command line.
            self._git_cmd('git submodule add ' + app.remote + ' ' + app.name)
            self._git_cmd('git submodule init')
            self._git_cmd('git submodule update')
            # Checkout the submodule to a specific tag
            self._git_cmd('cd ' + app.name + '; git checkout ' + tag)

    def _add_and_commit_submodules(self, apps):
        """
        Add all the files and submodules to the master repo.
        """
        # Gitpython was corrupting tree. Going with old school command line.
        self._git_cmd('git add .')
        self._git_cmd('git commit -m "Commiting submodules from Doula"')
        self._git_cmd('git push origin ' + self.branch)

    def _git_cmd(self, cmd):
        """Run a git command from the correct dir."""
        os.system('cd ' + self.path + '; ' + cmd)

    def _tag_site_tag_history(self, tag):
        """Tag the site tag history repo."""
        self._tag_repo(self.repo, tag)

    def _tag_repo(self, repo, tag):
        """Tag the repo on the active branch. As is today."""
        repo.create_tag(tag, message="Tag created by Doula")
        repo.remotes.origin.push(self.get_refspec('tags', tag))

    def _checkout_repo(self, path, remote):
        """
        Check if the repo already exist, if it doesn't create it and return repo obj.
        Do an update on the repo as well after pulling down.
        Switch the head to the selected branch.
        """
        if os.path.isdir(path):
            repo = Repo(path)

            if repo.bare:
                msg = "Path '" + path + "' exist but it is not a git repo."
                raise Exception(msg)
        else:
            repo = Repo.clone_from(remote, path)

        repo.remotes.origin.update()

        # Checkout the branch because the 
        if not repo.active_branch == self.branch:
            new_branch = repo.create_head(self.branch)
            repo.head.reference = new_branch
            repo.head.reset(index=True, working_tree=True)
            repo.remotes.origin.push(self.get_refspec('heads', self.branch))

        return repo

    def get_refspec(self, git_type, git_value):
        # From gitpython docs
        # A "refspec" is used by fetch and push to describe the
        # mapping between remote ref and local ref
        refspec = "refs/%s/%s:refs/%s/%s" % (git_type, git_value, git_type, git_value)
        # If type is heads, it will read: publish my local branch [branch] as [branch]
        # to the origin URL
        return refspec

# For development
import random

def get_random_tag():
    num = random.randrange(0, 1000000)
    return 'test_tag ' + str(num)

def get_applications():
    applications = { }

    with open('temp/applications.json') as app_file:
        rslt = json.loads(app_file.read())

        for app in rslt['applications']:
            a = Application.build_app('test site name', 'test node name', 'http://url', app)
            applications[a.name_url] = a

    return applications

# Need to add submodule to these applications, at a specific tag 
# git@code.corp.surveymonkey.com:alexv/createweb.git - testing_tag.1.0.4
# git@code.corp.surveymonkey.com:alexv/papi.git      - tag 1.0.0.111
# git@code.corp.surveymonkey.com:alexv/billweb.git   - tag 1.0.1

# see http://packages.python.org/GitPython/0.3.2/tutorial.html#initialize-a-repo-object

# Logic https://github.com/Doula/Doula/wiki/Tag-of-Tags-Logic
tag_history_path = '/Users/alexvazquezOLD/boxes/Doula/temp/site_tag_history'
tag_history_remote = 'git@code.corp.surveymonkey.com:alexv/site_tag_history.git'

if __name__ == '__main__':
    os.system('rm -rf ' + tag_history_path)
    sth = SiteTagHistory(tag_history_path, tag_history_remote, 'mttest')

    tag = get_random_tag()
    branch = 'mt1'
    apps = get_applications()
    
    sth.tag_site(tag, apps)

