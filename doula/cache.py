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
    # redis_store holds onto the permanent data for Doula
    redis_store = None

    @staticmethod
    def clear_cache():
        # Clear all keys from the cache
        r = Cache.cache()
        r.flushdb()

    @staticmethod
    def cache(db=0):
        try:
            if db == 0:
                if not Cache.redis:
                    Cache.redis = redis.StrictRedis(HOST, PORT, db)
                    # Excercise redis to make sure we have a connection
                    Cache.redis.ping()

                return Cache.redis
            elif db == 1:
                if not Cache.redis_store:
                    Cache.redis_store = redis.StrictRedis(HOST, PORT, db)
                    # Excercise redis to make sure we have a connection
                    Cache.redis_store.ping()

                return Cache.redis_store
        except:
            if Cache.env == 'prod':
                raise
            else:
                from mockredis import MockRedis
                Cache.redis = MockRedis()
                return Cache.redis
