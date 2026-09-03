def compute_match_score(student_skills, internship_skills):
    if not internship_skills:
        return 0.0, []
    
    required_weight = 2.0
    preferred_weight = 1.0
    
    weighted_total = 0.0
    weighted_intersection = 0.0
    skills_gap = []
    student_set = set(student_skills)
    
    for skill_name, is_required in internship_skills:
        weight = required_weight if is_required else preferred_weight
        weighted_total += weight
        if skill_name in student_set:
            weighted_intersection += weight
        elif is_required:
            skills_gap.append(skill_name)
    
    if weighted_total == 0:
        return 0.0, skills_gap
    
    match_score = (weighted_intersection / weighted_total) * 100
    return round(match_score, 2), skills_gap


def is_eligible(match_score, threshold=50.0):
    return match_score >= threshold