"""
Implements the auditing piece of Doula.
"""

import json

from datetime import datetime
from doula.cache import Cache
from doula.util import dirify

class Audit(object):
    def __init__(self):
        self.cache = Cache.cache()
    
    def log_action(self, site_name, app_name, action, user):
        timestamp = self._timestamp()
        key = '_'.join([site_name, app_name, 'log', timestamp])
        set_key = '_'.join([site_name, app_name, 'logs'])
        
        self.cache.sadd(set_key, key)
        self.cache.set(key, json.dumps(self._action_details(action, user, timestamp)))
    
    def _action_details(self, action, user):
        
    
    def _timestamp(self):
        return datetime.now().isoformat()
    
