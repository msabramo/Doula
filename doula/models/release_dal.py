from doula.cache import Redis
from doula.cache_keys import key_val
from doula.config import Config
from doula.github import get_appenv_releases, pull_appenv_service_names, pull_releases_for_service
from doula.models.release import Release
from doula.util import date_to_seconds_since_epoch, dumps
import json


class ReleaseDAL(object):
    """
    This module manages access to the manifest releases
    instead of the simple GitHub releases (releases pulled from commits)
    """

    def __init__(self):
        self.redis = Redis.get_instance(1)

    #####################
    # Release Query
    ####################

    def update_all_releases(self):
        """
        Update the releases for all the services
        """
        for service in pull_appenv_service_names():
            self.update_release_for_service(service)

    def update_release_for_service(self, service):
        """
        Update the release for a specific service, update all the release keys
        """
        print 'PULLING RELEASES FOR THE SERVICE: ' + service
        releases_and_branches = pull_releases_for_service(service)

        for site, releases in releases_and_branches.iteritems():
            for release in releases:
                release_as_json = dumps(release)

                subs = {
                    "site": site,
                    "service": service,
                    "date": release["date_as_epoch"],
                    "release_number": release['release_number']
                }

                if release["release_number"]:
                    release_by_number_key = key_val("release_by_number", subs)
                    self.redis.set(release_by_number_key, release_as_json)

                release_by_date_key = key_val("release_by_date", subs)
                self.redis.set(release_by_date_key, release_as_json)

                # Add the release to the list of releases
                releases_key = key_val("releases_for_service", subs)
                self.redis.zadd(releases_key, release_as_json, release["date_as_epoch"])

    #####################
    # Manifest Release
    ####################

    def next_release(self, site_name, service_name):
        """
        Increment the current release number and return that number
        """
        subs = {"site": site_name, "service": service_name}
        release_counter_key = key_val("release_counter", subs)

        return self.redis.incr(release_counter_key)

    def find_releases_for_service(self, site_name, service_name, limit=20):
        """
        Return the last X number of releases for this service. Always return
        the latest number of releases.

        We have to merge the existing GitHub releases with redis only releases
        while we transition to redis captured releases

        site_name    - the name of the site
        service_name - the name of the service
        limit        - max number releases to return
        """
        subs = {"site": site_name, "service": service_name}
        releases_key = key_val("releases_for_service", subs)

        releases = []
        releases_as_json = self.redis.zrevrange(releases_key, 0, limit - 1)

        for release_as_json in releases_as_json:
            release_as_dict = json.loads(release_as_json)
            releases.append(Release.build_from_dict(release_as_dict))

        return releases

    ######################################################################
    # These functions to be used when we have release numbers
    ######################################################################

    def find_manifest_by_release_number(self, site_name, service_name, release_number):
        """
        Manifest by release number
        """
        subs = {"site": site_name, "service": service_name, "release_number": release_number}
        release_key = key_val("release_by_number", subs)

        manifest_as_json = self.redis.get(release_key)

        if manifest_as_json:
            return json.loads(manifest_as_json)
        else:
            return {}

    def update_manifest(self, manifest, more_data):
        """
        This is an update to a manifest that was sent to production.

        manifest  - the original manifest dict
        more_data - new data sent after a production update as a dict
        """
        manifest.update(more_data)

        subs = {
            "site": manifest['site'],
            "service": manifest['service'],
            "release_number": manifest['release_number']
        }

        release_key = key_val("release_by_number", subs)

        self.redis.set(release_key, json.dumps(manifest))

