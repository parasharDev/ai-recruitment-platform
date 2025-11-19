from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.jd_generator import generate_jd

router = APIRouter()

class JDRequest(BaseModel):
    skills: str
    exp: str
    loc: str
    notice: str = ""
    extra: str = ""

@router.post("/ai/generate_jd")
async def generate_jd_api(req: JDRequest):
    try:
        jd = generate_jd(req.skills, req.exp, req.loc, req.notice, req.extra)
        return {"jd_text": jd}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
