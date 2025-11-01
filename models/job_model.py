from pydantic import BaseModel

class JobDescription(BaseModel):
    jd_text: str  # free-text string
