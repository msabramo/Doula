import unittest
import time
from doula.queue import Queue


def slow_function(num=0):
    if num < 0:
        raise Exception

    previous = 1
    for i in range(1, num):
        previous = previous + i
    return previous


class QueueTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_this(self):
        q = Queue()
        q.this('add',
               'MT1',
               'DummyCode',
               'doula.tests.test_queue:slow_function',
               num=100000000)
