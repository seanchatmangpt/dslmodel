from pathlib import Path

from dslmodel.readers.data_reader import DataReader
from dslmodel import DSLModel
from pydantic import Field


class Person(DSLModel):
    id_: int = Field(alias="id")
    name: str
    age: int


class PandasSQLModel(DSLModel):
    """
    Example:
        input: Select all
        output: SELECT * FROM df
    """
    sqldf_query: str = Field(..., description="SQL query to be applied to the `df` table only. That is the only table.")


class DSLSpreadsheet:
    def __init__(self, file_path: str | Path, dsl_model: type[DSLModel] = None):
        self.reader = DataReader(file_path)

        self.dsl_model = dsl_model

        self.results = None

    def convert_to_model(self):
        if not self.dsl_model:
            return self.results

        typed_results = []
        for row in self.results:
            typed_results.append(self.dsl_model.model_validate(row))

        self.results = typed_results

    def from_prompt(self, prompt: str):
        prompt = f"""{prompt}
        columns: {self.dsl_model.field_names()}"""

        query = PandasSQLModel.from_prompt(prompt).sqldf_query
        self.results = self.reader.forward(query=query)
        self.convert_to_model()
        return self.results

    def ask(self, prompt: str):
        return self.from_prompt(prompt)
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.results[item]
        elif isinstance(item, str):
            return [row[item] for row in self.results]
        else:
            raise KeyError(f"Invalid key type: {type(item)}")

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)


def main():
    from dslmodel import init_instant, init_text
    from dslmodel.utils.file_tools import data_dir

    init_text()

    spreadsheet = DSLSpreadsheet(data_dir("sample_data.csv"), dsl_model=Person)
    # print(spreadsheet.ask("Select names like jane"))
    # print(spreadsheet.ask("older than 24"))
    print(spreadsheet.ask("who has the middle age?"))
    # print(spreadsheet[0])


if __name__ == "__main__":
    main()
