from doula.cache import Cache
from doula.util import *

import json
import logging
import re

log = logging.getLogger('doula')
cache = Cache.cache()


class PythonPackage(object):
    def __init__(self, url, versions=[]):
        self.url = url
        self.name = url.split('/').pop()
        self.clean_name = comparable_name(self.name)
        self.versions = versions

    def pull_versions(self):
        """
        Pull the versions for this package off the CheesePrism site
        """
        if len(self.versions) == 0:
            self.versions = CheesePrism.pull_package_versions(self.url)

        return self.versions

    def get_versions(self):
        """
        Read the CheesePrism index for all available versions
        """
        this_pckg = json.loads(cache.get('cheeseprism_pckg_' + self.clean_name))
        return this_pckg['versions']


class CheesePrism(object):
    """
    Provides an interface to CheesePrism, Survey Monkey's PyPi
    """

    @staticmethod
    def find_package_by_name(name):
        """
        Package URL's are case sensitive so we need to find the exact URL
        """
        # redis key == cheeseprism_pckg_(cleaned name) = all versions of a pckg
        # also cull together the data for a package, commits, log history
        # all that ish.
        packages = CheesePrism.all_packages()
        name = comparable_name(name)

        for p in packages:
            if name == comparable_name(p.name):
                return p

        return False

    @staticmethod
    def all_packages():
        """
        Return all packages from our data store
        """
        all_packages = []
        packages_as_json = cache.get('cheeseprism_packages')

        if packages_as_json:
            json_packages = json.loads(packages_as_json)

            for jpckg in json_packages:
                pckg = PythonPackage(jpckg['url'], jpckg['versions'])
                all_packages.append(pckg)

        return all_packages

    @staticmethod
    def pull_all_packages():
        """
        Return all the packages from the Cheese Prism site.
        """
        text = pull_url(Config.get('doula.cheeseprism_url') + 'index/')
        matches = re.findall(r'a.+href="(.+)"', text, re.M)

        return [PythonPackage(m) for m in matches]

    @staticmethod
    def pull_package_versions(url):
        text = pull_url(url)
        matches = re.findall(r'a.+href="(.+)"', text, re.M)

        versions = []

        for m in matches:
            match = re.search(r'-([.\d]+).tar.gz', m)

            if match:
                versions.append(match.group(1))

        return versions

    @staticmethod
    def other_packages(packages):
        """
        Get all the packages on cheese prism, but not on this service
        """
        all_packages = CheesePrism.all_packages()

        for pckg in packages:
            found_pckg = False

            for all_pckg in all_packages:
                if all_pckg.name == pckg.name:
                    found_pckg = all_pckg
                    break

            if found_pckg:
                all_packages.remove(found_pckg)

            found_pckg = False

        return all_packages
