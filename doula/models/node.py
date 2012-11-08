from doula.util import pull_url
from doula.util import dirify
import logging
import simplejson as json

log = logging.getLogger('doula')


class Node(object):
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

    def pull_services_as_dicts(self):
        """
        Pull the services from the bambino then return result as dicts
        """
        try:
            services_as_dicts = {}
            # The bambino's are bit slow now so we'll give them extra
            # time to gather the data
            services_as_json = pull_url(self.url + '/services', 7)

            if services_as_json:
                services_as_dicts = json.loads(services_as_json)

            return services_as_dicts
        except Exception as e:
            from doula.models.doula_dal import DoulaDAL

            # If we're not able to contact a bambino we unregister
            # the Bambino node.
            dd = DoulaDAL()
            dd.unregister_node({'site': self.site_name, 'name': self.name})

            vals = (self.url + '/services', e.message)
            msg = 'Unable to contact Bambino at %s because of error %s' % vals
            print msg
            log.error(msg)

            # Return an empty list of services
            return {'services': []}


