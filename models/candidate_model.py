from pydantic import BaseModel
from typing import List, Optional

class Education(BaseModel):
    degree: str
    specialization: str
    university: str
    year_of_passing: int

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    experience_years: int
    current_designation: str
    current_company: str
    education: List[Education]
    key_skills: List[str]
    total_experience: str
    preferred_location: str
    preferred_shift: str
    current_location: str
    notice_period_days: int
    expected_ctc: str
    current_ctc: str
    resume_pdf: str
