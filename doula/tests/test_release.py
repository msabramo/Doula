import unittest
from doula.models.release import Release


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.repo = {
            'commits': [
                {
                    'date': '2012-08-27T22: 59: 17+00: 00',
                    'message': """Pushedpanel==1.0.24
                        ##################
                        pipfreeze:
                        ##################
                        Beaker==1.5.4
                        Chameleon==1.3.0-rc1
                        Elixir==0.7.1
                        """
                }
            ],
            'name': 'panel'
        }

    def testDown(self):
        pass

    def test_build_release_from_repo(self):
        release = Release.build_release_from_repo(
                                                self.repo,
                                                self.repo['commits'][0])

        self.assertEqual(release.name, 'panel')
        self.assertEqual(len(release.packages), 3)


if __name__ == '__main__':
    unittest.main()
