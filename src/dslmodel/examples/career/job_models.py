from pydantic import Field
from typing import List, Optional
from dslmodel import DSLModel


class JobLocationModel(DSLModel):
    address: Optional[str] = Field(description="The individual's street address.")
    postalCode: Optional[str] = Field(description="The postal code for the individual's address.")
    city: Optional[str] = Field(description="The city where the individual resides.")
    countryCode: Optional[str] = Field(description="The country code where the individual resides.")
    region: Optional[str] = Field(description="The region or state where the individual resides.")


class JobProfileModel(DSLModel):
    network: str = Field(description="The name of the social or professional network.")
    username: str = Field(description="The individual's username on the network.")
    url: str = Field(description="A URL to the individual's profile on the network.")


class JobBasicsModel(DSLModel):
    name: str = Field(description="The full name of the individual.")
    label: Optional[str] = Field(description="The individual's professional label or title.")
    image: Optional[str] = Field(description="A URL pointing to an image of the individual.")
    email: str = Field(description="The individual's email address.")
    phone: Optional[str] = Field(description="The individual's phone number.")
    url: Optional[str] = Field(description="A URL to the individual's personal website.")
    summary: Optional[str] = Field(description="A short summary about the individual.")
    location: JobLocationModel = Field(description="The individual's location details.")
    profiles: List[JobProfileModel] = Field(description="A list of profiles on various networks.")


class JobWorkModel(DSLModel):
    name: str = Field(description="The name of the company.")
    position: str = Field(description="The individual's position or role at the company.")
    url: Optional[str] = Field(description="A URL to the company's website.")
    startDate: str = Field(description="The start date of the employment.")
    endDate: Optional[str] = Field(description="The end date of the employment.")
    summary: Optional[str] = Field(description="A short description of the individual's role.")
    highlights: List[str] = Field(description="A list of achievements or key highlights.")


class JobVolunteerModel(DSLModel):
    organization: str = Field(description="The name of the organization.")
    position: str = Field(description="The individual's position or role at the organization.")
    url: Optional[str] = Field(description="A URL to the organization's website.")
    startDate: str = Field(description="The start date of the volunteering activity.")
    endDate: Optional[str] = Field(description="The end date of the volunteering activity.")
    summary: Optional[str] = Field(description="A short description of the individual's role.")
    highlights: List[str] = Field(description="A list of key highlights during volunteering.")


class JobEducationModel(DSLModel):
    institution: str = Field(description="The name of the educational institution.")
    url: Optional[str] = Field(description="A URL to the institution's website.")
    area: str = Field(description="The field of study or major.")
    studyType: str = Field(description="The type of degree or certification.")
    startDate: str = Field(description="The start date of the educational period.")
    endDate: Optional[str] = Field(description="The end date of the educational period.")
    score: Optional[str] = Field(description="The individual's score or GPA.")
    courses: List[str] = Field(description="A list of courses taken by the individual.")


class JobAwardModel(DSLModel):
    title: str = Field(description="The title of the award.")
    date: str = Field(description="The date the award was given.")
    awarder: str = Field(description="The entity that awarded the recognition.")
    summary: Optional[str] = Field(description="A brief description of the award.")


class JobCertificateModel(DSLModel):
    name: str = Field(description="The name of the certificate.")
    date: str = Field(description="The date the certificate was issued.")
    issuer: str = Field(description="The entity that issued the certificate.")
    url: Optional[str] = Field(description="A URL to more information about the certificate.")


class JobPublicationModel(DSLModel):
    name: str = Field(description="The name of the publication.")
    publisher: str = Field(description="The name of the entity that published the work.")
    releaseDate: str = Field(description="The release date of the publication.")
    url: Optional[str] = Field(description="A URL to the publication.")
    summary: Optional[str] = Field(description="A short description of the publication.")


class JobSkillModel(DSLModel):
    name: str = Field(description="The name of the skill.")
    level: Optional[str] = Field(description="The individual's proficiency level in the skill.")
    keywords: List[str] = Field(description="A list of keywords related to the skill.")


class JobLanguageModel(DSLModel):
    language: str = Field(description="The name of the language.")
    fluency: Optional[str] = Field(description="The individual's fluency level in the language.")


class JobInterestModel(DSLModel):
    name: str = Field(description="The name of the interest or hobby.")
    keywords: List[str] = Field(description="A list of keywords related to the interest.")


class JobReferenceModel(DSLModel):
    name: str = Field(description="The name of the reference person.")
    reference: str = Field(description="A reference description provided by the person.")


class JobProjectModel(DSLModel):
    name: str = Field(description="The name of the project.")
    startDate: str = Field(description="The start date of the project.")
    endDate: Optional[str] = Field(description="The end date of the project.")
    description: str = Field(description="A short description of the project.")
    highlights: List[str] = Field(description="A list of achievements or key highlights of the project.")
    url: Optional[str] = Field(description="A URL to the project.")

def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    from dslmodel.readers.doc_reader import DocReader
    drt = DocReader(path="/Users/sac/Downloads/consulting-contract.pdf")
    print(drt.forward())



if __name__ == '__main__':
    main()
