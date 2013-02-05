from doula.models.service_config_dal import ServiceConfigDAL
from doula.util import dirify
from doula.util import pull_url
from doula.util import dumps
import pdb
import logging
import simplejson as json
import sys

log = logging.getLogger('doula')


class Node(object):
    """
    Represents a node on a bambino.
    """
    def __init__(self, name, site_name, url, ip,
                 config={}, changed_files=[], supervisor_service_names=[]):
        self.name = name
        self.name_url = dirify(name)
        self.site_name = site_name
        self.url = url
        self.ip = ip
        self.errors = []
        self.config = config
        self.changed_files = changed_files
        self.supervisor_service_names = supervisor_service_names
        self._update_node_config()

    def _update_node_config(self):
        """
        Update the is_up_to_date key of the config attribute.

        The bambino will return the current sha and any files that have been changed.
        Here we figure out if the node is actually up to date and save it to the
        'is_up_to_date' key. We also update the config dict with the 'latest_sha'
        for the config for that service.
        """
        if not self.config:
            return ''

        sc_dal = ServiceConfigDAL()
        latest_service_config = sc_dal.latest_service_config(self.site_name, self.config.get('repo_name', self.name))
        self.config['latest_sha'] = latest_service_config.sha

        if self.config.get('sha', '') != self.config.get('latest_sha', '') or len(self.config.get('changed_files', [])) > 0:
            self.config['is_up_to_date'] = False
        else:
            self.config['is_up_to_date'] = True

    def pull_services_as_dicts(self):
        """
        Pull the services from the bambino then return result as dicts
        """
        try:
            services_as_dicts = {}
            # The bambino's are bit slow now so we'll give them extra
            # time to gather the data
            print 'PULLING SERVICES FOR: ' + self.url + '/services'
            services_as_json = pull_url(self.url + '/services', 60)

            if services_as_json:
                services_as_dicts = json.loads(services_as_json)

            return services_as_dicts
        except:
            from doula.models.doula_dal import DoulaDAL

            # If we're not able to contact a bambino we unregister
            # the Bambino node.
            dd = DoulaDAL()
            dd.unregister_node({'site': self.site_name, 'name': self.name})

            vals = (self.url + '/services', sys.exc_info())
            msg = 'Unable to contact Bambino at %s because of error %s' % vals
            print msg
            log.error(msg)

            # Return an empty list of services
            return {'services': []}


