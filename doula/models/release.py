from doula.config import Config
from doula.github import get_appenv_releases
from doula.models.package import Package
from doula.util import date_to_seconds_since_epoch
from sets import Set
import re


class Release(object):
    # See https://github.com/Doula/Doula/wiki/manifest
    # for the definition of a manifest

    def __init__(self, author, date, commit_message, branch, packages):
        self.author = author
        self.date = date
        self.date_in_seconds = date_to_seconds_since_epoch(date)
        self.branch = branch
        self.packages = packages
        self.commit_message = commit_message

        # Manifest attributes
        self.release_number = 0
        self.sha1_etc = ""
        self.site = ""
        self.service = ""
        self.pip_freeze = []
        self.is_rollback = False
        self.project_name = ""
        self.project_release = 0
        self.production = False

    ###################
    # Factory Methods
    ###################

    @staticmethod
    def build_from_dict(dict_data):
        release = Release('author', '2012-01-01T00:00:00', 'commit_message', 'branch', [])
        release.__dict__.update(dict_data)
        # Site and branch are equal
        release.branch = release.site
        release.date_in_seconds = date_to_seconds_since_epoch(dict_data['date'])
        release.packages = Release.build_packages_from_pip_freeze(dict_data['commit_message'])

        return release

    @staticmethod
    def build_release_from_repo(branch, commit):
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
        packages = Release.build_packages_from_pip_freeze(commit['message'])
        return Release(commit["author"], commit['date'], commit['message'], branch, packages)

    @staticmethod
    def build_packages_from_pip_freeze(text):
        """Build packages from text"""
        packages = []
        start_looking_for_packages = False

        for line in text.splitlines():
            line = line.strip()

            if re.match(r'^#+$', line):
                start_looking_for_packages = True

            if start_looking_for_packages:
                m = re.match(r'(.+)==(.+)', line)

                if m:
                    packages.append(Package(m.group(1), m.group(2), ''))

        return packages

    @staticmethod
    def get_releases(branch, service_name):
        # alextodo. remove this after we move to the release_dal
        # Dev pulls from mt3 by default because otherwise it's
        # the name of the local machine
        if Config.get('env') == 'dev':
            commits = get_appenv_releases(service_name, 'mt3')
        else:
            commits = get_appenv_releases(service_name, branch)

        releases = []

        for cmt in commits:
            release = Release.build_release_from_repo(branch, cmt)
            releases.append(release)

        releases.sort(key=lambda x: x.date_in_seconds, reverse=True)

        return releases

    ###########################
    # Diff package and release
    ###########################

    def diff_service_and_release(self, service):
        """
        Diff the service and this release

        Returns a dictionary with the following format:
        {
            "changed_packages": {
                "Anweb": {
                    "package_name": "Anweb",
                    "release_version": 1.1,
                    "service_version": 1.2
                },
                "create": {
                    "package_name": "create",
                    "release_version": 1.1.1,
                    "service_version": 1.1.2
                }
            },
            "packages_to_add": {
                "smlib": {
                    "package_name": 'smlib'
                    "package_version": 1.2
                }
            },
            "packages_to_subtract": {
                "smlib": {
                    "package_name": 'smproxy'
                    "package_name": 2.1
                }
            }
        }
        """
        release_packages = self._build_release_packages_dict()

        return {
            'changed_packages': self._find_same_packages_with_diff_versions(service, release_packages),
            'packages_to_add': self._find_packages_to_add(service, release_packages),
            'packages_to_subtract': self._find_packages_that_will_be_subtracted(service, release_packages)
        }

    def _build_release_packages_dict(self):
        """Build a dict from the release packages list"""
        release_packages = {}

        # release is a list. unlike the service packages. make same in future.
        for package in self.packages:
            release_packages[package.comparable_name] = package

        return release_packages

    def _find_packages_to_add(self, service, release_packages):
        """Find the packages in the release but not in the current service"""
        release_package_names = Set(release_packages.keys())
        service_package_names = Set(service.packages.keys())

        # Packages found on release but not on current service
        # will need to be added to the service environment
        packages_to_add = {}
        package_names_to_add = release_package_names - service_package_names

        for package_name in package_names_to_add:
            packages_to_add[package_name] = release_packages[package_name]

        return packages_to_add

    def _find_packages_that_will_be_subtracted(self, service, release_packages):
        """
        Find the packages in the current service but not in the release_package_names.
        This means if the user reverts to this release those packages will no longer
        exist.
        """
        release_package_names = Set(release_packages.keys())
        service_package_names = Set(service.packages.keys())

        packages_to_subtract = {}
        package_names_to_subtract = service_package_names - release_package_names

        for package_name in package_names_to_subtract:
            packages_to_subtract[package_name] = service.packages[package_name]

        return packages_to_subtract

    def _find_same_packages_with_diff_versions(self, service, release_packages):
        """
            The service represents the current state of the service on the test
            environment.

            Returns:
            {
                "Anweb": {
                    "package": "package": {
                        "github_info": "False",
                        "version": "1.2",
                        "remote": "",
                        "name": "smpackage",
                        "comparable_name": "smpackage"
                    },
                    "release_version": 1.1,
                    "service_version": 1.2
                },
                "create": {
                    "package": "package": {
                        "github_info": "False",
                        "version": "1.1.2",
                        "remote": "",
                        "name": "smpackage",
                        "comparable_name": "smpackage"
                    },
                    "release_version": 1.1.1,
                    "service_version": 1.1.2
                }
            }
        """
        changed_packages = {}

        for package_name, service_package in service.packages.iteritems():
            if package_name in release_packages:
                # Found a matching package. compare versions now.
                release_package = release_packages[package_name]

                if service_package.version != release_package.version:
                    changed_packages[service_package.comparable_name] = {
                        "package": service_package,
                        "release_version": release_package.version,
                        "service_version": service_package.version
                    }

        return changed_packages
