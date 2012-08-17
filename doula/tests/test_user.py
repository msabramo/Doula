from doula.models.user import User
import unittest


class UserTests(unittest.TestCase):

    def test_save(self):
        user = {
            "username": 'alexv'
        }

        User.save(user)
        users = User.users()

        self.assertEqual(users.pop()['username'], 'alexv')

    def test_find(self):
        user = {
            "username": 'alexv'
        }

        User.save(user)
        self.assertNotEqual(User.find('alexv'), None)


if __name__ == '__main__':
    unittest.main()
