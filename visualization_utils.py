import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import os

def save_skill_venn(skills_resume, skills_jd, out_path):
    plt.figure(figsize=(5, 5))
    venn_diagram = venn2([set(skills_resume), set(skills_jd)], set_labels=("Resume", "Job Description"))
    plt.title("Skills Overlap: Resume vs JD")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def save_skill_bar(skills_resume, skills_jd, out_path):
    matched = set(skills_resume).intersection(set(skills_jd))
    missing = set(skills_jd) - set(skills_resume)
    extra = set(skills_resume) - set(skills_jd)
    categories = ['Matched', 'Missing', 'Extra']
    values = [len(matched), len(missing), len(extra)]
    plt.figure(figsize=(6, 4))
    plt.bar(categories, values, color=['green', 'red', 'orange'])
    plt.title('Skill Gap Analysis')
    plt.ylabel('Number of Skills')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return matched, missing, extra
