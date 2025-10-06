from llm_utils import generate_feedback

def generate_interview_questions(resume_text, jd_text, provider="local", model_key="llama3", num_questions=5):
    prompt = f"""
Given the resume below and job description below, write {num_questions} highly relevant, technical, and practical interview questions for this candidate (avoid generic HR questions).

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return only an enumerated list of questions.
"""
    response = generate_feedback(prompt, provider=provider, model_key=model_key)
    # Clean: Only keep bullet/numbered lines
    questions = [line for line in response.split('\n') if line.strip() and line[0].isdigit()]
    if not questions:
        questions = [line for line in response.split('\n') if '?' in line]
    return "\n".join(questions) if questions else response
