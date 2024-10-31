import abc
import unittest


class TestRedisPubsub(unittest.TestCase):

    def test_import(self):

        from tesselite.pubsub import RedisPubsub

        assert isinstance(RedisPubsub, abc.ABCMeta)

    def test_publish(self):
        assert True  # add assertion here

    def test_consume(self):
        assert True  # add assertion here

if __name__ == '__main__':
    unittest.main()
