from fastapi import FastAPI
from routes.candidate_routes import router as candidate_router
from routes.interview_scheduling import router as interview_router  
from routes.web_hook import router as web_hook
from routes.whatsapp_send import router as whatsapp_send

app = FastAPI(title="AI Hiring Assistant Backend")

# Route registration
app.include_router(candidate_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(web_hook, prefix="/api")
app.include_router(whatsapp_send, prefix="/api")     

@app.get("/")
def root():
    return {"message": "Welcome to AI Hiring Assistant Backend"}
