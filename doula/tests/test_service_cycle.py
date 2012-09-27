from doula.models.service import Service
import unittest
import xmlrpclib


class ServiceCycleTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cycle_service(self):
        ip = '192.168.4.64'
        Service.cycle(xmlrpclib.ServerProxy('http://' + ip + ':9001'), 'anweb')
