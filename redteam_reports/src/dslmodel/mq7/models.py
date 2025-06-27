from typing import Dict, Optional

from pydantic import AnyUrl, BaseModel, RootModel

from dslmodel import DSLModel


class Contact(BaseModel):
    name: Optional[str]
    url: Optional[AnyUrl]
    email: Optional[str]

    model_config = {
        "extra": "allow"
    }


class License(BaseModel):
    name: str
    url: Optional[AnyUrl]

    model_config = {
        "extra": "allow"
    }


class Info(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    termsOfService: Optional[AnyUrl] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None

    model_config = {
        "extra": "allow"
    }


class Server(BaseModel):
    host: str
    protocol: str

    model_config = {
        "extra": "allow"
    }


class Servers(RootModel[Dict[str, Server]]):
    pass


class Property(BaseModel):
    type: str
    minimum: Optional[int] = None
    format: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "extra": "allow"
    }


class Payload(BaseModel):
    type: str
    properties: Dict[str, Property]

    model_config = {
        "extra": "allow"
    }


class Message(BaseModel):
    name: str
    payload: Payload

    model_config = {
        "extra": "allow"
    }


class Messages(RootModel[Dict[str, Message]]):
    pass


class Channel(BaseModel):
    address: str
    messages: Messages

    model_config = {
        "extra": "allow"
    }


class Channels(RootModel[Dict[str, Channel]]):
    pass


class Operation(BaseModel):
    action: str
    summary: str
    channel: str  # Reference to a channel, e.g., '#/channels/lightMeasured'

    model_config = {
        "extra": "allow"
    }


class Operations(RootModel[Dict[str, Operation]]):
    pass


class AsyncAPI(DSLModel):
    asyncapi: str
    info: Info
    servers: Servers
    channels: Channels
    operations: Operations

    model_config = {
        "extra": "allow"
    }


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    print(AsyncAPI.from_yaml(file_path="/Users/sac/dev/dslmodel/asyncapi.yaml"))


if __name__ == '__main__':
    main()
