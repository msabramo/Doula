import redis
import logging

from mockredis import MockRedis

# Right now this is hard coded. Would be nice to have a util class that reads
# the ini file
HOST = 'localhost'
PORT = 6379

log = logging.getLogger('doula')


class Cache(object):
    env = 'prod'
    redis = None

    @staticmethod
    def clear_cache():
        # Clear all keys from the cache
        r = Cache.cache()
        r.flushdb()

    @staticmethod
    def cache():
        try:
            if not Cache.redis:
                Cache.redis = redis.StrictRedis(HOST, PORT, db=0)
                # Excercise redis to make sure we have a connection
                Cache.redis.set('__test__', '')

            return Cache.redis
        except:
            if Cache.env == 'prod':
                raise
            else:
                Cache.redis = MockRedis()
                return Cache.redis
