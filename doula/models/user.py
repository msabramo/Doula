from doula.cache import Cache
from pyramid.security import unauthenticated_userid
import json


class User(object):
    """
    The user represents a user that has logged into Doula via Github

    Example user object:
    user = {
        'username': '',
        'oauth_token': '',
        'avatar_url': '',
        'email': '',
        'settings': {
            'notify_me': 'failed',
            'subscribed_to': ['my_jobs']
        }
    }
    """
    @staticmethod
    def find(username):
        """
        Find the user in the redis db by username
        Users are stored in redis with the key:
            'doula:user:[username]'
        """
        cache = Cache.cache(1)
        user_as_json = cache.get('doula:user:%s' % username)

        if user_as_json:
            return json.loads(user_as_json)
        else:
            return None

    @staticmethod
    def save(user):
        """
        Save the user object to redis and make sure the user
        has all right key values
        """
        if not 'email' in user:
            user['email'] = 'no-reply@surveymonkey.com'

        # Ensure the keys settings exist
        if not 'settings' in user:
            user['settings'] = {}

        if not 'notify_me' in user['settings']:
            user['settings']['notify_me'] = 'failed'

        if not 'subscribed_to' in user['settings']:
            user['settings']['subscribed_to'] = ['my_jobs']

        # Save whether or not this user is an admin
        from doula.github import get_doula_admins

        if user['username'] in get_doula_admins():
            user['admin'] = True
        else:
            user['admin'] = False

        json_user = json.dumps(user, sort_keys=True)

        cache = Cache.cache(1)

        cache.set('doula:user:%s' % user['username'], json_user)
        cache.sadd('doula:users', user['username'])

    @staticmethod
    def users():
        """
        Return all the users
        """
        cache = Cache.cache(1)
        users = []

        for username in cache.smembers('doula:users'):
            user = User.find(username)

            if user:
                users.append(user)

        return users

    @staticmethod
    def find_user_for_request(request):
        """
        Find the user that will be passed into the request object
        of every view callable
        """
        try:
            return User.find(unauthenticated_userid(request))
        except:
            return None
