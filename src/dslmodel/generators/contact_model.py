from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class ContactModel(DSLModel):
    """Verbose contact model from the friend of a friend ontology with 20 fields"""
    id: str = Field(default=None, title="", description="Unique identifier for the object.")
    name: str = Field(default=None, title="", description="A useful description for the name field")
    email: EmailStr = Field(default=None, title="", description="Email address for user authentication")
    phone_number: str = Field(default=None, title="", description="A phone number for contact purposes.")
    address: str = Field(default=None, title="", description="The physical address of the location.")
    social_media_handles: str = Field(default=None, title="", description="A list of social media handles for the user.")
    friend_status: str = Field(default=None, title="", description="The status of a friend, e.g., active, inactive, pending.")
    relationship_type: str = Field(default=None, title="", description="The type of relationship between entities.")
    mutual_friend_count: int = Field(default=0, title="", description="The number of mutual friends between two users.")
    friend_since: str = Field(default=None, title="", description="The date since when the person is considered a friend.")
    last_contact: str = Field(default=None, title="", description="The date of the last contact with the customer.")
    contact_method: str = Field(default=None, title="", description="A method of contact, e.g., phone, email, or in-person.")
    contact_frequency: str = Field(default=None, title="", description="The frequency at which to contact the customer, e.g., daily, weekly, monthly.")
    friend_type: str = Field(default=None, title="", description="A type of friend, e.g., close friend, acquaintance, or family member.")
    friend_group: str = Field(default=None, title="", description="A group of friends.")
    friend_network: str = Field(default=None, title="", description="A network of friends.")
    social_media_platforms: str = Field(default=None, title="", description="A list of social media platforms the user is active on.")
    profile_links: str = Field(default=None, title="", description="A list of links to the user's social media profiles.")
    contact_notes: str = Field(default=None, title="", description="Notes about the contact")
    update_status: str = Field(default=None, title="", description="A status update for the field.")

