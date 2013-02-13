from doula.cache import Redis
from doula.cache_keys import key_val
from doula.config import Config
from doula.github import pull_config_services_with_branches
from doula.github import pull_service_configs
from doula.models.service_config import ServiceConfig
from doula.util import date_to_seconds_since_epoch
import json
import logging


log = logging.getLogger('doula')


class ServiceConfigDAL(object):

    def __init__(self):
        self.redis = Redis.get_instance(1)

    def update_service_config_data(self):
        """
        Update the service config repo data for all the configs
        """
        # Pull the service names
        config_services = pull_config_services_with_branches()

        # For every service name
        for config_service in config_services:
            self.update_service_config_data_for_service(config_service)

    def update_service_config_data_for_service(self, config_service):
        """
        Update the service config repo data for all the configs
        """
        for branch in config_service["branches"]:
            # Pull the latest date for each site and service service
            latest_service_config = self._get_latest_service_config_as_dict(
                branch["site"], config_service["service"])

            # Pull the data
            service_configs = pull_service_configs(branch["site"],
                                                   config_service["service"],
                                                   latest_service_config["sha"],
                                                   latest_service_config['date'])

            # Add all the newly pulled service configs to the redis sorted set
            key_params = {"site": branch["site"], "service": config_service["service"]}
            service_config_key = key_val("service_configs", key_params)

            for service_config in service_configs:
                # Save the service config with the sha as the key
                key_params["sha"] = service_config["sha"]
                service_config_sha_key = key_val("service_config_sha", key_params)
                self.redis.set(service_config_sha_key, json.dumps(service_config))

                # Add to the sorted set
                date_as_epoch = float(date_to_seconds_since_epoch(service_config["date"]))
                self.redis.zadd(service_config_key, json.dumps(service_config), date_as_epoch)

    def _get_latest_service_config_as_dict(self, site, service):
        """
        Find the last service config dict.
        If it doesn't exist return an emtpy service config dict.
        """
        service_config_key = key_val("service_configs", {"site": site, "service": service})
        # The latest is always at the zero index in redis
        latest_service_config = self.redis.zrevrange(service_config_key, 0, 0)

        if latest_service_config:
            return json.loads(latest_service_config[0])
        else:
            # Nothing exists. We create one and return that
            return {
                "site": site,
                "service": service,
                "date": "",
                "sha" : "",
                "author": "",
                "message": ""
            }

    def find_service_config_by_sha(self, site, service, sha):
        key_params = {
            "site": Config.get_safe_site(site),
            "service": service,
            "sha": sha
            }

        service_config_sha_key = key_val("service_config_sha", key_params)
        service_config_as_json = self.redis.get(service_config_sha_key)

        if service_config_as_json:
            service_config_as_dict = json.loads(service_config_as_json)
            return ServiceConfig(**service_config_as_dict)
        else:
            return False

    def latest_service_config(self, site, service):
        """
        Return the last service config commit.
        """
        service_config_as_dict = self._get_latest_service_config_as_dict(Config.get_safe_site(site), service)
        return ServiceConfig(**service_config_as_dict)


    def get_service_configs(self, site, service, limit=10):
        """
        Pull a config commits for this site and service
        """
        service_config_key = key_val("service_configs", {"site": site, "service": service})
        service_configs_as_json = self.redis.zrevrange(service_config_key, 0, limit - 1)
        service_configs = []

        for service_config_as_json in service_configs_as_json:
            service_config_as_dict = json.loads(service_config_as_json)

            service_configs.append(ServiceConfig(**service_config_as_dict))

        return service_configs
