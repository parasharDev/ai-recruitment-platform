from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.candidate_routes import router as candidate_router
from routes.interview_scheduling import router as interview_router  
from routes.web_hook import router as web_hook
from routes.whatsapp_send import router as whatsapp_send

from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="AI Hiring Assistant Backend")

origins = [
    "http://localhost:5173",      # Vite dev
    "http://127.0.0.1:5173",      # Vite alternative
    "http://localhost:3000",      # React alternative
    "http://127.0.0.1:3000",
    "*",                           # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] for full dev freedom
    allow_credentials=True,
    allow_methods=["*"],            # VERY IMPORTANT → allows OPTIONS
    allow_headers=["*"],            # Allow all headers
)

# Route registration
app.include_router(candidate_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(web_hook, prefix="/api")
app.include_router(whatsapp_send, prefix="/api")     

@app.get("/")
def root():
    return {"message": "Welcome to AI Hiring Assistant Backend"}
