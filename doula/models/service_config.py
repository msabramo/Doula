from doula.util import comparable_name
import logging

log = logging.getLogger('doula')


class ServiceConfig(object):

    def __init__(self, **dict_data):
        """
        The dict_data contains all the service config's attributes:

        Ex.
        {
            "name": "billweb",
            "date": "2012-12-18T09:57:45-08:00",
            "sha": "fd743b3de157c38340b03989579bdc35daf5f77d",
            "message": "Update app.ini",
            "author": "metalculus84"
        }
        """
        self.__dict__.update(dict_data)
        self.comparable_name = comparable_name(self.name)
