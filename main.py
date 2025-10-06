import os
import glob
import csv
from dotenv import load_dotenv
from pdf_utils import extract_text_from_pdf
from text_cleaner import clean_resume_text, extract_sections
from embedding_utils import get_embedding, cosine_similarity
from llm_utils import generate_feedback, list_available_models, AVAILABLE_MODELS
from skill_extractor import extract_skills, SKILL_LIST
from visualization_utils import save_skill_venn, save_skill_bar
from report_utils import save_pdf_report, save_html_report
from ats_optimizer import ats_optimization_report, resume_format_suggestions
from interview_questions import generate_interview_questions

load_dotenv()

def get_resume_text(resume_path):
    file_ext = os.path.splitext(resume_path)[1].lower()
    if file_ext == ".pdf":
        return extract_text_from_pdf(resume_path)
    elif file_ext == ".txt":
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported resume file format! Please provide PDF or TXT.")

def get_user_model_choice():
    """Get user's choice of model provider and specific model"""
    list_available_models()
    
    print("\nChoose model provider:")
    print("1. Local (Ollama)")
    print("2. Groq API")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "1":
            provider = "local"
            print("\nAvailable local models:")
            for key in AVAILABLE_MODELS["local"].keys():
                print(f"  - {key}")
            break
        elif choice == "2":
            provider = "groq"
            print("\nAvailable Groq models:")
            for key in AVAILABLE_MODELS["groq"].keys():
                print(f"  - {key}")
            break
        else:
            print("Please enter 1 or 2")
    
    while True:
        model_key = input("Enter model key: ").strip()
        if model_key in AVAILABLE_MODELS[provider]:
            break
        else:
            print(f"Invalid model key. Available: {list(AVAILABLE_MODELS[provider].keys())}")
    
    return provider, model_key

def process_resume_vs_jd(resume_path, jd_path, provider, model_key, out_prefix="outputs"):
    resume_text = get_resume_text(resume_path)
    resume_clean_text = clean_resume_text(resume_text)
    with open(jd_path, "r", encoding="utf-8") as f:
        job_desc_clean = clean_resume_text(f.read())

    resume_embed = get_embedding(resume_clean_text)
    job_embed = get_embedding(job_desc_clean)
    overall_score = cosine_similarity(resume_embed, job_embed)

    resume_sections = extract_sections(resume_clean_text)
    jd_sections = extract_sections(job_desc_clean)
    tracked_sections = ["skills", "education", "project experience", "experience"]
    section_scores = {}
    for sec in tracked_sections:
        resume_val = resume_sections.get(sec, "")
        jd_val = jd_sections.get(sec, "")
        if not resume_val.strip():
            resume_val = resume_clean_text
        if not jd_val.strip():
            jd_val = job_desc_clean
        if resume_val.strip() and jd_val.strip():
            r_embed = get_embedding(resume_val)
            j_embed = get_embedding(jd_val)
            section_scores[sec] = cosine_similarity(r_embed, j_embed)
        else:
            section_scores[sec] = 0.0

    skills_resume = extract_skills(resume_clean_text)
    skills_jd = extract_skills(job_desc_clean)
    matched = skills_resume & skills_jd
    missing = skills_jd - skills_resume
    extra = skills_resume - skills_jd

    # ATS Optimization
    ats_composite, ats_keyword_coverage, ats_sections_found, ats_sections_missing, ats_issues, ats_report = ats_optimization_report(
        resume_clean_text, matched, skills_jd
    )
    print(ats_report)

    format_sugg = resume_format_suggestions(ats_sections_missing, ats_issues)

    feedback_prompt = f"""
Analyze this resume against the job description and provide detailed feedback.

RESUME:
{resume_clean_text}

JOB DESCRIPTION:
{job_desc_clean}

SIMILARITY SCORES:
- Overall Match: {overall_score:.3f}
- Skills Match: {section_scores.get('skills', 0):.3f}
- Education Match: {section_scores.get('education', 0):.3f}
- Experience Match: {section_scores.get('experience', 0):.3f}
- Project Experience Match: {section_scores.get('project experience', 0):.3f}

ATS OPTIMIZATION REPORT:
{ats_report}

Matched skills: {', '.join(sorted(matched))}
Missing (in JD, not in resume): {', '.join(sorted(missing))}
Extra (in resume, not in JD): {', '.join(sorted(extra))}

Please evaluate the resume and provide specific feedback for improvement.
"""

    print(f"Generating feedback using {provider} model: {model_key}")
    llm_feedback = generate_feedback(feedback_prompt, provider=provider, model_key=model_key)

    interview_qs = generate_interview_questions(
    resume_clean_text, job_desc_clean, provider=provider, model_key=model_key, num_questions=5
    )

    cand_id = os.path.splitext(os.path.basename(resume_path))[0]
    jd_id = os.path.splitext(os.path.basename(jd_path))[0]
    os.makedirs(out_prefix, exist_ok=True)
    pdf_report = f"{out_prefix}/{cand_id}__{jd_id}_report.pdf"
    html_report = f"{out_prefix}/{cand_id}__{jd_id}_report.html"
    venn_img = f"{out_prefix}/{cand_id}__{jd_id}_venn.png"
    bar_img = f"{out_prefix}/{cand_id}__{jd_id}_bar.png"
    save_skill_venn(skills_resume, skills_jd, venn_img)
    save_skill_bar(skills_resume, skills_jd, bar_img)

    def clean_text_for_pdf(text):
        replacements = {
            '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u00a0': ' ',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode('latin1', 'ignore').decode('latin1')

    save_pdf_report(
        pdf_report, clean_text_for_pdf(resume_clean_text), clean_text_for_pdf(job_desc_clean),
        section_scores, overall_score, clean_text_for_pdf(llm_feedback + "\n\n" + ats_report)
    )
    save_html_report(html_report, resume_clean_text, job_desc_clean, section_scores, overall_score, llm_feedback + "\n\n" + ats_report)

    # Return matrix row with ATS results
    return [
        os.path.basename(resume_path), os.path.basename(jd_path), provider, model_key,
        overall_score, section_scores.get("skills", 0.0),
        section_scores.get("education", 0.0),
        section_scores.get("project experience", 0.0),
        section_scores.get("experience", 0.0),
        ", ".join(sorted(matched)), ", ".join(sorted(missing)), ", ".join(sorted(extra)),
        ats_composite, ats_keyword_coverage, "|".join(ats_sections_found), "|".join(ats_sections_missing), "|".join(ats_issues),
        format_sugg,
        interview_qs,
        pdf_report
    ]


def main():
    resume_folder = "data/resumes"
    jd_folder = "data/jds"
    output_summary_path = "outputs/batch_matrix.csv"

    # Get user's model choice once for the batch
    provider, model_key = get_user_model_choice()
    print(f"\nUsing {provider} model: {model_key}")

    resume_files = glob.glob(f"{resume_folder}/*.*")
    jd_files = glob.glob(f"{jd_folder}/*.txt")

    matrix_headers = [
    "resume_filename", "jd_filename", "model_provider", "model_key",
    "overall_score", "skills_score", "education_score", "project_score", "experience_score",
    "matched_skills", "missing_skills", "extra_skills",
    "ats_composite_score", "ats_keyword_coverage",
    "ats_sections_found", "ats_sections_missing", "ats_format_issues",
    "interview_questions", "resume_format_suggestions",
    "report_path"
    ]      

    matrix_rows = []
    total = len(resume_files) * len(jd_files)
    count = 1

    for resume_path in resume_files:
        for jd_path in jd_files:
            print(f"\n[{count}/{total}] Resume: {os.path.basename(resume_path)} vs JD: {os.path.basename(jd_path)}")
            matrix_row = process_resume_vs_jd(resume_path, jd_path, provider, model_key, out_prefix="outputs")
            matrix_rows.append(matrix_row)
            count += 1

    # Save CSV matrix for all results
    with open(output_summary_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(matrix_headers)
        for row in matrix_rows:
            writer.writerow(row)
    print(f"\nMatching matrix saved: {output_summary_path}")

if __name__ == "__main__":
    main()
