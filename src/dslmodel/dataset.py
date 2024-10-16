from pathlib import Path
import random
from typing import Optional, List, Type

from dspy.datasets.dataset import Dataset
from dslmodel import DSLModel
from dslmodel.readers.data_reader import DataReader
from pydantic import ValidationError

from dslmodel.spreadsheet import PandasSQLModel


class DSLDataset(Dataset):
    """
    A dataset class for MLE-bench competition reports with spreadsheet-like querying,
    validation through DSLModels, and flexible data handling.
    """

    def __init__(
        self,
        dsl_model: Type[DSLModel],  # Required DSLModel to structure and validate data
        file_path: Optional[Path] = None,  # Optional file path for loading external data
        num_reports: int = 0,  # Number of synthetic reports to generate if no file is provided
        train_size: float = 0.75,  # Train/Dev split ratio
        seed: Optional[int] = None  # Seed for reproducibility
    ):
        """Initialize the dataset with a DSLModel and either a file path or synthetic data."""
        super().__init__()
        random.seed(seed)  # Ensure reproducibility

        self.dsl_model = dsl_model  # Store the DSLModel class
        self.reader = DataReader(file_path) if file_path else None

        if file_path:
            print(f"📂 Loading data from: {file_path}")
            raw_data = self.reader.forward()
            self.data = self._convert_to_model(raw_data)  # Convert to DSLModels
        else:
            print(f"🧪 Generating {num_reports} synthetic reports...")
            self.data = [dsl_model() for _ in range(num_reports)]

        self._train_ = []
        self._dev_ = []
        self.split(train_size)

    def _convert_to_model(self, raw_data: List[dict]) -> List[DSLModel]:
        """Convert raw data to instances of the DSLModel."""
        typed_data = []
        for row in raw_data:
            try:
                typed_data.append(self.dsl_model.model_validate(row))
            except ValidationError as e:
                print(f"⚠️ Validation error: {e}")
                continue  # Skip invalid rows
        return typed_data

    def split(self, train_size: float = 0.75):
        """Split the dataset into train and dev sets."""
        split_index = int(len(self.data) * train_size)
        self._train_ = self.data[:split_index]
        self._dev_ = self.data[split_index:]
        print(f"📊 Dataset split: {len(self._train_)} train, {len(self._dev_)} dev")

    def resplit(self, train_size: float):
        """Allow re-splitting of the dataset at runtime."""
        self.split(train_size)

    @property
    def train(self) -> List[DSLModel]:
        """Return the train set."""
        return self._train_

    @property
    def dev(self) -> List[DSLModel]:
        """Return the dev set."""
        return self._dev_

    def ask(self, prompt: str) -> List[DSLModel]:
        """Query the dataset using a natural language-like SQL prompt."""
        return self.from_prompt(prompt)

    def from_prompt(self, prompt: str) -> List[DSLModel]:
        """Generate an SQL query from the prompt and retrieve matching results."""
        prompt = f"{prompt}\ncolumns: {self.dsl_model.field_names()}"
        query = PandasSQLModel.from_prompt(prompt).sqldf_query
        raw_results = self.reader.forward(query=query) if self.reader else []
        return self._convert_to_model(raw_results)

    def get_random_sample(self) -> DSLModel:
        """Retrieve a random report from the dataset."""
        return random.choice(self.data)

    def __getitem__(self, item) -> DSLModel:
        """Enable access by index."""
        return self.data[item]

    def __len__(self) -> int:
        """Return the total number of reports."""
        return len(self.data)

    def __iter__(self):
        """Iterate over the dataset."""
        return iter(self.data)


# Example Usage
def main():
    """Main function to demonstrate DSLDataset usage."""
    # Initialize with synthetic reports using MLE_Bench_CompetitionReport as the DSL model
    dataset = DSLDataset(dsl_model=MLE_Bench_CompetitionReport, num_reports=100, seed=42)

    # Explore the dataset
    print(f"Total reports: {len(dataset)}")
    print("Random Sample:")
    print(dataset.get_random_sample().model_dump_json(indent=2))

    # Query using prompts
    print("Query Result:")
    print(dataset.ask("Select reports with gold_medal = true"))

    # Train and dev set sizes
    print(f"Train set size: {len(dataset.train)}")
    print(f"Dev set size: {len(dataset.dev)}")


if __name__ == "__main__":
    main()
