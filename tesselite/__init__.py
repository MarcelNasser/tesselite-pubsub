# High-Level Setters
import os

from dotenv import load_dotenv

from tesselite.exceptions import ConfigurationException
from tesselite.logger import Logger

load_dotenv()

class App:
    Name = "tesselite"
    BrokerType = os.environ.get("BROKER", "GCP-PUBSUB")
    Logger = Logger(Name) # root logger


