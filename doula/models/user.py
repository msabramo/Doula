from doula.cache import Cache
from pyramid.security import unauthenticated_userid
import json


class User(object):
    def __init__(self):
        pass

    @staticmethod
    def find(username):
        cache = Cache.cache()
        user_as_json = cache.get('doula:user:%s' % username)

        if not user_as_json:
            raise "Unable to find user"

        return json.loads(user_as_json)

    @staticmethod
    def save(user):
        json_user = json.dumps(user, sort_keys=True)

        cache = Cache.cache()
        cache.set('doula:user:%s' % user['username'], json_user)


def get_user(request):
    try:
        return User.find(unauthenticated_userid(request))
    except:
        return None
