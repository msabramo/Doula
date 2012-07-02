from doula.util import pull_url
import logging
import re

log = logging.getLogger('doula')


class PythonPackage(object):
    def __init__(self, url):
        self.url = url
        self.name = url.split('/').pop()
        self.versions = []

    def get_versions(self):
        """
        Read the CheesePrism index for all available versions
        """
        if len(self.versions) == 0:
            self.versions = CheesePrism.package_versions(self.url)

        return self.versions


class CheesePrism(object):
    """
    Provides an interface to CheesePrism, Survey Monkey's PyPi
    """
    url = 'http://yorick:9003/'

    @staticmethod
    def find_package_by_name(name):
        """
        Package URL's are case sensitive so we need to find the exact URL
        """
        packages = CheesePrism.all_packages()
        comparable_name = CheesePrism.clean_for_compare(name)

        for p in packages:
            if comparable_name == CheesePrism.clean_for_compare(p.name):
                return p
        
        return False

    @staticmethod
    def clean_for_compare(name):
        name = name.lower()
        name = name.replace('-', '')
        name = name.replace('_', '')

        return name

    @staticmethod
    def all_packages():
        """
        Return all packages
        """
        text = pull_url(CheesePrism.url + '/index/')
        matches = re.findall(r'a.+href="(.+)"', text, re.M)

        return [PythonPackage(m) for m in matches]
    
    @staticmethod
    def package_versions(url):
        text = pull_url(url)
        matches = re.findall(r'a.+href="(.+)"', text, re.M)

        versions = []

        for m in matches:
            match = re.search(r'-([.\d]+).tar.gz', m)

            if match:
                versions.append(match.group(1))

        return versions
