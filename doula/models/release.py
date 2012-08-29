from doula.config import Config
from doula.github.github import get_appenv_repos
from doula.models.package import Package
import re


class Release(object):
    def __init__(self, name, date, branch, packages):
        # alextodo change this too. a release should not have a name
        # it's identified by it's date stupid
        self.name = name
        self.date = date
        self.branch = branch
        self.packages = packages

    @staticmethod
    def build_release_from_repo(repo, commit):
        """
        Build a release object from an app env repo with the format
        and a commit that is a single commit of this repo object
            {
            'commits': [
                {
                    'date': '2012-08-27T22: 59: 17+00: 00',
                    'message': "Pushedpanel==1.0.24
                        ##################
                        pipfreeze:
                        ##################
                        Beaker==1.5.4
                        Chameleon==1.3.0-rc1
                        Elixir==0.7.1
                        JSTools==0.5
                        "
                }
            ],
            'name': 'panel'
        }
        """
        # alextodo. update once tim pulls the branch here
        # can i pull that? any way?
        packages = []
        start_looking_for_packages = False

        for line in commit['message'].splitlines():
            line = line.strip()

            if re.match(r'^#+$', line):
                start_looking_for_packages = True

            if start_looking_for_packages:
                m = re.match(r'(.+)==(.+)', line)

                if m:
                    packages.append(Package(m.group(1), m.group(2), ''))

        return Release(repo['name'], commit['date'], 'mt3', packages)

    @staticmethod
    def get_releases(branch, service_name):
        # Dev pulls from mt3 by default
        if Config.get('env') == 'dev':
            repos = get_appenv_repos('mt3')
        else:
            repos = get_appenv_repos(branch)

        releases = []

        for name, repo in repos.iteritems():
            if service_name == name:
                for commit in repo["commits"]:
                    release = Release.build_release_from_repo(repo, commit)
                    releases.append(release)

        return releases
