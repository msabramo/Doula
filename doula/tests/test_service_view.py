from doula.models.package import Package
from doula.models.release import Release
from doula.views.services_view import get_proper_package_name
from doula.views.services_view import diff_between_last_release_and_release_previous_to_that
import unittest


class PackageTests(unittest.TestCase):
    def setUp(self):
        pass

    def testDown(self):
        pass

    def test_diff_between_last_release_and_release_previous_to_that(self):
        p1 = Package('package name 1', '0.1')
        p2 = Package('package name 2', '0.2')
        p3 = Package('package name 3', '0.3')
        p4 = Package('package name 3', '0.5')

        d1 = '2012-11-13T18:24:21+00:00'
        r1 = Release('author', d1, 'commit message', 'master', [p1, p2, p4])
        r2 = Release('author', d1, 'commit message', 'master', [p1, p2, p3])
        releases = [r1, r2]
        diff = diff_between_last_release_and_release_previous_to_that(releases)

        self.assertEqual(diff['package name 3'], '0.5')

    def test_get_proper_package_name(self):
        name = '1.2.7b11-admintools-new'
        expected = '1.2.7b11-admintools_new'
        result = get_proper_package_name(name)

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
