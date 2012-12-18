from doula.cache_keys import key_val
import unittest


class CacheKeysTests(unittest.TestCase):

    def test_key(self):
        expected = "cheeseprism:package:test_package_name"
        result = key_val("cheeseprism_package", {"name": "test_package_name"})
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
