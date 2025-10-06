from fpdf import FPDF

def save_pdf_report(path, resume_text, job_desc, section_scores, overall_score, llm_feedback):
    # Clean text to handle unicode characters
    def clean_text_for_pdf(text):
        # Replace common unicode characters
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '--', # em dash  
            '\u2018': "'",  # left single quote
            '\u2019': "'",  # right single quote
            '\u201c': '"',  # left double quote
            '\u201d': '"',  # right double quote
            '\u2022': '*',  # bullet point
            '\u00a0': ' ',  # non-breaking space
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Remove any remaining non-latin1 characters
        return text.encode('latin1', 'ignore').decode('latin1')
    
    # Clean all input texts
    resume_text = clean_text_for_pdf(resume_text)
    job_desc = clean_text_for_pdf(job_desc)
    llm_feedback = clean_text_for_pdf(llm_feedback)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, "Resume Reviewer Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Resume (Extracted & Cleaned):", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, resume_text)
    pdf.ln(5)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Job Description:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, job_desc)
    pdf.ln(5)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Section-wise Similarity Scores:", ln=True)
    pdf.set_font("Arial", size=11)
    for sec, sc in section_scores.items():
        pdf.cell(0, 8, f"{sec.capitalize():<20}: {sc:.3f}", ln=True)
    pdf.cell(0, 8, f"{'Overall':<20}: {overall_score:.3f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "AI-Powered Feedback:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, llm_feedback)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Skill Gap Visualizations", ln=True)
    pdf.image("outputs/skill_venn.png", w=100)
    pdf.image("outputs/skill_bar.png", w=100)

    pdf.output(path)

def save_html_report(path, resume_text, job_desc, section_scores, overall_score, llm_feedback):
    html = "<html><head><title>Resume Reviewer Report</title></head><body>"
    html += "<h2>Resume Reviewer Report</h2>"

    html += "<h3>Resume (Extracted & Cleaned):</h3><pre>{}</pre>".format(resume_text)
    html += "<h3>Job Description:</h3><pre>{}</pre>".format(job_desc)
    html += "<h3>Section-wise Similarity Scores:</h3><ul>"
    for sec, sc in section_scores.items():
        html += "<li><b>{}</b>: {:.3f}</li>".format(sec.capitalize(), sc)
    html += "<li><b>Overall</b>: {:.3f}</li>".format(overall_score)
    html += "</ul>"
    html += "<h3>AI-Powered Feedback:</h3><pre>{}</pre>".format(llm_feedback)
    html += "</body></html>"
    html += '<img src="outputs/skill_venn.png">'
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
