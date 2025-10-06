import spacy

# Predefined dictionary of high-confidence AI/ML/tech skills
SKILL_LIST = [
    "python", "java", "c++", "tensorflow", "pytorch", "scikit-learn", "keras", "sql", "nosql", "aws", "gcp", "azure",
    "docker", "kubernetes", "linux", "pandas", "numpy", "opencv", "huggingface", "transformers",
    "langchain", "groq", "mlops", "deep learning", "machine learning", "data preprocessing", "cloud", "nlp",
    "llm", "git", "ci/cd", "html", "css", "javascript", "power bi", "excel", "rest api", "flask", "django"
]

nlp = spacy.load("en_core_web_lg")  # load Spacy model once

def extract_skills(text, custom_skills=SKILL_LIST):
    """
    Extract skills/technologies from text using matching against a curated list.
    Returns a set of found skills (case-insensitive).
    """
    text_lower = text.lower()
    doc = nlp(text_lower)
    found_skills = set()

    # Token based matches
    for skill in custom_skills:
        skill_term = skill.lower()
        # Check for whole word/phrase in text
        if skill_term in text_lower:
            found_skills.add(skill_term)
        # Check for multi-token phrase in noun chunks
        for chunk in doc.noun_chunks:
            if skill_term in chunk.text.lower():
                found_skills.add(skill_term)
    return found_skills
