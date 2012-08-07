import logging
import redis

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
                Cache.redis = redis.Redis()
                # Excercise redis to make sure we have a connection
                Cache.redis.set('__test__', '')

            return Cache.redis
        except:
            if Cache.env == 'prod':
                raise
            else:
                from mockredis import MockRedis
                Cache.redis = MockRedis()
                return Cache.redis
