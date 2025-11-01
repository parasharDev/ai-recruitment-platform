from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb+srv://gparashar222:GEfI9kZVCsVNVSnw@cluster0.rhcgws5.mongodb.net/"
client = MongoClient(MONGO_URI)
# Database and collection
db = client["ai_hiring_assistant"]
candidates_collection = db["resumes"]
