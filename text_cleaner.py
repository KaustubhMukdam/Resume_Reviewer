import re

def clean_resume_text(raw_text):
    """
    Cleans and normalizes extracted resume text for downstream NLP tasks.
    - Removes duplicated line breaks.
    - Normalizes section headers.
    - Removes unwanted artifacts/emails/URLs.
    - Optionally parses education, skills, projects, etc.
    """

    # Remove excessive line breaks
    text = re.sub(r"\n{2,}", "\n", raw_text)

    # Remove obvious contact links (keep info elsewhere)
    text = re.sub(r"http\S+|www\S+|mailto:\S+", "", text)

    # Normalize section headers, e.g., Education, Skills, Projects
    section_patterns = [
        r"(?i)(Education)",
        r"(?i)(Skills)",
        r"(?i)(Project Experience)",
        r"(?i)(About Me)",
        r"(?i)(Certificat(e|ion)s?)",
        r"(?i)(Contact)",
    ]
    for pattern in section_patterns:
        text = re.sub(pattern, lambda m: f"\n=== {m.group(0).upper()} ===\n", text)
    
    # Remove common artifacts, e.g., "Hours Completed: ..."
    text = re.sub(r"Hours Completed:\s*\d+\s*hrs?", "", text)

    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text

def extract_sections(text):
    """
    Extracts main sections (Education, Skills, Projects, Experience, etc.)
    Returns a dict with section names as keys and their text as values.
    """
    # Pattern looks for our cleaned section headers
    split_pattern = re.compile(r"=== ([A-Z\s]+) ===")
    parts = split_pattern.split(text)
    
    sections = {}
    for i in range(1, len(parts), 2):
        header = parts[i].strip().lower()
        content = parts[i+1].strip() if (i+1) < len(parts) else ""
        sections[header] = content
    return sections

# Example usage
if __name__ == "__main__":
    dummy_resume = """
    === EDUCATION ===
    B.Tech in Computer Engineering ...
    === SKILLS ===
    Python, Java, ...
    === PROJECT EXPERIENCE ===
    Built an AI-powered tool ...
    """
    print(extract_sections(dummy_resume))  # {'education': 'B.Tech...', 'skills': 'Python, Java,...', ...}

# Example usage:
if __name__ == "__main__":
    raw = "...your extracted raw resume text..."
    print(clean_resume_text(raw))
