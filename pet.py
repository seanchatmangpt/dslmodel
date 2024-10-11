from pydantic import Field

from dslmodel import DSLModel


class Pet(DSLModel):
    """A DSLModel representing a pet."""

    id: int = Field(default=None, alias="id", description="Unique identifier for the field")
    name: str = Field(
        default=None, alias="name", description="A field to store the name of an entity."
    )
    category: str = Field(
        default=None, alias="category", description="A category field for classification purposes."
    )
    photo_urls: list[str] = Field(
        default=None, alias="photoUrls", description="A list of URLs of the photo."
    )
    tags: str = Field(
        default=None, alias="tags", description="A list of tags for categorization and filtering."
    )
    status: str = Field(
        default=None, alias="status", description="Indicates the current status of the entity."
    )


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()

    cali = Pet.from_prompt("Cali the Cat")
    print(cali)


if __name__ == "__main__":
    main()
