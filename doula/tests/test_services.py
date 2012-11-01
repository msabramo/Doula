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
        service = Service('test_app', 'site_name', 'test_node', 'http://test.com')
        service.remote = 'git@code.corp.surveymonkey.com:DevOps/WebApp1.git'
        service.last_tag_app = '1.0.3'
        service.current_branch_app = 'master'

        tags = [{'name': '1.0.3', 'message': 'message', 'date': 'date'}]
        service._add_tags_from_service_dict(tags)
        service._add_tags_from_service_dict(tags)

        compare_url = 'http://code.corp.surveymonkey.com'
        compare_url += '/DevOps/test_app/compare/1.0.3...master'

        self.assertEqual(service.get_compare_url(), compare_url)

    def test_freeze_requirements(self):
        service = Service('test_app', 'site_name', 'test_node', 'http://test.com')
        packages = []

        packages.append(Package('mnn', '1', 'origin'))
        packages.append(Package('ebd', '2', 'origin'))
        packages.append(Package('dbc', '2', 'origin'))
        packages.append(Package('abc', '1', 'origin'))
        service.packages = packages

        expected = "abc==1\n"
        expected += "dbc==2\n"
        expected += "ebd==2\n"
        expected += "mnn==1\n"

        self.assertEqual(service.freeze_requirements(), expected)

    def test_next_version_number(self):
        service = Service('test_app', 'site_name', 'test_node', 'http://test.com')
        tags = [{'name': '1.1.4', 'message': 'message', 'date': 'date'}]
        service._add_tags_from_service_dict(tags)

        expected = '0.1.5'

        self.assertEqual(service.next_version(), expected)

        service = Service('test_app', 'site_name', 'test_node', 'http://test.com')
        service.tags = [Tag('45.2.4 rc', 'date', 'message')]
        tags = [{'name': '45.2.4 rc', 'message': 'message', 'date': 'date'}]
        service._add_tags_from_service_dict(tags)

        expected = '45.2.5 rc'

        self.assertEqual(service.next_version(), expected)

if __name__ == '__main__':
    unittest.main()
