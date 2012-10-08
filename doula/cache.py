from doula.config import Config
import logging
import redis
import traceback

log = logging.getLogger('doula')


class Cache(object):
    env = 'prod'
    redis = None
    # redis_store holds onto the permanent data for Doula
    redis_store = None

    @staticmethod
    def connect(host, port, db):
        host = host or 'localhost'
        port = port or 6379

        try:
            redis_client = redis.Redis(host=host, port=int(port), db=db)
            redis_client.ping()
            log.debug("Connected to redis db: %s" % db)

            return redis_client
        except:
            log.error(traceback.format_exc())
            log.error("Unable to connect to redis server db: %s" % db)
            raise

    @staticmethod
    def cache(db=0):
        try:
            if db == 0:
                if not Cache.redis:
                    Cache.redis = Cache.connect(Config.get('redis.host'), Config.get('redis.port'), db)

                return Cache.redis
            elif db == 1:
                if not Cache.redis_store:
                    Cache.redis_store = Cache.connect(Config.get('redis.host'), Config.get('redis.port'), db)

                return Cache.redis_store
        except:
            if Cache.env == 'prod':
                raise
            else:
                # for testing we use mock redis so that we don't need an option
                from mockredis import MockRedis
                return MockRedis()
