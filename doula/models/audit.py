"""
Implements the auditing piece of Doula.
"""

import json

from datetime import datetime
from doula.cache import Cache

class Audit(object):
    def __init__(self):
        self.cache = Cache.cache()

    def log_action(self, site_name, app_name, action, user):
        timestamp = self._timestamp()
        key = '_'.join([site_name, app_name, 'log', timestamp])
        set_key = self._get_set_key(site_name, app_name)

        self.cache.sadd(set_key, key)
        self.cache.set(key, json.dumps(self._action_hash(action, user, timestamp)))

    def _action_hash(self, action, user, timestamp):
        return {
            'action': action,
            'user': user,
            'time': timestamp
        }

    def _timestamp(self):
        return datetime.now().isoformat()

    def get_app_logs(self, site_name, app_name):
        logs = []
        set_key = self._get_set_key(site_name, app_name)
        set_of_logs = self.cache.smembers(set_key)

        for log_key in set_of_logs:
            log_as_json = self.cache.get(log_key)
            logs.append(json.loads(log_as_json))

        return logs

    def _get_set_key(self, site_name, app_name):
        return '_'.join([site_name, app_name, 'logs'])

