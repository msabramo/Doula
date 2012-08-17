from doula.cache import Cache
from doula.models.user import User
from doula.notifications import build_email_list
import unittest


class NotificationsTests(unittest.TestCase):

    def setUp(self):
        cache = Cache.cache()
        cache.flushdb()

    def test_build_email_list_to_original_user(self):
        user = {
            "username": 'testuser',
            'email': 'test@surveymonkey.com',
            'settings': {
                'notify_me': 'always',
                'subscribed_to': ['my_jobs']
            }
        }

        User.save(user)

        job_dict = {
            'id': 1,
            'user_id': 'testuser',
            'status': 'complete',
            'job_type': 'push_to_cheeseprism',
            'site': 'mt1',
            'service': 'billweb',
            'time_started': 0,
            'exc': ''
        }

        email_list = build_email_list(job_dict)

        self.assertEqual(len(email_list), 1)
        self.assertEqual(email_list[0], 'test@surveymonkey.com')

    def test_build_email_list_to_subscribed_user(self):
        user = {
            "username": 'testuser2',
            'email': 'testuser2@surveymonkey.com',
            'settings': {
                'notify_me': 'always',
                'subscribed_to': ['my_jobs', 'mt1']
            }
        }

        User.save(user)

        # try with a job where the user is subscribed
        job_dict = {
            'id': 1,
            'user_id': 'testuser',
            'status': 'complete',
            'job_type': 'push_to_cheeseprism',
            'site': 'mt1',
            'service': 'billweb',
            'time_started': 0,
            'exc': ''
        }

        email_list = build_email_list(job_dict)

        self.assertEqual(len(email_list), 1)
        self.assertEqual(email_list[0], 'testuser2@surveymonkey.com')

        # try with a job where the user is NOT subscribed
        job_dict = {
            'id': 1,
            'user_id': 'testuser',
            'status': 'complete',
            'job_type': 'push_to_cheeseprism',
            'site': 'mt2',
            'service': 'billweb',
            'time_started': 0,
            'exc': ''
        }

        email_list = build_email_list(job_dict)

        self.assertEqual(len(email_list), 0)


if __name__ == '__main__':
    unittest.main()
