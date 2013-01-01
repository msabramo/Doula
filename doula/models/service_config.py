from doula.util import comparable_name
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
