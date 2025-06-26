from typing import List, Optional
from pydantic import BaseModel

from dslmodel import DSLModel


class Supplier(BaseModel):
    """Represents a supplier in the SIPOC process."""
    name: str
    description: str


class Input(BaseModel):
    """Represents an input in the SIPOC process."""
    name: str
    description: str


class ProcessStep(BaseModel):
    """Represents a single step in the process."""
    step_name: str
    description: str


class Output(BaseModel):
    """Represents an output in the SIPOC process."""
    name: str
    description: str


class Customer(BaseModel):
    """Represents a customer in the SIPOC process."""
    name: str
    description: str


class SIPOC(DSLModel):
    """Represents the complete SIPOC diagram."""
    suppliers: List[Supplier]
    inputs: List[Input]
    process: List[ProcessStep]
    outputs: List[Output]
    customers: List[Customer]


class Program(DSLModel):
    """Represents a program containing multiple SIPOCs."""
    program_name: str
    description: str
    sipocs: List[SIPOC]
    overall_objective: str
    program_outputs: Optional[List[Output]]
    program_customers: Optional[List[Customer]]


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    sipoc_example = SIPOC(
        suppliers=[
            Supplier(name="Project Leads", description="Define project goals and priorities."),
            Supplier(name="Developers", description="Provide technical insights and source code."),
            Supplier(name="Architects", description="Supply architectural patterns."),
            Supplier(name="Business Analysts", description="Contribute business requirements."),
        ],
        inputs=[
            Input(name="Project Requirements", description="Define the scope and objectives."),
            Input(name="Existing Documentation", description="Reference prior information."),
            Input(name="Source Code Structure", description="Inform context organization."),
            Input(name="Developer Feedback", description="Iterate on context files."),
        ],
        process=[
            ProcessStep(step_name="Define .context Structure", description="Establish folder and file layout."),
            ProcessStep(step_name="Create index.md", description="Add metadata and overview."),
            ProcessStep(step_name="Document Technical Details", description="Write in docs.md."),
            ProcessStep(step_name="Generate Diagrams", description="Use Mermaid for visualizations."),
            ProcessStep(step_name="Iterate with Feedback", description="Refine based on input."),
        ],
        outputs=[
            Output(name=".context Directory", description="Single source of truth for project context."),
            Output(name="Structured Documentation", description="Easily navigable project details."),
            Output(name="Mermaid Diagrams", description="Visual aids for architecture."),
            Output(name="AI-Ready Files", description="Enable integration with AI tools."),
        ],
        customers=[
            Customer(name="Developers", description="Reference technical documentation."),
            Customer(name="Project Managers", description="Ensure alignment with goals."),
            Customer(name="AI Tools", description="Use structured data for automation."),
            Customer(name="External Contributors", description="Understand and contribute effectively."),
        ]
    )

    print(sipoc_example.to_yaml())

    # Define individual SIPOCs
    recruiter_sipoc = SIPOC(
        suppliers=[
            Supplier(name="Recruiter PMs", description="Define recruiter module requirements."),
            Supplier(name="Data Team", description="Provide candidate data insights."),
        ],
        inputs=[
            Input(name="Recruiter Requirements", description="Defines the scope of recruiter tools."),
            Input(name="Candidate Data Schema", description="Structure of candidate data."),
        ],
        process=[
            ProcessStep(step_name="Design Recruiter Features", description="Plan feature requirements."),
            ProcessStep(step_name="Develop Recruiter Module", description="Code and build features."),
            ProcessStep(step_name="Test and Iterate", description="Validate features with end users."),
        ],
        outputs=[
            Output(name="Recruiter Module", description="Functional recruiter tools for the platform."),
        ],
        customers=[
            Customer(name="HR Teams", description="Users of the recruiter tools."),
            Customer(name="Company Admins", description="Oversee the recruitment process."),
        ]
    )

    learning_sipoc = SIPOC(
        suppliers=[
            Supplier(name="Learning Content Team", description="Provide educational content."),
            Supplier(name="UX Team", description="Optimize the learning experience."),
        ],
        inputs=[
            Input(name="Learning Content", description="Curated learning materials."),
            Input(name="User Feedback", description="Feedback from learners."),
        ],
        process=[
            ProcessStep(step_name="Create Content Categories", description="Organize courses into themes."),
            ProcessStep(step_name="Develop Learning Platform", description="Implement the learning system."),
            ProcessStep(step_name="Refine UX", description="Enhance usability."),
        ],
        outputs=[
            Output(name="Learning Module", description="Complete course library with a user-friendly interface."),
        ],
        customers=[
            Customer(name="Learners", description="End-users accessing the platform."),
            Customer(name="Content Creators", description="Create and upload learning materials."),
        ]
    )

    # Define the overall Program
    workin_program = Program(
        program_name="Workin Product Development",
        description="Development of the Workin platform with interconnected modules for recruitment, learning, and professional growth.",
        sipocs=[recruiter_sipoc, learning_sipoc],
        overall_objective="Create a scalable and user-friendly platform for professional and educational growth.",
        program_outputs=[
            Output(name="Integrated Platform", description="A unified system integrating all modules."),
        ],
        program_customers=[
            Customer(name="Corporate Clients", description="End-to-end HR and learning solutions."),
            Customer(name="Individual Users", description="Job seekers and learners benefiting from the tools."),
        ]
    )

    # Print the program details
    print(workin_program.to_yaml())


if __name__ == '__main__':
    main()
