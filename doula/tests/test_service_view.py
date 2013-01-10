from doula.models.package import Package
from doula.models.release import Release
from doula.models.service import Service
from doula.views.services_view import build_release_manifest
from doula.views.services_view import get_proper_version_name
from mock import Mock
from pyramid import testing
import unittest


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def testDown(self):
        pass

    def test_build_release_manifest(self):
        service = Service(**{
            "site_name": "mt3",
            "name": "anweb",
            "packages": {},
            "tags": []
            })

        packages = {
            "anweb": "1.0.2",
            "smlib.web": "2.4"
        }

        expected = {
            "is_rollback": False,
            "service": service.name,
            "site": "mt3"
        }

        self.request.user = {'username': 'quez'}
        manifest = build_release_manifest(self.request, service, packages)

        self.assertEqual(manifest["is_rollback"], False)



if __name__ == '__main__':
    unittest.main()
