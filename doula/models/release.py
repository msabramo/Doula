from doula.config import Config
from doula.github import get_appenv_releases
from doula.models.package import Package
from doula.models.service_config import ServiceConfig
from doula.models.service_config_dal import ServiceConfigDAL
from doula.util import date_to_seconds_since_epoch, find_package_and_version_in_pip_freeze_text
from sets import Set


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

        self.release_number = 0
        self.sha1 = ""
        self.sha1_etc = ""
        self.site = branch # the branch and site are equal
        self.service = ""

        self.is_rollback = False
        self.production = False
        self.rolled_back_from_release_number = 0

    ###################
    # Factory Methods
    ###################

    @staticmethod
    def build_empty_release(site):
        """
        Build an empty release object
        """
        return Release('', '', '', site, [])

    @staticmethod
    def build_release_on_the_fly(dict_data, service):
        """
        Build a release type object on the fly from packages and manifest
        dict_data = {
            "sha": "",
            "packages": {
                "package name": versin number,
            }
        }
        """
        release = Release('author', dict_data['date'], '', service.site_name, [])
        release.sha1_etc = dict_data['sha']
        release.site = service.site_name
        release.service = service.name
        release.date_in_seconds = date_to_seconds_since_epoch(dict_data['date'])
        release.packages = []

        for name, version in dict_data['packages'].iteritems():
            release.packages.append(Package(name, version, ''))

        return release

    @staticmethod
    def build_from_dict(dict_data):
        release = Release('author', '2012-01-01T00:00:00', 'commit_message', 'branch', [])
        release.__dict__.update(dict_data)
        # Site and branch are equal
        release.branch = release.site
        release.date_in_seconds = date_to_seconds_since_epoch(dict_data['date'])
        release.packages = Release.build_packages_from_commit_message(dict_data['commit_message'])

        return release

    @staticmethod
    def build_release_from_repo(branch, commit):
        """
        Build a release object from an app env repo with the format
        and a commit that is a single commit of this repo object
            {
            'commits': [
                {
                    'author': 'test@surveymonkey.com',)
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
        packages = Release.build_packages_from_commit_message(commit['message'])
        return Release(commit["author"], commit['date'], commit['message'], branch, packages)

    @staticmethod
    def build_packages_from_commit_message(text):
        """Build packages from text"""
        packages = []

        for line in text.splitlines():
            package_and_version = find_package_and_version_in_pip_freeze_text(line)

            if len(package_and_version.keys()) > 0:
                for name, version in package_and_version.iteritems():
                    packages.append(Package(name, version))

        return packages

    @staticmethod
    def get_releases(branch, service_name):
        commits = get_appenv_releases(service_name, Config.get_safe_site(branch))
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
            "current_service_config": ServiceConfig(),
            "release_service_config": ServiceConfig(),
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
            'current_service_config': self._find_service_service_config(service),
            'release_service_config': self._find_release_service_config(service),
            'changed_packages'      : self._find_same_packages_with_diff_versions(service, release_packages),
            'packages_to_add'       : self._find_packages_to_add(service, release_packages),
            'packages_to_subtract'  : self._find_packages_that_will_be_subtracted(service, release_packages)
        }

    def _build_release_packages_dict(self):
        """Build a dict from the release packages list"""
        release_packages = {}

        # release is a list. unlike the service packages. make same in future.
        for package in self.packages:
            release_packages[package.comparable_name] = package

        return release_packages

    def _find_service_service_config(self, service):
        """
        Find or build the service config object for this service
        """
        return ServiceConfig.build_instance_from_service(service)

    def _find_release_service_config(self, service):
        """
        Find or build the service config object for this release

        If there is no existing sha1 for this release, we pull the
        latest sha1 from the service_config_dal
        """
        sc_dal = ServiceConfigDAL()
        service_config = sc_dal.find_service_config_by_sha(service.site_name, service.name, self.sha1_etc)

        if service_config:
            return service_config
        else:
            return sc_dal.latest_service_config(service.site_name, service.name)

    def _find_packages_to_add(self, service, release_packages):
        """
        Find the packages in the release but not in the current service.
        The packages on this release need to be added to the service if
        it's released to the MT environment
        """
        release_package_names = Set(release_packages.keys())
        service_package_names = Set(service.packages.keys())

        packages_to_add = {}
        package_names_to_add = release_package_names - service_package_names

        for package_name in package_names_to_add:
            packages_to_add[package_name] = release_packages[package_name]

        return packages_to_add

    def _find_packages_that_will_be_subtracted(self, service, release_packages):
        """
        Find the packages in the current service but not in the release.
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
