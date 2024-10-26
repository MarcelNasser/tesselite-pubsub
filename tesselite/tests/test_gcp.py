import abc
import unittest
from unittest.mock import patch

from tesselite import ConfigurationException


class TestGCPPubsub(unittest.TestCase):

    @patch('tesselite.load')
    @patch('dotenv.load_dotenv')
    def test_import(self, *mocked):

        from tesselite.pubsub import GCPPubSub

        assert isinstance(GCPPubSub, abc.ABCMeta)

    def test_publish(self):
        assert True  # add assertion here

    def test_consume(self):
        assert True  # add assertion here

if __name__ == '__main__':
    unittest.main()
