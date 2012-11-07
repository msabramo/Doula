from doula.cache import Redis
from doula.config import Config
from doula.util import *
import simplejson as json
import logging

log = logging.getLogger('doula')


class PythonPackage(object):
    def __init__(self, name, versions=[]):
        self.name = name
        self.clean_name = comparable_name(self.name)
        self.versions = versions
        self.versions.sort()

    def get_last_version(self):
        """
        Get the latest version in the versions list
        """
        index = len(self.versions) - 1

        if index < 0:
            index = 0

        if len(self.versions) > 0:
            return self.versions[index]
        else:
            return ""


class CheesePrism(object):
    """
    Provides an interface to CheesePrism, Survey Monkey's PyPi
    """
    @staticmethod
    def find_package_by_name(name):
        """
        Package URL's are case sensitive so we need to find the exact URL

        Return the python package object.
        """
        redis = Redis.get_instance()
        package_as_json = redis.get('cheeseprism:package:' + comparable_name(name))

        if package_as_json:
            package_as_dict = json.loads(package_as_json)

            return PythonPackage(package_as_dict['name'], package_as_dict['versions'])
        else:
            log.info('Returning an empty package %s' % name)
            return PythonPackage(name, [])

    @staticmethod
    def all_packages():
        """
        Return all packages from our redis
        """
        redis = Redis.get_instance()
        all_packages = []
        packages_as_json = redis.get('cheeseprism:packages')

        if packages_as_json:
            json_packages = json.loads(packages_as_json)

            for jpckg in json_packages:
                pckg = PythonPackage(jpckg['name'], jpckg['versions'])
                all_packages.append(pckg)

        return all_packages

    @staticmethod
    def pull_all_packages():
        """
        Return all the packages and their versions from Cheese Prism site
        """
        packages = {}

        url = Config.get('doula.cheeseprism_url')
        text = pull_url(url + '/index/index.json')
        packages_on_cheeseprism = json.loads(text)

        for sha1 in packages_on_cheeseprism:
            pckg = packages_on_cheeseprism[sha1]

            if pckg['name'] in packages:
                packages[pckg['name']]['versions'].append(pckg['version'])
            else:
                packages[pckg['name']] = {
                    'name': pckg['name'],
                    'versions': [pckg['version']]
                }

        all_packages = []

        for name, pckg in packages.iteritems():
            all_packages.append(PythonPackage(name, pckg['versions']))

        return all_packages

    @staticmethod
    def other_packages(packages):
        """
        Get all the packages on cheese prism, but not on this service
        """
        all_packages = CheesePrism.all_packages()

        for package_name, pckg in packages.iteritems():
            found_pckg = False

            for all_pckg in all_packages:
                if all_pckg.name == pckg.name:
                    found_pckg = all_pckg
                    break

            if found_pckg:
                all_packages.remove(found_pckg)

            found_pckg = False

        return all_packages
