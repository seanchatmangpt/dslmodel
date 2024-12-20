from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class NuxtFilesystemModel(DSLModel):
    """A model representing the Nuxt filesystem."""
    pages: int = Field(default=1, alias: "pages", title="", description="The number of pages in a document or book.")
    components: str = Field(default=None, alias: "components", title="", description="A field to store the components of a system or a product.")
    layouts: str = Field(default=None, alias: "layouts", title="", description="A field to store the layout configuration.")
    middleware: str = Field(default=None, alias: "middleware", title="", description="The middleware field is used to specify the software that acts as an intermediary between the operating system and applications, enabling communication and data exchange between them.")
    plugins: str = Field(default=None, alias: "plugins", title="", description="A list of plugins used in the application.")
    static: str = Field(default=None, alias: "static", title="", description="A static field for storing static data.")
    store: str = Field(default=None, alias: "store", title="", description="The name of the store where the item is located.")
    nuxt_config: str = Field(default=None, alias: "nuxtConfig", title="", description="The Nuxt configuration file.")

