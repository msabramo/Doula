import json
import os
import logging
import subprocess
import sys

from git import Git
from git import Repo
from git import Submodule
from doula.util import git_dirify
from doula.util import dumps

log = logging.getLogger('doula')
log.setLevel(logging.INFO)
std_out = logging.StreamHandler(sys.__stdout__)
log.addHandler(std_out)

class SiteTagHistory(object):
    """
    Site tag manages the Site Tag History Repo that keeps track of
    the services tagged together for deployment.
    """
    def __init__(self, path, remote, branch, log_path):
        self.path = path
        self.remote = remote
        self.branch = git_dirify(branch)
        self.log_path = log_path
        self.repo = self._checkout_repo(path, remote)
    def tags(self):
        # need to return a list of tags here for the site tag history
        pass

    def tag_site(self, tag, msg, apps):
        """ 
        Tag every app with the new tag. Then tag the sitetaghistory repo
        with the tag and every repo as a submodule for that branch. The branch
        will always be equal to the site.

        The tag is a simple string
        The branch is the name of the site
        The apps is a dictionary of Application objects. {'app name': service object}
        """
        # alextodo, need to check for duplicate tags
        # need to be able to autogenerate a tag.
        tag = git_dirify(tag)
        log.info("Adding new tag '%s'." % tag)

        self._tag_services(tag, msg, apps)
        self._add_apps_as_submodules(apps, tag)
        self._add_and_commit_submodules(apps)
        self._tag_site_tag_history(tag, msg)

        # after moving this logic to site. make the status tagged.

    def _tag_services(self, tag, msg, apps):
        """Tag every service. Push those changes now."""
        # check if the directory exist for each app below the path dir
        # if it does not check it out at the branch
        # then check if the tag exist if it does not tag it
        # push change to server
        for app_name, app in apps.iteritems():
            path_to_app = self.path + '/' + app.name
            app.repo = self._checkout_repo(path_to_app, app.remote)
            self._tag_repo(app.repo, tag, msg)

    def _add_apps_as_submodules(self, apps, tag):
        for name, app in apps.iteritems():
            path_to_app = self.path + '/' + app.name
            log.info("Adding apps as submodules")

            if app.remote == '':
                msg = "Application '%s' does not have a valid Git remote." % (app.name)
                raise Exception(msg)

            self._cmd('git submodule add ' + app.remote + ' ' + app.name)
            self._cmd('git submodule init')
            self._cmd('git submodule update')
            # Checkout the submodule to a specific tag
            self._cmd('git checkout ' + tag, path_to_app)

    def _add_and_commit_submodules(self, apps):
        """
        Add all the files and submodules to the master repo.
        """
        # Gitpython was corrupting tree. Going with old school command line.
        # rebase prior to changes
        log.info('Adding and committing submodules')

        self._cmd('git pull origin ' + self.branch)
        self._cmd('git checkout ' + self.branch)
        self._cmd('git add .')
        self._cmd('git commit -a -m "Commit_from_Doula"')
        self._cmd('git push origin ' + self.branch)

    def _cmd(self, cmd, path=None):
        """Run a git command from the correct dir."""
        if not path:
            path = self.path

        f = open(self.log_path, 'a', 0)
        f.write('Running command: ' + cmd + "\n")
        cmd_list = ['cd', path]
        cmd_list.extend(cmd.split())

        # Just need to do specify the name of the log file
        cmd = 'cd ' + path + ' && ' + cmd + ' >> ' + self.log_path
        # alextodo, still need to figure out how to putput result, this works
        g = Git()
        rslt = g.execute(cmd_list, output_stream=f)
        print 'RSLT: ' + str(rslt)
        f.close()


    def _tag_site_tag_history(self, tag, msg):
        """Tag the site tag history repo."""
        log.info('Tagging site tag history with tag %s' % tag)

        self._tag_repo(self.repo, tag, msg)

    def _tag_repo(self, repo, tag, msg):
        """Tag the repo on the active branch. As is today."""
        repo.create_tag(tag, message=msg)
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
        # Checkout the branch that the site is currently on. All the repos
        # including submodules must be on the same branch.
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

# alextodo, put into a unit test
def get_random_tag():
    num = random.randrange(0, 1000000)
    return 'test_tag ' + str(num)

def get_services():
    services = { }

    with open('temp/services.json') as app_file:
        rslt = json.loads(app_file.read())

        for app in rslt['services']:
            a = Application.build_app('test site name', 'test node name', 'http://url', app)
            services[a.name_url] = a

    return services

# see http://packages.python.org/GitPython/0.3.2/tutorial.html#initialize-a-repo-object

# Logic https://github.com/Doula/Doula/wiki/Tag-of-Tags-Logic
tag_history_path = '/Users/alexvazquezOLD/boxes/Doula/temp/site_tag_history'
tag_history_remote = 'git@code.corp.surveymonkey.com:alexv/site_tag_history.git'

if __name__ == '__main__':
    os.system('rm -rf ' + tag_history_path)
    sth = SiteTagHistory(tag_history_path, tag_history_remote, 'mttest', 'output.log')

    tag = get_random_tag()
    branch = 'mt1'
    apps = get_services()
    
    sth.tag_site(tag, 'tagging site test', apps)

