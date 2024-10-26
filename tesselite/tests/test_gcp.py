import abc
import unittest
from unittest.mock import patch

class TestGCPPubsub(unittest.TestCase):

    @patch('dotenv.load_dotenv')
    def test_import(self, load):

        load.side_effect = [None] * 3

        from tesselite.pubsub import GCPPubSub

        assert isinstance(GCPPubSub, abc.ABCMeta)

    def test_publish(self):
        assert True  # add assertion here

    def test_consume(self):
        assert True  # add assertion here

if __name__ == '__main__':
    unittest.main()
