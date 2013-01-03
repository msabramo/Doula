from doula.cache import Redis
from doula.cache_keys import key_val
from doula.config import Config
from doula.github import get_appenv_releases
from doula.models.release import Release
import json


class ReleaseDAL(object):
    """
    This module manages access to the manifest releases
    instead of the simple GitHub releases (releases pulled from commits)
    """

    def __init__(self):
        self.redis = Redis.get_instance(1)

    def next_release(self, site_name, service_name):
        """
        Increment the current release number and return that number
        """
        subs = {"site": site_name, "service": service_name}
        release_counter_key = key_val("release_counter", subs)

        return self.redis.incr(release_counter_key)

    def add_manifest(self, site_name, service_name, manifest):
        """
        Add a new manifest to this site and service
        """
        subs = {"site": site_name, "service": service_name, "release_number": manifest['release_number']}
        release_key = key_val("release_by_number", subs)

        self.redis.set(release_key, json.dumps(manifest))

        # alextodo. need to add manifests by date too. or maybe just use the dates only.

        releases_key = key_val("releases", subs)
        self.redis.zadd(releases_key, release_key, manifest['release_number'])

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
        releases_dict = {}
        redis_releases = self._find_redis_releases(site_name, service_name, limit)

        # The commit message is used to determine the uniqueness of the release
        # versus the github commit only release
        for release in redis_releases:
            releases_dict[release.commit_message] = release

        github_releases = self._find_github_releases(site_name, service_name)

        for release in github_releases:
            releases_dict[release.commit_message] = release

        releases = releases_dict.values()
        releases.sort(key=lambda x: x.date_in_seconds, reverse=True)

        return releases

    def _find_redis_releases(self, site_name, service_name, limit):
        """Releases stored in redis"""
        subs = {"site": site_name, "service": service_name}
        releases_key = key_val("releases", subs)

        releases = []
        release_count = int(self.redis.zcount(releases_key, '-inf', '+inf')) - 1
        start_count = (release_count - limit) if ((release_count - limit) > 0) else 0

        release_ids = self.redis.zrange(releases_key, start_count, release_count - 1)

        for release_id in release_ids:
            release_as_json = self.redis.get(release_id)
            release_as_dict = json.loads(release_as_json)

            releases.append(Release.build_from_dict(release_as_dict))

        return releases

    def _find_github_releases(self, site_name, service_name):
        site_name = Config.get_safe_site(site_name)
        commits = get_appenv_releases(service_name, site_name)
        releases = []

        for cmt in commits:
            release = Release.build_release_from_repo(site_name, cmt)
            releases.append(release)

        return releases
