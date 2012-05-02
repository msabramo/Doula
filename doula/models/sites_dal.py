import json

from datetime import datetime
from doula.cache import Cache
from doula.util import dirify

class SiteDAL(object):
    def __init__(self):
        self.cache = Cache.cache()
    
    def save_application_as_deployed(self, app, tag):
        self._add_to_deploy_set(app, tag)
        self._set_app_tag_as_deployed(app, tag)
    
    def _add_to_deploy_set(self, app, tag):
        set_key = self._get_deployed_app_set_key(app)
        app_details = self._deployed_app_details(app, tag)
        self.cache.sadd(set_key, json.dumps(app_details))
    
    def _set_app_tag_as_deployed(self, app, tag):
        app_key = self._get_deployed_app_key(app)
        self.cache.set(app_key, tag.name)
    
    def is_deployed(self, app, tag):
        deployed_tag = self.cache.get(self._get_deployed_app_key(app))
        
        return deployed_tag == tag.name
    
    def _deployed_app_details(self, app, tag):
        """
        Returns a dictionary with the values
        { datetime: value, tag: value, comment: value }
        """
        return { 
            'tag'      : tag.name,
            'message'  : tag.message,
            'datetime' : self._timestamp()
        }
    
    def _timestamp(self):
        return datetime.now().isoformat()
    
    def _get_deployed_app_set_key(self, app):
        return '_'.join([app.site_name, app.name_url, 'deploy_tags'])
    
    def _get_deployed_app_key(self, app):
        return '_'.join([app.site_name, app.name_url, 'deployed'])
    
        