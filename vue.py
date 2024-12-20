from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class Vue(DSLModel):
    """A user interface framework for building web applications."""
    main.js: str = Field(default=None, alias: "main.js", title="", description="Main JavaScript file for the application.")
    app.vue: str = Field(default=None, alias: "App.vue", title="", description="The main application Vue.js file.")
    components/: str = Field(default=None, alias: "components/", title="", description="A field used to store components.")
    vite.config.js: str = Field(default=None, alias: "vite.config.js", title="", description="Configuration file for Vite, a fast and lightweight development server.")
    package.json: str = Field(default=None, alias: "package.json", title="", description="A JSON file containing metadata about the project, including its name, version, and dependencies.")

