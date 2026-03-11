import json
import os
from kivy.app import App

DATA_FILE = None

DEFAULT_SCHEDULE = {
    "Monday":    [["7:00 AM","Mathematics","Room 204"],["9:00 AM","English","Room 112"],["1:00 PM","Physics","Lab 3"]],
    "Tuesday":   [["8:00 AM","History","Room 305"],["10:00 AM","P.E.","Gym"],["2:00 PM","Chemistry","Lab 1"]],
    "Wednesday": [["7:00 AM","Mathematics","Room 204"],["9:00 AM","Filipino","Room 110"],["11:00 AM","MAPEH","Room 201"]],
    "Thursday":  [["8:00 AM","English","Room 112"],["10:00 AM","TLE","Lab 2"],["1:00 PM","Science","Lab 1"]],
    "Friday":    [["7:00 AM","Physics","Lab 3"],["9:00 AM","Values Ed","Room 302"],["2:00 PM","Free Period","Library"]],
    "Saturday":  [],
    "Sunday":    [],
}

DEFAULT_EXAMS = [
    {"id":1,"subject":"Mathematics","type":"Long Quiz","date":"2026-03-10","notes":"Chapters 5-7","done":False},
    {"id":2,"subject":"Physics","type":"Lab Exam","date":"2026-03-12","notes":"Optics & Waves","done":False},
    {"id":3,"subject":"English","type":"Essay","date":"2026-03-15","notes":"Literary analysis","done":False},
    {"id":4,"subject":"Chemistry","type":"Unit Test","date":"2026-03-18","notes":"Periodic Table","done":False},
    {"id":5,"subject":"History","type":"Recitation","date":"2026-03-07","notes":"World War II","done":True},
]

DEFAULT_TODOS = [
    {"id":1,"text":"Finish Math homework","done":False,"priority":"high"},
    {"id":2,"text":"Read Chapter 8 of English","done":False,"priority":"medium"},
    {"id":3,"text":"Submit lab report","done":True,"priority":"high"},
    {"id":4,"text":"Study for Physics quiz","done":False,"priority":"high"},
    {"id":5,"text":"Print History assignment","done":False,"priority":"low"},
]

DEFAULT_GRADES = [
    {"id":1,"subject":"Mathematics","written":88,"performance":90,"exam":85},
    {"id":2,"subject":"English","written":92,"performance":88,"exam":90},
    {"id":3,"subject":"Physics","written":80,"performance":85,"exam":78},
    {"id":4,"subject":"Chemistry","written":75,"performance":80,"exam":72},
    {"id":5,"subject":"History","written":95,"performance":92,"exam":94},
]


def get_data_file():
    global DATA_FILE
    if DATA_FILE is None:
        try:
            app = App.get_running_app()
            DATA_FILE = os.path.join(app.user_data_dir, "student_data.json")
        except Exception:
            DATA_FILE = "student_data.json"
    return DATA_FILE


def load_data():
    path = get_data_file()
    if os.path.exists(path):
        try:
            with open(path) as f:
                d = json.load(f)
            if "grades"   not in d: d["grades"]   = [dict(g) for g in DEFAULT_GRADES]
            if "schedule" not in d: d["schedule"]  = {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()}
            for day in d["schedule"]:
                d["schedule"][day] = [list(i) for i in d["schedule"][day]]
            return d
        except Exception as e:
            print(f"[LOAD] Error: {e}")
    return {
        "exams":    [dict(e) for e in DEFAULT_EXAMS],
        "todos":    [dict(t) for t in DEFAULT_TODOS],
        "grades":   [dict(g) for g in DEFAULT_GRADES],
        "schedule": {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()},
    }


def save_data(data):
    try:
        path = get_data_file()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[SAVE] OK → {path}")
    except Exception as e:
        print(f"[SAVE] Error: {e}")