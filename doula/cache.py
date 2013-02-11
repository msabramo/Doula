from doula.config import Config
import logging
import redis
import traceback

log = logging.getLogger('doula')


class Redis(object):
    env = 'prod'
    redis = None
    # redis_store holds onto the permanent data for Doula
    redis_store = None
    host = '127.0.0.1'
    port = 6379

    @staticmethod
    def connect(db):
        try:
            redis_client = redis.Redis(host=Redis.host, port=int(Redis.port), db=db)
            redis_client.ping()
            log.debug("Connected to redis db: %s" % db)

            return redis_client
        except:
            log.error(traceback.format_exc())
            log.error("Unable to connect to redis server db: %s" % db)
            raise

    @staticmethod
    def get_instance(db=0):
        if Redis.env == 'dev':
            # for testing we use mock redis so that we don't need an option
            from doula.tests.mock_redis import MockRedis
            return MockRedis()

        if db == 0:
            if not Redis.redis:
                Redis.redis = Redis.connect(db)

            return Redis.redis
        elif db == 1:
            if not Redis.redis_store:
                Redis.redis_store = Redis.connect(db)

        return Redis.redis_store
