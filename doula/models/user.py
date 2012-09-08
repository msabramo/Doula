from doula.cache import Cache
from pyramid.security import unauthenticated_userid
import json


class User(object):
    """
    Example user object:
    {
        'username': '',
        'oauth_token': '',
        'avatar_url': '',
        'email': '',
        'settings': {
            'notify_me': 'always',
            'subscribed_to': ['my_jobs']
        }
    }
    """

    @staticmethod
    def find(username):
        cache = Cache.cache(1)
        user_as_json = cache.get('doula:user:%s' % username)

        if not user_as_json:
            return None
        else:
            return json.loads(user_as_json)

    @staticmethod
    def save(user):
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


def get_user(request):
    try:
        return User.find(unauthenticated_userid(request))
    except:
        return None
