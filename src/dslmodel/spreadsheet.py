from pathlib import Path
from typing import Type, TypeVar, List, Union, Iterator

from pydantic import Field
from dslmodel import DSLModel
from dslmodel.readers.data_reader import DataReader

# Define a type variable to represent the specific DSLModel type used in DSLSpreadsheet
T = TypeVar("T", bound=DSLModel)


class Person(DSLModel):
    id_: int = Field(alias="id")
    name: str
    age: int
    friends_ids: list[int]


class PandasSQLModel(DSLModel):
    """
    Example:
        input: Select all
        output: SELECT * FROM df
    """
    sqldf_query: str = Field(
        ..., description="SQL query to be applied to the `df` table only. That is the only table."
    )


class DSLSpreadsheet:
    def __init__(self, file_path: Union[str, Path], dsl_model: Type[T]):
        self.reader = DataReader(file_path)
        self.dsl_model = dsl_model  # Required DSLModel type
        self.results: List[T] = []  # Ensure results are a list of dsl_model instances
        self.load_data()

    def load_data(self):
        """Load data and convert each row to an instance of dsl_model."""
        raw_results = self.reader.forward()  # Fetch data from file
        self.results = [self.dsl_model.model_validate(row) for row in raw_results]

    def from_prompt(self, prompt: str) -> List[T]:
        """Generate and execute SQL query from prompt, returning typed results."""
        query_prompt = f"""{prompt}\ncolumns: {', '.join(self.dsl_model.field_names())}"""
        query = PandasSQLModel.from_prompt(query_prompt).sqldf_query
        raw_results = self.reader.forward(query=query)
        self.results = [self.dsl_model.model_validate(row) for row in raw_results]
        return self.results

    def ask(self, prompt: str) -> List[T]:
        """Alias for from_prompt for natural querying."""
        return self.from_prompt(prompt)

    def __getitem__(self, item: int) -> T:
        return self.results[item]

    def __iter__(self) -> Iterator[T]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


class Domain(DSLModel):
    domain_name: str = Field(..., alias="Domain Name")


def main():
    from dslmodel import init_text
    from dslmodel.utils.file_tools import data_dir

    init_text()

    # Create spreadsheet with Domain as required DSLModel
    spreadsheet = DSLSpreadsheet(data_dir("domain_list.csv"), dsl_model=Domain)
    first_domain = spreadsheet[0]  # Typed as Domain because of TypeVar T
    print(type(first_domain))


if __name__ == "__main__":
    main()
