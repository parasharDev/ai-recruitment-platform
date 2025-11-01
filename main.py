from fastapi import FastAPI
from routes.candidate_routes import router as candidate_router
from routes.interview_scheduling import router as interview_router  

app = FastAPI(title="AI Hiring Assistant Backend")

# Route registration
app.include_router(candidate_router, prefix="/api")
app.include_router(interview_router, prefix="/api")  

@app.get("/")
def root():
    return {"message": "Welcome to AI Hiring Assistant Backend"}
