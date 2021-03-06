import random

from collections import defaultdict
from mockredis.lock import MockRedisLock


class MockRedis(object):
    """
    Imitate a Redis object so unit tests can run
    without needing a real Redis server.
    """

    env = 'dev'

    # The 'Redis' store
    redis = defaultdict(dict)
    # The pipeline
    pipe = None

    def __init__(self):
        """Initialize the object."""
        pass

    def type(self, key):
        _type = type(self.redis[key])
        if _type == dict:
            return 'hash'
        elif _type == str:
            return 'string'
        elif _type == set:
            return 'set'
        elif _type == list:
            return 'list'
        return None

    def get(self, key):  # pylint: disable=R0201
        """Emulate get."""

        # Override the default dict
        result = '' if key not in self.redis else self.redis[key]
        return result

    def set(self, key, value):
        """Emulate set command"""
        self.redis[key] = value

    def keys(self, pattern):  # pylint: disable=R0201
        """Emulate keys."""
        import re

        # Make a regex out of pattern. The only special matching character we look for is '*'
        regex = '^' + pattern.replace('*', '.*') + '$'

        # Find every key that matches the pattern
        result = [key for key in self.redis.keys() if re.match(regex, key)]

        return result

    def lock(self, key, timeout=0, sleep=0):  # pylint: disable=W0613
        """Emulate lock."""

        return MockRedisLock(self, key)

    def pipeline(self):
        """Emulate a redis-python pipeline."""
        # Prevent a circular import
        from mockredis.pipeline import MockRedisPipeline

        if self.pipe == None:
            self.pipe = MockRedisPipeline(self.redis)
        return self.pipe

    def delete(self, key):  # pylint: disable=R0201
        """Emulate delete."""

        if key in self.redis:
            del self.redis[key]

    def exists(self, key):  # pylint: disable=R0201
        """Emulate get."""

        return key in self.redis

    def execute(self):
        """Emulate the execute method. All piped commands are executed immediately
        in this mock, so this is a no-op."""

        pass

    def hget(self, hashkey, attribute):  # pylint: disable=R0201
        """Emulate hget."""
        # Return '' if the attribute does not exist
        result = self.redis[hashkey][attribute] if attribute in self.redis[hashkey] \
                 else ''
        return result

    def hgetall(self, hashkey):  # pylint: disable=R0201
        """Emulate hgetall."""
        return self.redis[hashkey]

    def hlen(self, hashkey):  # pylint: disable=R0201
        """Emulate hlen."""

        return len(self.redis[hashkey])

    def hmset(self, hashkey, value):  # pylint: disable=R0201
        """Emulate hmset."""

        # Iterate over every key:value in the value argument.
        for attributekey, attributevalue in value.items():
            self.redis[hashkey][attributekey] = attributevalue

    def hdel(self, hashkey, key):
        if key in self.redis[hashkey]:
            del self.redis[hashkey][key]

    def hset(self, hashkey, key, value):
        if not hashkey in self.redis:
            self.redis[hashkey] = {}

        self.redis[hashkey][key] = value

    def lrange(self, key, start, stop):
        """Emulate lrange."""

        # Does the set at this key already exist?
        if key in self.redis:
            # Yes, add this to the list
            return self.redis[key][start:stop + 1]
        else:
            # No, override the defaultdict's default and create the list
            self.redis[key] = list([])

    def rpush(self, key, *args):
        """Emulate rpush."""

        # Does the set at this key already exist?
        if not key in self.redis:
            self.redis[key] = list([])
        for arg in args:
            self.redis[key].append(arg)

    def rpop(self, key, *args):
        """Emulate rpop."""

        if key in self.redis:
            result = self.redis[key].pop()
            if self.redis[key] == []:
                self.delete(key)
            return result

    def sadd(self, key, value):  # pylint: disable=R0201
        """Emulate sadd."""

        # Does the set at this key already exist?
        if key in self.redis:
            # Yes, add this to the set
            self.redis[key].add(value)
        else:
            # No, override the defaultdict's default and create the set
            self.redis[key] = set([value])

    def srem(self, key, member):
        """Emulate a srem."""
        if type(self.redis[key]) == dict:
            if member in self.redis[key]:
                del self.redis[key][member]
        else:
            self.redis[key].discard(member)

        return self

    def srandmember(self, key):
        """Emulate a srandmember."""
        length = len(self.redis[key])
        rand_index = random.randint(0, length - 1)

        i = 0
        for set_item in self.redis[key]:
            if i == rand_index:
                return set_item

    def smembers(self, key):  # pylint: disable=R0201
        """Emulate smembers."""

        return self.redis[key]

    def zadd(self, key, value, value_number):
        """Emulate zadd."""
        # Does the set at this key already exist?
        if not key in self.redis:
            # Yes, set the dict value
            self.redis[key] = []

        self.redis[key].append({value: value_number})

    def zcount(self, key, start, finish):
        """Emulate zcount."""
        if key in self.redis:
            return len(self.redis[key])
        else:
            return 0

    def zrange(self, key, start, finish):
        """Emulate zrange"""
        keys_in_values = []

        if key in self.redis:
            for zdict in self.redis[key]:
                for zdict_key in zdict:
                    keys_in_values.append(zdict_key)

        return keys_in_values

    def incr(self, key):
        """Emulate incr"""
        if key in self.redis:
            self.redis[key] += 1
        else:
            self.redis[key] = 1

        return self.redis[key]

    def flushdb(self):
        self.redis.clear()


def mock_redis_client():
    """
    Mock common.util.redis_client so we can return a MockRedis object
    instead of a Redis object.
    """
    return MockRedis()
