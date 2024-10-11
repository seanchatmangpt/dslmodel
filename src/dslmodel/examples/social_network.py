from pydantic import Field

from dslmodel import DSLModel


class SocialNetwork(DSLModel):
    """A model named SocialNetwork from the friend of a friend ontology with 20 fields"""

    user_id: int = Field(default=None, title="", description="A unique identifier for the user.")
    friend_id: int = Field(default=None, title="", description="A unique identifier for a friend.")
    acquaintance_id: int = Field(
        default=None, title="", description="A unique identifier for an acquaintance."
    )
    connection_type: str = Field(
        default=None, title="", description="The type of connection used to access the data."
    )
    relationship_status: str = Field(
        default=None, title="", description="The current relationship status of the individual."
    )
    friend_of_friend_id: str = Field(
        default=None, title="", description="A field to store the id of a friend of a friend."
    )
    friend_of_friend_type: str = Field(
        default=None,
        title="",
        description="The type of friend of a friend, e.g., acquaintance, colleague, or family member.",
    )
    friend_of_friend_status: str = Field(
        default=None, title="", description="Status of a friend of a friend"
    )
    acquaintance_of_friend_id: int = Field(
        default=None, title="", description="The ID of a friend's acquaintance."
    )
    acquaintance_of_friend_type: str = Field(
        default=None,
        title="",
        description="A person with whom one knows someone but not very well.",
    )
    acquaintance_of_friend_status: str = Field(
        default=None, title="", description="The status of acquaintance of a friend"
    )
    connection_to_friend_id: str = Field(
        default=None,
        title="",
        description="A connection to a friend's id for social media purposes.",
    )
    connection_to_friend_type: str = Field(
        default=None,
        title="",
        description="A connection type to a friend, e.g., social media, phone number, or email.",
    )
    connection_to_friend_status: str = Field(
        default=None,
        title="",
        description="The status of a connection to a friend, e.g., active, inactive, pending.",
    )
    connection_from_friend_id: str = Field(
        default=None, title="", description="A connection to a friend based on their ID."
    )
    connection_from_friend_type: str = Field(
        default=None,
        title="",
        description="A connection from a friend type, e.g., social media, family, or colleague.",
    )
    connection_from_friend_status: str = Field(
        default=None,
        title="",
        description="A status indicating whether a connection is made from a friend.",
    )
    friend_of_acquaintance_id: int = Field(
        default=None, title="", description="The ID of a friend or acquaintance."
    )
    friend_of_acquaintance_type: str = Field(
        default=None, title="", description="A field to specify the type of friend or acquaintance."
    )
    friend_of_acquaintance_status: str = Field(
        default=None, title="", description="The status of a friend or acquaintance."
    )
    connection_to_acquaintance_id: int = Field(
        default=None,
        title="",
        description="A unique identifier for the connection to an acquaintance.",
    )
