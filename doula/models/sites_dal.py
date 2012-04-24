from datetime import datetime
from doula.cache import Cache
from doula.util import dirify

class SiteDAL(object):
    def __init__(self):
        self.cache = Cache.cache()
    
    def save_application_as_deployed(self, app):
        self._add_to_deploy_set(app)
        key = self._get_deployed_app_key(app)
        self.cache.set(key, self._deployed_app_details)
    
    def _add_to_deploy_set(self, app):
        set_key = self._get_deployed_app_set_key(app)
        self.cache.sadd(set_key, app.last_tag_app)
    
    def is_deployed(self, app):
        set_key = self._get_deployed_app_set_key(app)
        return self.cache.sismember(set_key, app.last_tag_app)
    
    def _deployed_app_details(self, app):
        """
        Returns a dictionary with the values
        { datetime: value, tag: value, comment: value }
        """
        return { 
            'tag'      : app.last_tag_app, 
            'message'  : app.last_tag_message,
            'datetime' : SiteDAL._timestamp()
        }
    
    def _timestamp(self):
        return datetime.now().isoformat()
    
    def _get_deployed_app_set_key(self, app):
        return '_'.join([app.site_name, app.name_url, 'deploy_tags'])
    
    def _get_deployed_app_key(self, app):
        return '_'.join([app.site_name, app.name_url, 'deploy', dirify(app.last_tag_app)])
    
        