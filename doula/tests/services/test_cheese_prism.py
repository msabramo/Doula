import unittest
from doula.services.cheese_prism import CheesePrism
from doula.services.cheese_prism import PythonPackage


class CheesePrismTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all_packages(self):
        packages = CheesePrism.all_packages()

        self.assertTrue(len(packages))
        package = packages.pop()
        self.assertIsInstance(package, PythonPackage)

    def test_package_versions(self):
        packages = CheesePrism.all_packages()
        package = packages.pop()
        
        self.assertEqual(len(package.get_versions()), 1)
    def test_find_package_url_by_name(self):
        package = CheesePrism.find_package_by_name('jinja2')
        self.assertEqual(package.name, 'Jinja2')


if __name__ == '__main__':
    unittest.main()
