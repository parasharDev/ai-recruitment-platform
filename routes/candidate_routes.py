import os
import shutil
from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer
from database.connection import candidates_collection
from models.candidate_model import Candidate
from models.job_model import JobDescription
from utils.embeddings import embed_text, cosine_similarity
from utils.explanation import generate_explanation
from utils.pdf_parser import parse_pdf
from fastapi import HTTPException
import traceback

# Imports for temporary Vector DB (RAG)
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
import numpy as np
import traceback
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from groq import Groq
import os


router = APIRouter()

@router.get("/candidates")
def get_all_candidates():
    candidates = list(candidates_collection.find({}, {"_id": 0}))
    return {"total": len(candidates), "data": candidates}

@router.get("/candidate/{id}")
def get_candidate(id: str):
    candidate = candidates_collection.find_one({"_id": id}, {"_id": 0})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# <---Cosine Scoring--->
@router.post("/ai_score_candidates/cosine_scoring")
def ai_score_candidates(jd: JobDescription):
    candidates = list(candidates_collection.find())
    # Embeding JD text
    jd_embedding = embed_text(jd.jd_text)
    scored_candidates = []
    for candidate in candidates:
        pdf_path = candidate.get("resume_pdf")  # should contain path like "uploads/resumes/rahul_sharma.pdf"
        print("path",pdf_path)
        resume_text = ""
        if pdf_path and os.path.exists(pdf_path):
            print('pdf')
            #parsing pdf
            resume_text = parse_pdf(pdf_path)
        if not resume_text:
            print('hardcode')
            resume_text = " ".join(candidate["key_skills"]) + " " + candidate["current_designation"]

    # Embed resume text
        candidate_embedding = embed_text(resume_text)

    # Comparing score
        score = cosine_similarity(jd_embedding, candidate_embedding)

    # Generating explanation by LLM
        explanation = generate_explanation(candidate, jd.jd_text, score)

        scored_candidates.append({
            "candidate_id": str(candidate["_id"]),
            "name": candidate["name"],
            "email": candidate["email"],
            "phone": candidate["phone"],
            "total_score": round(float(score), 4),
            "explanation": explanation
        })

    scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)
    return {"ranked_candidates": scored_candidates}



# <---Vector DB Scoring--->
@router.post("/ai_score_candidates/vectordb_scoring")
def ai_score_candidates(jd: JobDescription):
    try:
        print("🔹 Starting candidate scoring...")
        candidates = list(candidates_collection.find())
        VECTOR_DB_PATH = "temp_vector_store"
        if os.path.exists(VECTOR_DB_PATH):
            shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)

        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2",encode_kwargs={"normalize_embeddings": True})
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

        docs = []
 
        # Processong all candidate resumes
        for candidate in candidates:
            pdf_path = candidate.get("resume_pdf")
            resume_text = ""
            if pdf_path and os.path.exists(pdf_path):
                print(f"📄 Parsing PDF: {pdf_path}")
                resume_text = parse_pdf(pdf_path)
            if not resume_text:
                resume_text = " ".join(candidate["key_skills"]) + " " + candidate["current_designation"]

            chunks = text_splitter.create_documents(
                [resume_text],
                metadatas=[{
                    "name": candidate["name"],
                    "email": candidate["email"],
                    "phone": candidate["phone"],
                    "id": str(candidate["_id"])
                }]
            )
            docs.extend(chunks)

        if not docs:
            raise HTTPException(status_code=400, detail="No candidate documents available")

        # Creating temporary Chroma vector store
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding_function,
            persist_directory=VECTOR_DB_PATH,
            collection_metadata={"hnsw:space": "cosine"}
        )

        # Using similarity search with scores (built-in Chroma score)
        relevant_docs_with_scores = vectorstore.similarity_search_with_score(jd.jd_text, k=5)

        scored_candidates = []
        for doc, score in relevant_docs_with_scores:
            metadata = doc.metadata
            candidate = next((c for c in candidates if str(c["_id"]) == metadata["id"]), None)
            if not candidate:
                continue

            # Using Chroma’s internal similarity score instead of manual cosine
            # normalized_score = 1 / (1 + score) 
            normalized_score = 50 + 50 * max(0, 1 - score) 
            explanation = generate_explanation(candidate, jd.jd_text, normalized_score)

            scored_candidates.append({
                "candidate_id": str(candidate["_id"]),
                "name": candidate["name"],
                "email": candidate["email"],
                "phone": candidate["phone"],
                "total_score": round(normalized_score, 4),
                "explanation": explanation
            })

        scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)
        shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)
        return {"ranked_candidates": scored_candidates}

    except Exception as e:
        print("ERROR during candidate scoring:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# <---LLM Scroring--->
@router.post("/ai_score_candidates/llm_scoring")
def ai_score_candidates(jd: JobDescription):
    try:
        print("Starting candidate scoring...")
        candidates = list(candidates_collection.find())

        VECTOR_DB_PATH = "temp_vector_store"
        if os.path.exists(VECTOR_DB_PATH):
            shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)

        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)

        docs = []

        for candidate in candidates:
            pdf_path = candidate.get("resume_pdf")
            resume_text = ""
            if pdf_path and os.path.exists(pdf_path):
                print(f"Parsing PDF: {pdf_path}")
                resume_text = parse_pdf(pdf_path)
            if not resume_text:
                resume_text = " ".join(candidate["key_skills"]) + " " + candidate["current_designation"]

            chunks = text_splitter.create_documents(
                [resume_text],
                metadatas=[{
                    "name": candidate["name"],
                    "email": candidate["email"],
                    "phone": candidate["phone"],
                    "id": str(candidate["_id"]),
                    "skills": ", ".join(candidate.get("key_skills", [])),
                    "experience": candidate.get("experience", 0)
                }]
            )
            docs.extend(chunks)

        if not docs:
            raise HTTPException(status_code=400, detail="No candidate documents available")

        # Create vector store and fetch relevant chunks with scores
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding_function,
            persist_directory=VECTOR_DB_PATH
        )
        relevant_docs = vectorstore.similarity_search_with_score(jd.jd_text, k=3)  # returns (Document, score)

        # Initialize LLM for semantic scoring
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )

        prompt_template = PromptTemplate.from_template("""
        You are an expert recruiter.
        Compare the following candidate resume to the job description.
        Job Description:
        {jd_text}

        Candidate Resume:
        {resume_text}

        Score the match on a scale of 0 to 1 (1 = perfect match) and explain briefly.
        Respond in JSON format: {{"score": <float>, "reason": "<string>"}}
        """)

        scored_candidates = []

        for doc, retrieval_score in relevant_docs:
            metadata = doc.metadata
            candidate = next((c for c in candidates if str(c["_id"]) == metadata["id"]), None)
            if not candidate:
                continue

            # Get LLM-based semantic score
            formatted_prompt = prompt_template.format(jd_text=jd.jd_text, resume_text=doc.page_content)
            llm_response = llm.invoke(formatted_prompt).content
            try:
                result = json.loads(llm_response)
                llm_score = float(result.get("score", 0.0))
                explanation = result.get("reason", "")
            except:
                llm_score = 0.0
                explanation = llm_response.strip()

            # Metadata score (rule-based)
            skills = candidate.get("key_skills", [])
            exp = candidate.get("experience", 0)
            metadata_score = 0.0
            if any(keyword.lower() in jd.jd_text.lower() for keyword in skills):
                metadata_score += 0.05
            if exp >= 3:
                metadata_score += 0.05  # Example: add points for decent experience

            # Normalize retrieval score (since vector DB gives negative distance sometimes)
            retrieval_score = max(0.0, min(1.0, retrieval_score))

            # 🆕 Final weighted score
            final_score = (
                0.5 * retrieval_score +
                0.4 * llm_score +
                0.1 * metadata_score
            )

            scored_candidates.append({
                "candidate_id": str(candidate["_id"]),
                "name": candidate["name"],
                "email": candidate["email"],
                "phone": candidate["phone"],
                "retrieval_score": round(retrieval_score, 4),
                "llm_score": round(llm_score, 4),
                "metadata_score": round(metadata_score, 4),
                "total_score": round(final_score, 4),
                "explanation": explanation
            })

        # Sorting by descending total score
        scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)

        # Cleanup
        shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)

        return {"ranked_candidates": scored_candidates}

    except Exception as e:
        print("❌ ERROR during candidate scoring:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))