from doula.cache import Redis
from doula.cache_keys import key_val
from doula.github import pull_services_for_config_names
from doula.github import pull_service_configs
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
        config_names = pull_services_for_config_names()

        # alextodo incorporate the branches too. we will need those.
        # so it'll be config for every branch.

        # For every service name
        for config_name in config_names:
            # pull the latest date for each service
            last_service_config = self._get_last_service_config(config_name)

            # pull the data
            service_configs = pull_service_configs(config_name, last_service_config['date'])

            # add all the newly pulled service configs to the redis sorted set
            service_config_key = key_val("service_configs", {"name": config_name})

            for service_config in service_configs:
                date_as_epoch = float(date_to_seconds_since_epoch(service_config["date"]))
                self.redis.zadd(service_config_key, json.dumps(service_config), date_as_epoch)


    def _get_last_service_config(self, config_name):
        """
        Find the last service config dict.
        If it doesn't exist return an emtpy service config dict.
        """
        service_config_key = key_val("service_configs", {"name": config_name})

        configs_count = int(self.redis.zcount(service_config_key, '-inf', '+inf')) - 1
        configs_count = 0 if (configs_count == -1) else configs_count
        last_service_config = self.redis.zrange(service_config_key, configs_count, configs_count)

        if last_service_config:
            return json.loads(last_service_config[0])
        else:
            # Nothing exists. We create one and return that
            return {
                "name": config_name,
                "date": "",
                "sha" : "",
                "author": "",
                "message": ""
            }


    def get_service_config(self):
        """
        Pull a service config
        """
        pass
