from groq import Groq
import os

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_explanation(candidate: dict, jd_text: str, score: float) -> str:
    """
    Generate textual explanation for why candidate matches JD
    """
    prompt = f"""
    Job Description: {jd_text}
    Candidate Name: {candidate['name']}
    Candidate Skills: {', '.join(candidate['key_skills'])}
    Candidate Experience: {candidate['experience_years']} years
    Candidate Location: {candidate['preferred_location']}
    Overall similarity score: {round(score*100,2)}%
    
    Generate a concise explanation (2-3 lines) why this candidate matches the JD.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq generation failed:", e)
        explanation = f"{candidate['name']} has skills {', '.join(candidate['key_skills'])} and {candidate['experience_years']} years experience. Similarity score: {round(score*100,2)}%."
    return explanation
