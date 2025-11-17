# from groq import Groq
# import os

# # Initialize Groq client
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

from services.llm_service import client

def generate_explanation(candidate: dict, jd_text: str, score: float) -> str:
    """
    Generate textual explanation for why candidate matches JD
    """
    prompt = f"""
    You are an AI recruitment assistant. Your job is to evaluate how well a candidate fits a job description.

    Job Description: {jd_text}
    Candidate Name: {candidate['name']}
    Candidate Skills: {', '.join(candidate['key_skills'])}
    Candidate Experience: {candidate['experience_years']} years
    Candidate Location: {candidate['preferred_location']}
    Overall similarity score: {round(score*100,2)}%
    
    Write a short, recruiter-friendly explanation (2–3 lines max) focusing on:
    1. Key skill overlap between JD and candidate
    2   . Fit based on experience level
    3  . Any standout strengths making them a strong match

    Do NOT repeat the job description.  
    Do NOT be generic.  
    Return only the explanation.
    """
    try:
        # response = groq_client.chat.completions.create(
        #     model="llama-3.3-70b-versatile",
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=100,
        #     temperature=0.3
        # )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3,
            # top_p=1.0,
            # deployment="gpt-4o-mini",
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        print("Azure generation failed:", e)
        explanation = f"{candidate['name']} has skills {', '.join(candidate['key_skills'])} and {candidate['experience_years']} years experience. Similarity score: {round(score*100,2)}%."
    return explanation
