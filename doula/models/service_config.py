from doula.util import comparable_name
from doula.helper_filters import formatted_github_day_and_time
import logging

log = logging.getLogger('doula')


class ServiceConfig(object):

    def __init__(self, **dict_data):
        """
        The dict_data contains all the service config's attributes:

        Ex.
        {
            "service": "billweb",
            "author": "chrisg@surveymonkey.com",
            "site": "mt1",
            "sha": "3a2df77fbcf804165c8e79e3d22d05fa3798e405",
            "date": "2012-03-06T15:17:44-08:00",
            "message": "Add ho-DOR"
        }
        """
        self.__dict__.update(dict_data)
        self.comparable_service = comparable_name(self.service)
        self.formatted_date = formatted_github_day_and_time(self.date)

    @staticmethod
    def build_instance_from_service(service):
        """
        Build a service config object from the attributes of a service object
        """
        config_dict = service.config.copy()
        config_dict["service"] = service.name
        config_dict["site"] = service.site_name

        if service.config.get('sha', False):
            config_dict['sha'] = service.config.get('sha')
        else:
            config_dict['sha'] = ''

        return ServiceConfig(**config_dict)
