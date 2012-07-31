import json
from pyramid.security import unauthenticated_userid
from doula.cache import Cache


def get_user(request):
    cache = Cache.cache()
    user_id = unauthenticated_userid(request)
    if user_id is not None:
        # this should return None if the user doesn't exist
        # in the database
        user_json = cache.get('doula:user:%s' % user_id)
        return json.loads(user_json)
    return None
