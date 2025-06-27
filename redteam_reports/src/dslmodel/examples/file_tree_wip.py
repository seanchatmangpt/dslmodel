# Define two trees for comparison
from pydantic2_schemaorg import JobPosting
from pydantic2_schemaorg.DefinedTerm import DefinedTerm

from dslmodel.utils.dspy_tools import init_versatile, init_lm

from typing import List, Optional
from pydantic2_schemaorg.Person import Person
from pydantic2_schemaorg.Organization import Organization
from pydantic2_schemaorg.Place import Place
from pydantic2_schemaorg.CreativeWork import CreativeWork
from pydantic2_schemaorg.EducationalOccupationalCredential import EducationalOccupationalCredential
from pydantic2_schemaorg.Language import Language
from pydantic2_schemaorg.Thing import Thing
from pydantic import BaseModel, Field

from dslmodel.utils.pydantic_ai_tools import instance

from pydantic import BaseModel, Field
from typing import List, Optional


class Location(BaseModel):
    address: Optional[str] = Field(None, description="The address of the location.")
    postalCode: Optional[str] = Field(None, description="The postal code of the location.")
    city: Optional[str] = Field(None, description="The city of the location.")
    countryCode: Optional[str] = Field(None, description="The country code (ISO Alpha-2) of the location.")
    region: Optional[str] = Field(None, description="The region or state of the location.")


class Profile(BaseModel):
    network: str = Field(..., description="The name of the network, e.g., Twitter.")
    username: str = Field(..., description="The username on the network.")
    url: str = Field(..., description="The URL of the profile.")


class Basics(BaseModel):
    name: str = Field(..., description="The full name of the individual.")
    label: str = Field(..., description="A label or job title for the individual.")
    image: Optional[str] = Field(None, description="URL to a profile image.")
    email: str = Field(..., description="The email address of the individual.")
    phone: str = Field(..., description="The phone number of the individual.")
    url: str = Field(..., description="The personal website URL of the individual.")
    summary: str = Field(..., description="A short summary or bio for the individual.")
    location: Location = Field(..., description="The physical location details of the individual.")
    profiles: List[Profile] = Field(..., description="A list of social or professional profiles.")


class Work(BaseModel):
    name: str = Field(..., description="The name of the company.")
    position: str = Field(..., description="The position held by the individual.")
    url: Optional[str] = Field(None, description="The URL of the company.")
    startDate: str = Field(..., description="The start date of the position (YYYY-MM-DD).")
    endDate: Optional[str] = Field(None, description="The end date of the position (YYYY-MM-DD).")
    summary: str = Field(..., description="A short summary of the role.")
    highlights: List[str] = Field(..., description="A list of notable highlights from the role.")


class Volunteer(BaseModel):
    organization: str = Field(..., description="The name of the organization.")
    position: str = Field(..., description="The position held by the individual.")
    url: Optional[str] = Field(None, description="The URL of the organization.")
    startDate: str = Field(..., description="The start date of the position (YYYY-MM-DD).")
    endDate: Optional[str] = Field(None, description="The end date of the position (YYYY-MM-DD).")
    summary: str = Field(..., description="A short summary of the role.")
    highlights: List[str] = Field(..., description="A list of notable highlights from the role.")


class Education(BaseModel):
    institution: str = Field(..., description="The name of the educational institution.")
    url: Optional[str] = Field(None, description="The URL of the institution.")
    area: str = Field(..., description="The area of study.")
    studyType: str = Field(..., description="The type of study, e.g., Bachelor.")
    startDate: str = Field(..., description="The start date of the education (YYYY-MM-DD).")
    endDate: Optional[str] = Field(None, description="The end date of the education (YYYY-MM-DD).")
    score: Optional[str] = Field(None, description="The grade or score achieved.")
    courses: List[str] = Field(..., description="A list of completed courses.")


class Award(BaseModel):
    title: str = Field(..., description="The title of the award.")
    date: str = Field(..., description="The date the award was received (YYYY-MM-DD).")
    awarder: str = Field(..., description="The name of the awarder.")
    summary: str = Field(..., description="A description or summary of the award.")


class Certificate(BaseModel):
    name: str = Field(..., description="The name of the certificate.")
    date: str = Field(..., description="The date the certificate was issued (YYYY-MM-DD).")
    issuer: str = Field(..., description="The issuer of the certificate.")
    url: Optional[str] = Field(None, description="The URL of the certificate.")


class Publication(BaseModel):
    name: str = Field(..., description="The name of the publication.")
    publisher: str = Field(..., description="The publisher of the publication.")
    releaseDate: str = Field(..., description="The release date of the publication (YYYY-MM-DD).")
    url: Optional[str] = Field(None, description="The URL of the publication.")
    summary: str = Field(..., description="A summary of the publication.")


class Skill(BaseModel):
    name: str = Field(..., description="The name of the skill.")
    level: str = Field(..., description="The proficiency level, e.g., Master.")
    keywords: List[str] = Field(..., description="A list of keywords associated with the skill.")


class Language(BaseModel):
    language: str = Field(..., description="The name of the language.")
    fluency: str = Field(..., description="The fluency level in the language.")


class Interest(BaseModel):
    name: str = Field(..., description="The name of the interest.")
    keywords: List[str] = Field(..., description="A list of keywords associated with the interest.")


class Reference(BaseModel):
    name: str = Field(..., description="The name of the referee.")
    reference: str = Field(..., description="The reference or note provided by the referee.")


class Project(BaseModel):
    name: str = Field(..., description="The name of the project.")
    startDate: str = Field(..., description="The start date of the project (YYYY-MM-DD).")
    endDate: Optional[str] = Field(None, description="The end date of the project (YYYY-MM-DD).")
    description: str = Field(..., description="A description of the project.")
    highlights: List[str] = Field(..., description="A list of notable highlights from the project.")
    url: Optional[str] = Field(None, description="The URL of the project.")


class Resume(BaseModel):
    basics: Basics = Field(..., description="Basic information about the individual.")
    work: List[Work] = Field(..., description="A list of work experiences.")
    volunteer: List[Volunteer] = Field(..., description="A list of volunteer experiences.")
    education: List[Education] = Field(..., description="A list of educational qualifications.")
    awards: List[Award] = Field(..., description="A list of awards received.")
    certificates: List[Certificate] = Field(..., description="A list of certificates achieved.")
    publications: List[Publication] = Field(..., description="A list of publications authored.")
    skills: List[Skill] = Field(..., description="A list of skills possessed.")
    languages: List[Language] = Field(..., description="A list of languages spoken.")
    interests: List[Interest] = Field(..., description="A list of interests.")
    references: List[Reference] = Field(..., description="A list of references.")
    projects: List[Project] = Field(..., description="A list of projects worked on.")


yawl_posting = """job_posting:
  description: We are seeking a highly motivated PhD holder with extensive experience in YAWL server management. The ideal candidate will have a strong background in workflow management systems and a proven track record of successfully implementing and maintaining YAWL servers. Excellent communication and problem-solving skills are essential. The candidate will be responsible for designing, implementing, and maintaining workflow management systems using YAWL. A strong understanding of workflow patterns, business process modeling, and workflow execution is required.
  requirements:
  - PhD in Computer Science or related field
  - At least 3 years of experience with YAWL server management
  - Strong understanding of workflow management systems and business process modeling
  - Excellent communication and problem-solving skills
  title: Research Position"""

Resume(basics=Basics(name='John Doe', label='PhD Researcher', image=None, email='johndoe@example.com',
                     phone='123-456-7890', url='https://www.example.com/johndoe',
                     summary='Highly motivated PhD holder with extensive experience in YAWL server management.',
                     location=Location(address=None, postalCode=None, city=None, countryCode=None, region=None),
                     profiles=[Profile(network='LinkedIn', username='johndoe123',
                                       url='https://www.linkedin.com/in/johndoe123')]),
       work=[Work(name='Google', position='Software Engineer', url=None, startDate='2015-01-01', endDate='2018-01-01',
                  summary='Designed and implemented workflow management systems using YAWL.',
                  highlights=['Improved workflow execution efficiency by 25%'])],
       volunteer=[Volunteer(organization='Workflow Management Association', position='President', url=None,
                            startDate='2020-01-01', endDate=None,
                            summary="Managed the association's workflow management system.",
                            highlights=['Improved workflow efficiency by 30%']),
                  Volunteer(organization='Business Process Modeling Group', position='Member', url=None,
                            startDate='2018-01-01', endDate=None,
                            summary='Contributed to the development of business process modeling standards.',
                            highlights=["Helped establish the group's workflow modeling benchmark."])],
       education=[Education(institution='Stanford University', url='https://www.stanford.edu', area='Computer Science',
                            studyType='PhD', startDate='2018-01-01', endDate='2022-01-01', score='GPA 3.8',
                            courses=['Workflow Management Systems', 'Business Process Modeling']),
                  Education(institution='University of California, Berkeley', url='https://www.berkeley.edu',
                            area='Computer Science', studyType='MS', startDate='2015-01-01', endDate='2016-01-01',
                            score='GPA 3.5', courses=['Workflow Management', 'Business Process Model'])],
       awards=[Award(title='Best Paper Award', date='2020-01-01', awarder='Academy of Computer Science',
                     summary='Best Paper Award')],
       certificates=[Certificate(name='Certified YAWL Administrator', date='2019-01-01',
                                 issuer='YAWL Server Management Certification Board', url=None)],
       publications=[Publication(name='YAWL Server Management', publisher='ACM Press', releaseDate='2020-01-01',
                                 url='https://dl.acm.org/citation.cfm?id=201005',
                                 summary='This paper discusses the design and implementation of a YAWL server.')],
       skills=[Skill(name='YAWL Server Management', level='expert',
                     keywords=['YAWL server configuration', 'workflow execution']),
               Skill(name='Business Process Modeling', level='advanced', keywords=['bpmn', 'workflow modeling'])],
       languages=[Language(language='English', fluency='fluent')],
       interests=[Interest(name='Workflow Management', keywords=['YAWL server management', 'workflow patterns']),
                  Interest(name='Business Process Modeling', keywords=['bpmn', 'workflow modeling'])],
       references=[Reference(name='Jane Doe', reference='Excellent PhD advisor.')],
       projects=[Project(name='YAWL Server Project', startDate='2019-01-01', endDate=None,
                         description='Designed and implemented a YAWL server for a large enterprise.',
                         highlights=['Successfully deployed YAWL server on AWS', 'Improved workflow efficiency by 30%'],
                         url=None), Project(name='Workflow Management System', startDate='2018-01-01', endDate=None,
                                            description='Developed a workflow management system using YAWL.',
                                            highlights=['Improved workflow execution efficiency by 25%',
                                                        'Reduced workflow errors by 50%'], url=None)])


async def main():
    # init_lm("groq/llama3-groq-70b-8192-tool-use-preview")
    # job_posting = DSLJobPosting.from_prompt("PhD with YAWL server experience. Verbose requirements.")
    resume = await instance(Resume, f"A resume that matches this job posting. \n{yawl_posting}")
    print(resume)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
