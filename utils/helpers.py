from datetime import datetime, date
from utils.colors import SUBJECT_COLORS, GREEN, BLUE, ACCENT, PURPLE, RED


def days_left(date_str):
    try:
        exam_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (exam_date - date.today()).days
        if delta < 0:  return "Past"
        if delta == 0: return "Today!"
        return f"{delta}d left"
    except Exception:
        return "?"


def subject_color(s):
    return SUBJECT_COLORS.get(s, (0.4, 0.4, 0.4, 1.0))


def compute_gwa(written, performance, exam):
    try:
        return round(float(written) * 0.25 + float(performance) * 0.50 + float(exam) * 0.25, 1)
    except Exception:
        return 0.0


def grade_remark(g):
    if g >= 90: return ("Outstanding",         GREEN)
    if g >= 85: return ("Very Satisfactory",   BLUE)
    if g >= 80: return ("Satisfactory",        ACCENT)
    if g >= 75: return ("Fairly Satisfactory", PURPLE)
    return ("Did Not Meet", RED)