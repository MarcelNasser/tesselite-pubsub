import json
from typing import Union
from tesselite import root_logger
from tesselite.exceptions import MessageProcessingException


class Message:

    content: dict | None # message content as map

    def __init__(self, content: Union [str, dict]):
        if isinstance(content, str):
            self.content = json.loads(content)
        elif isinstance(content, dict):
            self.content = content
        else:
            root_logger.error(f"unsupported message type: {type(content)}")
            raise MessageProcessingException(content)

    def serialize(self) -> str:
        return json.dumps(self.content)

    @classmethod
    def deserialize(cls, message: str):
        return cls(message)
