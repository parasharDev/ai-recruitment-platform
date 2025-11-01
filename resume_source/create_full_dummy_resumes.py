from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import json

# Path to candidates JSON (in the same folder as this script)
json_path = os.path.join(os.path.dirname(__file__), "CandidateData.json")

with open(json_path, "r") as f:
    candidates = json.load(f)

# Output folder for PDFs (relative to project root)
output_dir = os.path.join(os.path.dirname(__file__), "../uploads/resumes")
os.makedirs(output_dir, exist_ok=True)

for candidate in candidates:
    file_name = candidate["resume_pdf"].split("/")[-1]
    pdf_path = os.path.join(output_dir, file_name)
    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Resume - {candidate['name']}")

    # Candidate Info
    c.setFont("Helvetica", 12)
    y = 770
    c.drawString(100, y, f"Email: {candidate['email']}")
    y -= 20
    c.drawString(100, y, f"Phone: {candidate['phone']}")
    y -= 20
    c.drawString(100, y, f"Current Designation: {candidate['current_designation']}")
    y -= 20
    c.drawString(100, y, f"Current Company: {candidate['current_company']}")
    y -= 20
    c.drawString(100, y, f"Total Experience: {candidate['total_experience']} ({candidate['experience_years']} years)")
    y -= 20
    c.drawString(100, y, f"Preferred Location: {candidate['preferred_location']}")
    y -= 20
    c.drawString(100, y, f"Preferred Shift: {candidate['preferred_shift']}")
    y -= 20
    c.drawString(100, y, f"Current Location: {candidate['current_location']}")
    y -= 20
    c.drawString(100, y, f"Notice Period: {candidate['notice_period_days']} days")
    y -= 20
    c.drawString(100, y, f"Current CTC: {candidate['current_ctc']} | Expected CTC: {candidate['expected_ctc']}")
    y -= 30

    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Education:")
    y -= 20
    c.setFont("Helvetica", 12)
    for edu in candidate["education"]:
        c.drawString(120, y, f"{edu['degree']} in {edu['specialization']} - {edu['university']} ({edu['year_of_passing']})")
        y -= 20

    y -= 10
    # Key Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Key Skills:")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(120, y, ", ".join(candidate["key_skills"]))

    # Save PDF
    c.save()

print("✅ All candidate PDFs generated in uploads/resumes/")
