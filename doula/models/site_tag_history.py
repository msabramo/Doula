import os

from git import Git
from git import Repo

remote_git = 'git@code.corp.surveymonkey.com:alexv/sitetaghistory.git'
path = '/Users/alexvazquezOLD/boxes/Doula/temp/sitetaghistory'
site = 'alexv_laptop'
root_path = '/opt/webapp'
repo_name = 'sitetaghistory'


# Need to add submodule to these applications, at a specific tag 
# git@code.corp.surveymonkey.com:alexv/createweb.git - testing_tag.1.0.4
# git@code.corp.surveymonkey.com:alexv/papi.git      - tag 1.0.0.111
# git@code.corp.surveymonkey.com:alexv/billweb.git   - tag 1.0.1

# during development clear everything out from /opt/webapp

# Tag applications with changed states
# Make sure the application is on the same branch as as the site. so there u go.

# Hold onto the tags and refs to repos

# If repo does not exist at the /opt/webapp/ level create it
# If the branch for this site does not exist, create it.
# Add applications as submodules. submodules point to a specific tag
# commit main module
# push main module

# see http://packages.python.org/GitPython/0.3.2/tutorial.html#initialize-a-repo-object

class SiteTagHistory(object):
    """
    Site tag manages the Site Tag History Repo that keeps track of
    the applications tagged together for deployment.
    """
    def get_main_repo(self):
        # determine if the repo already exist
        repo_path = root_path + '/' + repo_name

        if os.path.isdir(repo_path):
            repo = Repo(repo_path)
            print repo
            print repo.bare
        else:
            repo = Repo.init("/var/git/git-python.git", bare=True)
            os.makedirs(repo_path)

        # if it does not exist create it
        # return a reference to main repo

if __name__ == '__main__':
    sth = SiteTagHistory()
    sth.get_main_repo()