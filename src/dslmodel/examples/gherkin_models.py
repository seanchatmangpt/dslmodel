from __future__ import annotations
from typing import List, Optional, Union, Literal
from pydantic import Field
from enum import Enum

from dslmodel import DSLModel


class StepKeyword(str, Enum):
    """Enumeration of primary step keywords in Gherkin."""
    GIVEN = "Given"
    WHEN = "When"
    THEN = "Then"
    AND = "And"
    BUT = "But"
    STAR = "*"


class PrimaryKeyword(str, Enum):
    """Enumeration of primary keywords in Gherkin."""
    FEATURE = "Feature"
    RULE = "Rule"
    SCENARIO = "Scenario"
    SCENARIO_OUTLINE = "Scenario Outline"
    BACKGROUND = "Background"
    EXAMPLES = "Examples"


class SecondaryKeyword(str, Enum):
    """Enumeration of secondary keywords in Gherkin."""
    DOC_STRING = '"""'  # or '```'
    DATA_TABLE = '|'
    TAG = '@'
    COMMENT = '#'


class DocString(DSLModel):
    """
    Represents a multi-line string argument for a step, enclosed by delimiters.
    """
    content_type: Optional[str] = Field(
        None,
        description='Optional content type annotation (e.g., "markdown").'
    )
    content: str = Field(
        ...,
        description='The actual multi-line string content.'
    )


class DataTable(DSLModel):
    """
    Represents a table of data passed to a step.
    """
    headers: List[str] = Field(
        ...,
        description='List of column headers for the data table.'
    )
    rows: List[List[str]] = Field(
        ...,
        description='List of rows, each containing a list of cell values.'
    )


# Define StepArgument as a Union of DocString and DataTable
StepArgument = Union[DocString, DataTable]


class Step(DSLModel):
    """
    Represents a single step within a scenario.
    """
    keyword: str = Field(
        ...,
        description='The keyword that begins the step (e.g., Given, When, Then).'
    )
    text: str = Field(
        ...,
        description='The descriptive text of the step.'
    )
    argument: Optional[StepArgument] = Field(
        None,
        description='Optional argument for the step, either a DocString or a DataTable.'
    )





class Comment(DSLModel):
    """
    Represents a comment within the Gherkin feature file.
    """
    text: str = Field(
        ...,
        description='The text of the comment, excluding the leading # symbol.'
    )


class Background(DSLModel):
    """
    Represents a Background section containing steps common to all scenarios in a feature or rule.
    """
    keyword: Literal['Background'] = Field(
        ...,
        description='The keyword indicating this section is a Background.'
    )
    steps: List[Step] = Field(
        ...,
        description='List of Given steps that set up the context for all scenarios.'
    )


class Example(DSLModel):
    """
    Represents an Examples section providing data for a Scenario Outline.
    """
    keyword: Literal['Examples', 'Scenarios'] = Field(
        ...,
        description='The keyword indicating this section provides examples for a Scenario Outline.'
    )
    name: Optional[str] = Field(
        None,
        description='Optional name for the examples set.'
    )
    description: Optional[str] = Field(
        None,
        description='Optional description providing additional context for the examples.'
    )
    table: DataTable = Field(
        ...,
        description='The data table containing example values for scenario parameters.'
    )


class Scenario(DSLModel):
    """
    Represents a Scenario, which is a single executable test case.
    """
    keyword: Literal['Scenario', 'Example'] = Field(
        ...,
        description='The keyword indicating this is a Scenario or Example.'
    )
    name: str = Field(
        ...,
        description='The name of the scenario, describing its purpose.'
    )
    description: Optional[str] = Field(
        None,
        description='Optional description providing additional context for the scenario.'
    )
    tags: List[str] = Field(
        [],
        description='Optional list of tags categorizing the scenario.'
    )
    steps: List[Step] = Field(
        ...,
        description='List of steps that define the scenario behavior.'
    )


class ScenarioOutline(DSLModel):
    """
    Represents a Scenario Outline, which allows parameterization of scenarios using examples.
    """
    keyword: Literal['Scenario Outline', 'Scenario Template'] = Field(
        ...,
        description='The keyword indicating this is a Scenario Outline or Template.'
    )
    name: str = Field(
        ...,
        description='The name of the scenario outline, describing its purpose.'
    )
    description: Optional[str] = Field(
        None,
        description='Optional description providing additional context for the scenario outline.'
    )
    tags: Optional[List[str]] = Field(
        None,
        description='Optional list of tags categorizing the scenario outline.'
    )
    steps: List[Step] = Field(
        ...,
        description='List of steps that define the scenario outline behavior with placeholders.'
    )
    examples: List[Example] = Field(
        ...,
        description='List of examples providing data for the placeholders in the steps.'
    )


class Rule(DSLModel):
    """
    Represents a Rule, which groups related scenarios under a business rule.
    """
    keyword: Literal['Rule'] = Field(
        ...,
        description='The keyword indicating this section is a Rule.'
    )
    name: str = Field(
        ...,
        description='The name of the rule, describing the business rule it represents.'
    )
    description: Optional[str] = Field(
        None,
        description='Optional description providing additional context for the rule.'
    )
    tags: Optional[List[str]] = Field(
        None,
        description='Optional list of tags categorizing the rule.'
    )
    background: Optional[Background] = Field(
        None,
        description='Optional Background section containing common steps for all scenarios under this rule.'
    )
    children: List[Union[Scenario, ScenarioOutline]] = Field(
        ...,
        description='List of scenarios or scenario outlines that belong to this rule.'
    )


class Feature(DSLModel):
    """
    Represents a Feature, which is the root element of a Gherkin document.
    """
    keyword: Literal['Feature'] = Field(
        ...,
        description='The keyword indicating this section is a Feature.'
    )
    name: str = Field(
        ...,
        description='The name of the feature, describing the functionality being specified.'
    )
    description: Optional[str] = Field(
        None,
        description='Optional description providing additional context for the feature.'
    )
    tags: List[str] = Field(
        [],
        description='Optional list of tags categorizing the feature.'
    )
    background: Optional[Background] = Field(
        None,
        description='Optional Background section containing common steps for all scenarios in the feature.'
    )
    # children: List[Union[Rule, Scenario, ScenarioOutline]] = Field(
    #     ...,
    #     description='List of rules, scenarios, or scenario outlines that belong to this feature.'
    # )
    rules: List[Rule] = Field(
        [],
        description='List of rules that belong to this feature.'
    )
    scenarios: List[Scenario] = Field(
        [],
        description='List of scenarios that belong to this feature.'
    )
    scenario_outlines: List[ScenarioOutline] = Field(
        [],
        description='List of scenario outlines that belong to this feature.'
    )


class GherkinDocument(DSLModel):
    """
    Represents the entire Gherkin document, encapsulating the feature.
    """
    feature: Feature = Field(
        ...,
        description='The Feature defined in the Gherkin document.'
    )
    comments: Optional[List[Comment]] = Field(
        None,
        description='Optional list of comments present in the Gherkin document.'
    )


def main():
    """Main function"""
    from dslmodel.utils.dspy_tools import init_text, init_instant
    # from dslmodel.utils.dspy_tools import init_lm
    # init_lm()
    init_text()
    # init_instant()

    scenario = Scenario.from_prompt("I want to test the login feature with 4 steps. Make sure all fields have example values and tags")
    print(scenario.to_yaml())


if __name__ == '__main__':
    main()
