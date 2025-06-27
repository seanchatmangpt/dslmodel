import json
from functools import partial

import requests
from loguru import logger


class DSLVerb:
    def __init__(self, context=None, **kwargs):
        """
        Initialize the verb with an optional context dictionary.
        Additional keyword arguments can be used to preset context parameters.
        """
        self.context = context if context is not None else {}
        self.update_context(kwargs)

    def __call__(self, context):
        """
        Execute the verb's main functionality.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("This verb must implement the __call__ method.")

    def __or__(self, other):
        """
        Allow chaining verbs using the pipe (|) operator.
        """
        return ComposeVerb(self, other)

    def update_context(self, updates: dict):
        """
        Update the internal context with new values.
        """
        self.context.update(updates)

    def curry(self, **kwargs):
        """
        Preset certain context parameters for the verb.
        """
        new_context = self.context.copy()
        new_context.update(kwargs)
        return partial(self, new_context)

    def bind(self, func):
        """
        Bind a function to the verb's output.
        """
        if not hasattr(self, "value") or self.value is None:
            return DSLVerb(context=self.context)  # Propagate with current context
        try:
            new_value = func(self.value)
            new_verb = DSLVerb(self.context)
            new_verb.value = new_value
            return new_verb
        except Exception as e:
            logger.error(f"Error: {e!s}")
            return DSLVerb(context=self.context)


class ComposeVerb(DSLVerb):
    def __init__(self, verb1: DSLVerb, verb2: DSLVerb):
        """
        Initialize with two verbs to be composed.
        """
        # Merge contexts from both verbs
        combined_context = {**verb1.context, **verb2.context}
        super().__init__(context=combined_context)
        self.verb1 = verb1
        self.verb2 = verb2

    def __call__(self, context):
        """
        Execute the first verb, then the second verb using the updated context.
        """
        # Execute the first verb
        result1 = self.verb1(context)
        if result1 is None:
            logger.error("Composition halted: First verb returned None.")
            return None

        # Execute the second verb
        result2 = self.verb2(context)
        if result2 is None:
            logger.error("Composition halted: Second verb returned None.")
            return None

        return context

    def __or__(self, other):
        """
        Allow further chaining by composing with another verb.
        """
        return ComposeVerb(self, other)


class FetchData(DSLVerb):
    def __call__(self, context):
        """
        Fetch data from a specified URL and store it in the context.
        """
        url = context.get("url")
        if not url:
            logger.error("No URL provided for FetchData.")
            context["data"] = None
            return None

        logger.info(f"Fetching data from {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()  # Return JSON data
            context["data"] = data  # Store the result in context
            return context
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e!s}")
            context["data"] = None
            return None  # Return None if there was an error


class ProcessData(DSLVerb):
    def __call__(self, context):
        """
        Process the fetched data and store the processed data in the context.
        """
        data = context.get("data")
        if data is None:
            logger.error("No data to process.")
            context["processed_data"] = None
            return None
        logger.info(f"Processing data: {data}")
        # Example processing: filter out items with falsy values
        if isinstance(data, list):
            # If data is a list of dictionaries
            processed_data = [{k: v for k, v in item.items() if v} for item in data]
        elif isinstance(data, dict):
            processed_data = {k: v for k, v in data.items() if v}
        else:
            logger.error("Unsupported data format for processing.")
            processed_data = None
        context["processed_data"] = processed_data
        return context


class SaveToFile(DSLVerb):
    def __call__(self, context):
        """
        Save the processed data to a specified file path.
        """
        data = context.get("processed_data")
        file_path = context.get("file_path", "output.json")

        if data is None:
            logger.error("No data to save.")
            context["saved_file"] = None
            return None
        logger.info(f"Saving data to {file_path}")
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Data successfully saved to {file_path}")
            context["saved_file"] = file_path
            return context
        except Exception as e:
            logger.error(f"Failed to save data: {e!s}")
            context["saved_file"] = None
            return None


# Sample data for testing without making actual HTTP requests
cat_api_data = [
    {"id": "59k", "url": "https://cdn2.thecatapi.com/images/59k.jpg", "width": 500, "height": 375},
    {"id": "8la", "url": "https://cdn2.thecatapi.com/images/8la.jpg", "width": 640, "height": 480},
    {"id": "9l1", "url": "https://cdn2.thecatapi.com/images/9l1.jpg", "width": 900, "height": 1267},
    {"id": "cc0", "url": "https://cdn2.thecatapi.com/images/cc0.jpg", "width": 900, "height": 609},
    {"id": "dgh", "url": "https://cdn2.thecatapi.com/images/dgh.jpg", "width": 679, "height": 1012},
    {"id": "dl1", "url": "https://cdn2.thecatapi.com/images/dl1.jpg", "width": 500, "height": 333},
    {"id": "eeb", "url": "https://cdn2.thecatapi.com/images/eeb.jpg", "width": 400, "height": 267},
    {
        "id": "MTU4NjcyMg",
        "url": "https://cdn2.thecatapi.com/images/MTU4NjcyMg.jpg",
        "width": 480,
        "height": 640,
    },
    {
        "id": "2UAyYkzVK",
        "url": "https://cdn2.thecatapi.com/images/2UAyYkzVK.jpg",
        "width": 2890,
        "height": 2271,
    },
    {
        "id": "JBkP_EJm9",
        "url": "https://cdn2.thecatapi.com/images/JBkP_EJm9.jpg",
        "width": 800,
        "height": 1114,
    },
]


def main():
    # Initialize the shared context with necessary parameters
    initial_context = {
        "url": "https://api.thecatapi.com/v1/images/search?limit=10",
        "file_path": "hello.json",
    }

    # Instantiate verbs without presetting any parameters
    fetch_data = FetchData()
    process_data = ProcessData()
    save_to_file = SaveToFile()

    # Chain verbs together using the pipe (|) operator
    pipeline = fetch_data | process_data | save_to_file

    # For testing purposes, we'll mock the FetchData call to use predefined data
    # Replace the FetchData __call__ method with the mock
    def mock_fetch(context):
        url = context.get("url")
        logger.info(f"Mock fetching data from {url}")
        context["data"] = cat_api_data  # Store predefined data in context
        return context

    # Assign the mock_fetch method to the fetch_data instance
    fetch_data.__call__ = mock_fetch

    # Execute the pipeline with the initial context
    pipeline(initial_context)

    # Optionally, inspect the final context
    logger.info(f"Final context: {initial_context}")


if __name__ == "__main__":
    main()
