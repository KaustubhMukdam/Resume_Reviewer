import re

ATS_SECTIONS = [
    "contact", "education", "skills", "experience", "project", "certificat", "about"
]

ATS_BAD_FORMATTING = [
    r'\|\|',   # tables (pipes)
    r'<table', # html table tag
    r'{|}',    # curly braces (break some ATS)
]

BULLET_SYMBOLS = ['•', '◦', '●', '○', '▪', '–', '—']

def ats_section_coverage(resume_text):
    found, missing = [], []
    lower_text = resume_text.lower()
    for sec in ATS_SECTIONS:
        if re.search(sec, lower_text):
            found.append(sec)
        else:
            missing.append(sec)
    return found, missing

def ats_bad_formatting_score(resume_text):
    issues = []
    for regex in ATS_BAD_FORMATTING:
        if re.search(regex, resume_text):
            issues.append(regex)
    for b in BULLET_SYMBOLS:
        if b in resume_text:
            issues.append(f"Bullet symbol: {repr(b)}")
    return issues

def ats_keyword_score(matched_skills, jd_skills):
    if len(jd_skills) == 0:
        return 0.0
    return len(matched_skills) / len(jd_skills)

def ats_optimization_report(resume_clean, matched_skills, jd_skills):
    sections_found, sections_missing = ats_section_coverage(resume_clean)
    bad_format_issues = ats_bad_formatting_score(resume_clean)
    keyword_score = ats_keyword_score(matched_skills, jd_skills)
    composite = (keyword_score * 0.6) + (len(sections_found) / len(ATS_SECTIONS)) * 0.3 - (len(bad_format_issues) * 0.1)
    composite = max(min(composite, 1.0), 0.0)

    report = f"""ATS Optimization:
------------------------------
ATS Skill Coverage: {keyword_score*100:.1f}%
Sections Present: {sections_found}
Sections Missing: {sections_missing}
Formatting Issues/Warnings: {bad_format_issues}
ATS-Readability Score (0-1): {composite:.2f}
------------------------------
"""
    return composite, keyword_score, sections_found, sections_missing, bad_format_issues, report

def resume_format_suggestions(sections_missing, format_issues):
    suggestions = []
    if sections_missing:
        suggestions.append("Add missing sections: " + ", ".join(sections_missing))

    for issue in format_issues:
        if 'Bullet symbol' in issue:
            suggestions.append("Replace fancy bullet symbols (•, –, etc) with plain '-' or '*' for maximum ATS compatibility.")
        elif '<table' in issue or '||' in issue:
            suggestions.append("Avoid tables/layout images—use simple text and bullet points.")
        elif '{|}' in issue:
            suggestions.append("Remove curly braces and table markup from the resume text.")
        else:
            suggestions.append(f"Check formatting: {issue}")
    if not suggestions:
        suggestions.append("No major formatting issues detected. Resume is ATS-friendly!")
    return "\n".join(suggestions)
