from services.llm_service import client, model_name

def generate_jd(skills: str, exp: str, loc: str, notice: str, extra: str) -> str:
    """Generate a professional Job Description using Azure OpenAI."""

    prompt = f"""
Generate a professional Job Description based on the following inputs:

Skills: {skills}
Experience Required: {exp} years
Location: {loc}
Notice Period: {notice if notice else "Not specified"}
Additional Information: {extra if extra else "None"}

Return ONLY the following JSON structure:

{{
  "description": "1 paragraph summary of the role",
  "responsibilities": ["bullet 1", "bullet 2", "bullet 3", ...],
  "required_skills": ["skill 1", "skill 2", ...],
  "preferred_skills": ["skill 1", "skill 2", ...]
}}

Rules:
- Use proper JSON (no trailing commas, no markdown).
- Do NOT wrap JSON in code blocks.
- Do NOT include extra text.
- Use short bullet items.
- Make it like a LinkedIn job posting.
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500
        )

        jd_text = response.choices[0].message.content
        return jd_text.strip()

    except Exception as e:
        print("JD generation error:", e)
        return "Error generating JD. Please try again."
