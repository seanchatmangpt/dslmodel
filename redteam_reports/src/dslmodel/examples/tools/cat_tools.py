import httpx

from dslmodel import DSLModel
from dslmodel.mixins.tools import ToolMixin


class Cat(DSLModel):
    id: str
    name: str | None = None
    url: str
    width: int
    height: int


class CatBreed(DSLModel):
    name: str
    description: str


# Define the base URL for The Cat API
CAT_API_URL = "https://api.thecatapi.com/v1"


class CatTools(ToolMixin):
    def fetch_random_cat_image(self) -> Cat:
        """Fetch a random cat image from the API."""
        with httpx.Client() as client:
            response = client.get(f"{CAT_API_URL}/images/search")
            return Cat(**response.json()[0])

    def fetch_cat_breeds(self, limit: int | None = 5) -> list[CatBreed]:
        """Fetch cat breeds with a limit on the number of breeds."""
        with httpx.Client() as client:
            response = client.get(f"{CAT_API_URL}/breeds")
            breeds = response.json()[:limit]  # Limit the number of breeds
            breed_info = [
                CatBreed(name=breed["name"], description=breed["description"]) for breed in breeds
            ]
            return breed_info


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()

    # Example usage
    cats = CatTools()

    result = cats.call("get rando", True)
    for cat in result:
        print(cat)


if __name__ == "__main__":
    main()
