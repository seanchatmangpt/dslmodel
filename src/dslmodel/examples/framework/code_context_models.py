from pydantic import Field, HttpUrl

from dslmodel import DSLModel


class RelatedModule(DSLModel):
    """
    Represents a related module that the current project interacts with. This field helps capture dependencies
    between different parts of the system. Each related module should have its own .context.md file, either
    stored locally or accessed via a URL. This relationship provides external context for the generator to
    understand project-level modularity and interdependencies.
    """

    name: str = Field(..., description="The name of the related module.")
    path: str = Field(
        ..., description="The relative path or URL to the related module’s .context.md file."
    )


class Diagram(DSLModel):
    """
    Describes a diagram that helps visualize the project’s structure or flow. Diagrams provide crucial context for
    understanding how components interact and operate within the system. This can help the generator integrate
    or visualize components in generated code or documentation.
    """

    name: str = Field(..., description="The name of the diagram.")
    path: str = Field(
        ...,
        description="The file path to the diagram, preferably in .mermaid format or another visual format.",
    )


class Architecture(DSLModel):
    """
    Defines the overall architecture of the project. The architecture field gives the code generator a top-level view
    of the project, allowing it to make decisions based on the style, components, and data flow between them.
    This helps the generator understand the structural design of the project.
    """

    style: str = Field(
        ..., description="The architecture style (e.g., microservices, monolithic, layered)."
    )
    components: list[str] = Field(..., description="The key components of the system.")
    data_flow: str | None = Field(
        None, description="A description of how data moves through the system."
    )


class Development(DSLModel):
    """
    Outlines the development process, including setup, build, and testing commands. This section provides the generator
    with insight into how the project is built and tested, which helps automate tasks like setting up environments
    or integrating with CI/CD pipelines.
    """

    setup_steps: list[str] = Field(
        ..., description="The steps required to set up the project for development."
    )
    build_command: str | None = Field(None, description="The command used to build the project.")
    test_command: str | None = Field(
        None, description="The command used to run tests in the project."
    )


class BusinessRequirements(DSLModel):
    """
    Captures the key business requirements of the project. This helps the generator align code generation with
    business goals and features that are most important. It provides the context necessary to prioritize features
    and ensure the system aligns with business objectives.
    """

    key_features: list[str] = Field(
        ..., description="The main features that fulfill the business requirements."
    )
    target_audience: str = Field(..., description="A description of the project's target audience.")
    success_metrics: list[str] = Field(
        ..., description="Metrics used to measure the success of the project."
    )


class QualityAssurance(DSLModel):
    """
    Details the quality assurance processes, including testing frameworks and coverage thresholds. By understanding
    the quality benchmarks, the generator can ensure that generated code follows the necessary testing and
    performance standards.
    """

    testing_frameworks: list[str] = Field(
        ..., description="The testing frameworks used in the project."
    )
    coverage_threshold: float | None = Field(
        None, description="The required code coverage percentage threshold."
    )
    performance_benchmarks: list[str] | None = Field(
        None, description="The performance benchmarks that must be met."
    )


class Deployment(DSLModel):
    """
    Describes how and where the project is deployed. This includes platform details and CI/CD pipeline configurations.
    The deployment field is critical for the generator to automate and optimize deployment processes.
    """

    platform: str = Field(
        ..., description="The platform where the project is deployed (e.g., AWS, GCP)."
    )
    cicd_pipeline: str | None = Field(
        None, description="Details about the CI/CD pipeline used for deployment."
    )
    staging_environment: HttpUrl | None = Field(
        None, description="The URL to the staging environment."
    )
    production_environment: HttpUrl | None = Field(
        None, description="The URL to the production environment."
    )


class ContextFile(DSLModel):
    """
    The main model for .context.md files, representing the essential metadata and details about a project. Each field
    corresponds to a structured part of the YAML front matter, providing context that both humans and code generators
    can use to understand the project's architecture, development process, and business logic.
    """

    module_name: str = Field(..., description="The name of the project or module.")
    version: str = Field(..., description="The version of the project.")
    description: str = Field(
        ..., description="A brief description of the project, summarizing its purpose and scope."
    )
    related_modules: list[RelatedModule] | None = Field(
        None, description="A list of related modules the project depends on."
    )
    technologies: list[str] | None = Field(
        None,
        description="The primary technologies used in the project (e.g., languages, frameworks).",
    )
    conventions: list[str] | None = Field(
        None, description="Coding standards, naming conventions, or best practices followed."
    )
    directives: list[str] | None = Field(
        None, description="Any special directives or rules for the project."
    )
    diagrams: list[Diagram] | None = Field(
        None, description="Visual diagrams that describe the architecture or data flow."
    )
    architecture: Architecture | None = Field(
        None, description="The high-level architecture of the project."
    )
    development: Development | None = Field(
        None,
        description="Development-related details, such as setup steps and build/test commands.",
    )
    business_requirements: BusinessRequirements | None = Field(
        None, description="Business objectives and key features driving the project."
    )
    quality_assurance: QualityAssurance | None = Field(
        None, description="Quality assurance strategies, including testing and performance metrics."
    )
    deployment: Deployment | None = Field(
        None, description="Details about the deployment platform, CI/CD pipeline, and environments."
    )
