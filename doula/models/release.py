from doula.config import Config
from doula.github import get_appenv_releases
from doula.models.package import Package
import re


class Release(object):
    def __init__(self, author, date, branch, packages):
        self.author = author
        self.date = date
        self.branch = branch
        self.packages = packages

    @staticmethod
    def build_release_from_repo(branch, service_name, commit):
        """
        Build a release object from an app env repo with the format
        and a commit that is a single commit of this repo object
            {
            'commits': [
                {
                    'author': 'test@surveymonkey.com',
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
            ]
        }
        """
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

        return Release(commit["author"], commit['date'], branch, packages)

    @staticmethod
    def get_releases(branch, service_name):
        # Dev pulls from mt3 by default because otherwise it's
        # the name of the local machine
        if Config.get('env') == 'dev':
            commits = get_appenv_releases(service_name, 'mt3')
        else:
            commits = get_appenv_releases(service_name, branch)

        releases = []

        for cmt in commits:
            release = Release.build_release_from_repo(branch, service_name, cmt)
            releases.append(release)

        return releases
