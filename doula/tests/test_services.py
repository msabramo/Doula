from doula.models.package import Package
from doula.models.service import Service
from doula.models.tag import Tag
import unittest


class ServiceTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_compare_url(self):
        tags = [{'name': '1.0.3', 'message': 'message', 'date': 'date'}]

        service = Service(
            name='test_app',
            site_name='site_name',
            config={'date': '2011-07-18 15:08:55 -0700'},
            packages={},
            tags=tags)
        service.remote = 'git@code.corp.surveymonkey.com:DevOps/WebApp1.git'
        service.last_tag_app = '1.0.3'
        service.current_branch_app = 'master'

        compare_url = 'http://code.corp.surveymonkey.com'
        compare_url += '/DevOps/test_app/compare/1.0.3...master'

        self.assertEqual(service.get_compare_url(), compare_url)

    def test_freeze_requirements(self):
        service = Service(
            name='test_app',
            site_name='site_name',
            config={'date': '2011-07-18 15:08:55 -0700'},
            packages={
                'mnn': {'name': 'mnn', 'version': '1'},
                'ebd': {'name': 'ebd', 'version': '2'},
                'dbc': {'name': 'dbc', 'version': '2'},
                'abc': {'name': 'abc', 'version': '1'}},
            tags=[])

        expected = "abc==1\n"
        expected += "dbc==2\n"
        expected += "ebd==2\n"
        expected += "mnn==1\n"

        self.assertEqual(service.freeze_requirements(), expected)

    def test_next_version_number(self):
        tags = [{'name': '0.1.4', 'message': 'message', 'date': 'date'}]
        service = Service(
            name='test_app',
            site_name='site_name',
            config={'date': '2011-07-18 15:08:55 -0700'},
            packages={},
            tags=tags)

        expected = '0.1.5'

        self.assertEqual(service.next_version(), expected)

        tags = [{'name': '45.2.4 rc', 'message': 'message', 'date': 'date'}]
        service = Service(
            name='test_app',
            site_name='site_name',
            config={'date': '2011-07-18 15:08:55 -0700'},
            packages={},
            tags=tags)

        expected = '45.2.5 rc'

        self.assertEqual(service.next_version(), expected)

if __name__ == '__main__':
    unittest.main()
