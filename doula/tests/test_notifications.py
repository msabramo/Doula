from doula.cache import Redis
from doula.models.user import User
from doula.notifications import build_email_list
import unittest


class NotificationsTests(unittest.TestCase):

    def setUp(self):
        redis = Redis.get_instance()
        redis.flushdb()

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
            'job_type': 'build_new_package',
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
            'job_type': 'build_new_package',
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
            'job_type': 'build_new_package',
            'site': 'mt2',
            'service': 'billweb',
            'time_started': 0,
            'exc': ''
        }

        email_list = build_email_list(job_dict)

        self.assertEqual(len(email_list), 0)

        job_dict = {
            'status': 'complete',
            'user_id': 'testuser2',
            'exc': '',
            'service': 'billweb',
            'job_type': 'cycle_service',
            'site': 'alexs-macbook-pro-4.local',
            'time_started': 1345244421.622244,
            'nodes': ['192.168.104.109'],
            'id': '525ef351e8bf11e1aa30b8f6b1191577',
            'supervisor_service_names': []
        }

        email_list = build_email_list(job_dict)

        self.assertEqual(len(email_list), 1)


if __name__ == '__main__':
    unittest.main()
