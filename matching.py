EXPERIENCE_LEVELS = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
}


def normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def parse_skills(text: str) -> set[str]:
    return {normalize_skill(s) for s in text.split(",") if s.strip()}


def skill_score(student_skills: str, required_skills: str) -> float:
    required = parse_skills(required_skills)
    if not required:
        return 100.0
    student = parse_skills(student_skills)
    matched = student & required
    return len(matched) / len(required) * 100


def budget_score(task_budget: float, minimum_budget: float) -> float:
    if minimum_budget <= 0:
        return 100.0
    if task_budget >= minimum_budget:
        return 100.0
    return max(0.0, task_budget / minimum_budget * 100)


def availability_score(student_availability: str, task_schedule: str) -> float:
    if not task_schedule.strip():
        return 100.0
    available = {x.strip().lower() for x in student_availability.split(",") if x.strip()}
    wanted = {x.strip().lower() for x in task_schedule.split(",") if x.strip()}
    if not wanted:
        return 100.0
    if not available:
        return 0.0
    return len(available & wanted) / len(wanted) * 100


def experience_score(student_level: str, required_level: str) -> float:
    student = EXPERIENCE_LEVELS.get(student_level, 1)
    required = EXPERIENCE_LEVELS.get(required_level, 1)
    if student >= required:
        return 100.0
    if student == required - 1:
        return 70.0
    return 40.0


def rating_score(rating: float) -> float:
    if rating <= 0:
        return 70.0  # neutral score for new users
    return min(100.0, rating / 5 * 100)


def calculate_match(student: dict, task: dict) -> dict:
    """Calculate the weighted MicroIntern matching score."""
    parts = {
        "skill": skill_score(student.get("skills", ""), task.get("required_skills", "")),
        "budget": budget_score(float(task.get("budget", 0)), float(student.get("minimum_budget", 0))),
        "availability": availability_score(
            student.get("availability", ""), task.get("schedule", "")
        ),
        "experience": experience_score(
            student.get("experience", "Beginner"),
            task.get("experience", "Beginner"),
        ),
        "rating": rating_score(float(student.get("rating", 0))),
    }
    total = (
        parts["skill"] * 0.50
        + parts["budget"] * 0.20
        + parts["availability"] * 0.15
        + parts["experience"] * 0.10
        + parts["rating"] * 0.05
    )
    parts["total"] = round(total, 1)
    for key in list(parts):
        if key != "total":
            parts[key] = round(parts[key], 1)
    return parts
