import sqlite3
from pathlib import Path
from datetime import datetime
from security import hash_password

DB_PATH = Path(__file__).with_name("microintern.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('student','business')),
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                skills TEXT DEFAULT '',
                availability TEXT DEFAULT '',
                minimum_budget REAL DEFAULT 0,
                experience TEXT DEFAULT 'Beginner',
                rating REAL DEFAULT 0,
                jobs_completed INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS businesses (
                user_id INTEGER PRIMARY KEY,
                industry TEXT DEFAULT '',
                description TEXT DEFAULT '',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT NOT NULL,
                budget REAL NOT NULL,
                deadline TEXT NOT NULL,
                schedule TEXT DEFAULT '',
                experience TEXT DEFAULT 'Beginner',
                status TEXT NOT NULL DEFAULT 'Open',
                assigned_student_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(business_id) REFERENCES users(id),
                FOREIGN KEY(assigned_student_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                match_score REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL,
                UNIQUE(task_id, student_id),
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY(student_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL UNIQUE,
                gross REAL NOT NULL,
                platform_fee REAL NOT NULL,
                student_earnings REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL UNIQUE,
                business_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                score REAL NOT NULL,
                comment TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(business_id) REFERENCES users(id),
                FOREIGN KEY(student_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS student_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                cover_image TEXT DEFAULT '',
                live_url TEXT DEFAULT '',
                repo_url TEXT DEFAULT '',
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS project_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                student_id INTEGER NOT NULL REFERENCES users(id),
                sender_id INTEGER NOT NULL REFERENCES users(id),
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                read_at TEXT DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS project_messages_thread
                ON project_messages(task_id,student_id,id);
        """)
        student_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(students)")
        }
        profile_fields = {
            "headline": "TEXT DEFAULT ''",
            "university": "TEXT DEFAULT ''",
            "course": "TEXT DEFAULT ''",
            "graduation_year": "TEXT DEFAULT ''",
            "location": "TEXT DEFAULT ''",
            "about": "TEXT DEFAULT ''",
            "portfolio": "TEXT DEFAULT ''",
            "linkedin": "TEXT DEFAULT ''",
            "skill_levels": "TEXT DEFAULT '{}'",
            "resume_path": "TEXT DEFAULT ''",
            "avatar_path": "TEXT DEFAULT ''",
        }
        for column, definition in profile_fields.items():
            if column not in student_columns:
                conn.execute(f"ALTER TABLE students ADD COLUMN {column} {definition}")
        task_columns = {row['name'] for row in conn.execute('PRAGMA table_info(tasks)')}
        if 'deliverables' not in task_columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deliverables TEXT DEFAULT ''")
        for column in ('submission_notes', 'submission_url', 'submission_path', 'submitted_at', 'review_feedback'):
            if column not in task_columns:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {column} TEXT DEFAULT ''")


def now():
    return datetime.now().isoformat(timespec="seconds")


def create_user(role, name, email, password):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO users(role,name,email,password_hash,created_at) VALUES(?,?,?,?,?)",
            (role, name.strip(), email.strip().lower(), hash_password(password), now()),
        )
        uid = cur.lastrowid
        if role == "student":
            conn.execute("INSERT INTO students(user_id) VALUES(?)", (uid,))
        else:
            conn.execute("INSERT INTO businesses(user_id) VALUES(?)", (uid,))
    return uid


def get_user_by_email(email):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email=?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None


def get_user(user_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_student(user_id):
    with connect() as conn:
        row = conn.execute(
            """SELECT u.id,u.name,u.email,s.skills,s.availability,s.minimum_budget,
                     s.experience,s.rating,s.jobs_completed,s.headline,s.university,
                     s.course,s.graduation_year,s.location,s.about,s.portfolio,s.linkedin,
                     s.skill_levels,s.resume_path,s.avatar_path
               FROM users u JOIN students s ON u.id=s.user_id WHERE u.id=?""",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def update_student(user_id, name, skills, availability, minimum_budget, experience,
                   headline="", university="", course="", graduation_year="",
                   location="", about="", portfolio="", linkedin="",
                   skill_levels="{}", resume_path="", avatar_path=""):
    with connect() as conn:
        conn.execute("UPDATE users SET name=? WHERE id=?", (name.strip(), user_id))
        conn.execute(
                """UPDATE students SET skills=?,availability=?,minimum_budget=?,experience=?,
                             headline=?,university=?,course=?,graduation_year=?,location=?,
                             about=?,portfolio=?,linkedin=?,skill_levels=?,resume_path=?,avatar_path=?
               WHERE user_id=?""",
                (skills.strip(), availability.strip(), minimum_budget, experience,
                 headline.strip(), university.strip(), course.strip(), graduation_year.strip(),
                 location.strip(), about.strip(), portfolio.strip(), linkedin.strip(),
                 skill_levels, resume_path, avatar_path, user_id),
        )


def list_student_projects(user_id):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM student_projects WHERE user_id=? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_student_project(user_id, title, description, tags, cover_image,
                         live_url, repo_url, project_id=None):
    values = (title.strip(), description.strip(), tags.strip(), cover_image.strip(),
              live_url.strip(), repo_url.strip())
    with connect() as conn:
        if project_id is None:
            cur = conn.execute(
                """INSERT INTO student_projects(
                       user_id,title,description,tags,cover_image,live_url,repo_url,updated_at
                   ) VALUES(?,?,?,?,?,?,?,?)""",
                (user_id, *values, now()),
            )
            return cur.lastrowid
        cur = conn.execute(
            """UPDATE student_projects SET title=?,description=?,tags=?,cover_image=?,
                      live_url=?,repo_url=?,updated_at=? WHERE id=? AND user_id=?""",
            (*values, now(), project_id, user_id),
        )
        if cur.rowcount != 1:
            raise ValueError("Project not found.")
        return project_id


def delete_student_project(user_id, project_id):
    with connect() as conn:
        cur = conn.execute(
            "DELETE FROM student_projects WHERE id=? AND user_id=?",
            (project_id, user_id),
        )
        return cur.rowcount == 1


def get_business(user_id):
    with connect() as conn:
        row = conn.execute(
            """SELECT u.id,u.name,u.email,b.industry,b.description
               FROM users u JOIN businesses b ON u.id=b.user_id WHERE u.id=?""",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def update_business(user_id, name, industry, description):
    with connect() as conn:
        conn.execute("UPDATE users SET name=? WHERE id=?", (name.strip(), user_id))
        conn.execute(
            "UPDATE businesses SET industry=?,description=? WHERE user_id=?",
            (industry.strip(), description.strip(), user_id),
        )


def create_task(business_id, title, category, description, required_skills,
                budget, deadline, schedule, experience, deliverables=""):
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO tasks(
                business_id,title,category,description,required_skills,budget,
                deadline,schedule,experience,status,created_at,deliverables
            ) VALUES(?,?,?,?,?,?,?,?,?,'Open',?,?)""",
            (business_id, title.strip(), category.strip(), description.strip(),
             required_skills.strip(), budget, deadline.strip(), schedule.strip(),
             experience, now(), deliverables.strip()),
        )
        return cur.lastrowid


def list_open_tasks():
    with connect() as conn:
        rows = conn.execute(
            """SELECT t.*,u.name AS business_name,
               (SELECT COUNT(*) FROM applications a WHERE a.task_id=t.id) AS applicants_count
               FROM tasks t JOIN users u ON t.business_id=u.id
               WHERE t.status='Open' ORDER BY t.id DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


def list_business_tasks(business_id):
    with connect() as conn:
        rows = conn.execute(
            """SELECT t.*,u.name AS student_name
               FROM tasks t
               LEFT JOIN users u ON t.assigned_student_id=u.id
               WHERE t.business_id=? ORDER BY t.id DESC""",
            (business_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_task(task_id):
    with connect() as conn:
        row = conn.execute(
            """SELECT t.*,u.name AS business_name,u.email AS business_email,
               (SELECT COUNT(*) FROM applications a WHERE a.task_id=t.id) AS applicants_count
               FROM tasks t JOIN users u ON t.business_id=u.id
               WHERE t.id=?""",
            (task_id,),
        ).fetchone()
        return dict(row) if row else None


def apply_to_task(task_id, student_id, match_score):
    with connect() as conn:
        conn.execute(
            """INSERT INTO applications(task_id,student_id,match_score,status,created_at)
               VALUES(?,?,?,'Pending',?)""",
            (task_id, student_id, match_score, now()),
        )


def list_student_applications(student_id):
    with connect() as conn:
        rows = conn.execute(
            """SELECT a.*,t.title,t.budget,t.status AS task_status,u.name AS business_name
               FROM applications a
               JOIN tasks t ON a.task_id=t.id
               JOIN users u ON t.business_id=u.id
               WHERE a.student_id=? ORDER BY a.id DESC""",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def list_task_applicants(task_id):
    with connect() as conn:
        rows = conn.execute(
            """SELECT a.*,u.name,u.email,s.skills,s.experience,s.rating,s.jobs_completed
               FROM applications a
               JOIN users u ON a.student_id=u.id
               JOIN students s ON a.student_id=s.user_id
               WHERE a.task_id=?
               ORDER BY a.match_score DESC,a.id ASC""",
            (task_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def decide_application(application_id, accept=False):
    with connect() as conn:
        app = conn.execute(
            "SELECT * FROM applications WHERE id=?", (application_id,)
        ).fetchone()
        if not app:
            raise ValueError("Application not found.")
        task = conn.execute("SELECT * FROM tasks WHERE id=?", (app["task_id"],)).fetchone()
        if not task or task["status"] != "Open":
            raise ValueError("This task is no longer open.")

        if accept:
            conn.execute(
                "UPDATE applications SET status='Accepted' WHERE id=?",
                (application_id,),
            )
            conn.execute(
                """UPDATE applications SET status='Rejected'
                   WHERE task_id=? AND id<>? AND status='Pending'""",
                (app["task_id"], application_id),
            )
            conn.execute(
                """UPDATE tasks SET status='Assigned',assigned_student_id=?
                   WHERE id=?""",
                (app["student_id"], app["task_id"]),
            )
        else:
            conn.execute(
                "UPDATE applications SET status='Rejected' WHERE id=?",
                (application_id,),
            )


def update_task_status(task_id, new_status):
    if new_status != 'In Progress':
        raise ValueError("Complete projects by reviewing and approving a student submission.")
    with connect() as conn:
        task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not task or not task['assigned_student_id']:
            raise ValueError('No student has been assigned.')
        if task['status'] != 'Assigned':
            raise ValueError('Only assigned projects can be started.')
        conn.execute("UPDATE tasks SET status='In Progress' WHERE id=?", (task_id,))


def submit_project(task_id, student_id, notes, url, file_path):
    if not url.strip() and not file_path.strip():
        raise ValueError("Attach a project file or provide a project link.")
    if url.strip() and not url.strip().lower().startswith(('https://', 'http://')):
        raise ValueError("Project links must start with https:// or http://.")
    with connect() as conn:
        task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not task or task['assigned_student_id'] != student_id:
            raise ValueError("You are not assigned to this project.")
        if task['status'] not in ('Assigned', 'In Progress', 'Changes Requested'):
            raise ValueError("This project is not accepting submissions.")
        conn.execute("""UPDATE tasks SET submission_notes=?, submission_url=?, submission_path=?,
                     submitted_at=?, status='Submitted' WHERE id=?""",
                     (notes.strip(), url.strip(), file_path, now(), task_id))


def review_project(task_id, business_id, approve, feedback):
    with connect() as conn:
        task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not task or task['business_id'] != business_id:
            raise ValueError("You cannot review this project.")
        if task['status'] != 'Submitted':
            raise ValueError("The student must submit work before review.")
        if not approve and not feedback.strip():
            raise ValueError("Describe the changes the student needs to make.")
        if approve:
            gross = float(task['budget'])
            fee = round(gross * .1, 2)
            conn.execute("""INSERT INTO transactions(task_id,gross,platform_fee,student_earnings,created_at)
                         VALUES(?,?,?,?,?)""", (task_id, gross, fee, round(gross-fee, 2), now()))
            conn.execute('UPDATE students SET jobs_completed=jobs_completed+1 WHERE user_id=?',
                         (task['assigned_student_id'],))
        conn.execute('UPDATE tasks SET status=?, review_feedback=? WHERE id=?',
                     ('Completed' if approve else 'Changes Requested', feedback.strip(), task_id))


def project_payment(task_id):
    with connect() as conn:
        row = conn.execute('SELECT * FROM transactions WHERE task_id=?', (task_id,)).fetchone()
        return dict(row) if row else None


def rate_student(task_id, business_id, score, comment):
    with connect() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not task or task["business_id"] != business_id:
            raise ValueError("Task not found.")
        if task["status"] != "Completed":
            raise ValueError("Complete the task before rating.")
        if not task["assigned_student_id"]:
            raise ValueError("No assigned student.")
        conn.execute(
            """INSERT INTO ratings(task_id,business_id,student_id,score,comment,created_at)
               VALUES(?,?,?,?,?,?)""",
            (task_id, business_id, task["assigned_student_id"], score, comment.strip(), now()),
        )
        avg = conn.execute(
            "SELECT AVG(score) AS avg_score FROM ratings WHERE student_id=?",
            (task["assigned_student_id"],),
        ).fetchone()["avg_score"]
        conn.execute(
            "UPDATE students SET rating=? WHERE user_id=?",
            (round(avg, 2), task["assigned_student_id"]),
        )


def student_financials(student_id):
    with connect() as conn:
        row = conn.execute(
            """SELECT COUNT(tr.id) AS completed,
                      COALESCE(SUM(tr.student_earnings),0) AS earnings
               FROM transactions tr
               JOIN tasks t ON tr.task_id=t.id
               WHERE t.assigned_student_id=?""",
            (student_id,),
        ).fetchone()
        return dict(row)


def business_analytics(business_id):
    with connect() as conn:
        row = conn.execute(
            """SELECT COUNT(t.id) AS tasks,
                      SUM(CASE WHEN t.status='Completed' THEN 1 ELSE 0 END) AS completed,
                      COALESCE(SUM(CASE WHEN t.status='Completed' THEN t.budget ELSE 0 END),0) AS spent
               FROM tasks t WHERE t.business_id=?""",
            (business_id,),
        ).fetchone()
        return dict(row)


def platform_analytics():
    with connect() as conn:
        students = conn.execute(
            "SELECT COUNT(*) n FROM users WHERE role='student'"
        ).fetchone()["n"]
        businesses = conn.execute(
            "SELECT COUNT(*) n FROM users WHERE role='business'"
        ).fetchone()["n"]
        tasks = conn.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"]
        completed = conn.execute(
            "SELECT COUNT(*) n FROM tasks WHERE status='Completed'"
        ).fetchone()["n"]
        trans = conn.execute(
            """SELECT COALESCE(SUM(gross),0) gross,
                      COALESCE(SUM(platform_fee),0) fees,
                      COALESCE(SUM(student_earnings),0) earnings
               FROM transactions"""
        ).fetchone()
        return {
            "students": students, "businesses": businesses, "tasks": tasks,
            "completed": completed, "gross": trans["gross"],
            "fees": trans["fees"], "earnings": trans["earnings"]
        }


def business_dashboard_data(business_id):
    year = str(datetime.now().year)
    with connect() as conn:
        totals = conn.execute(
            """SELECT
                      (SELECT COUNT(DISTINCT a.student_id)
                       FROM applications a JOIN tasks t ON t.id=a.task_id
                       WHERE t.business_id=?) AS customers,
                      (SELECT COUNT(*) FROM transactions tr JOIN tasks t ON t.id=tr.task_id
                       WHERE t.business_id=?) AS invoices,
                      (SELECT COALESCE(SUM(tr.gross),0) FROM transactions tr
                       JOIN tasks t ON t.id=tr.task_id WHERE t.business_id=?) AS revenue,
                      (SELECT COALESCE(SUM(tr.platform_fee),0) FROM transactions tr
                       JOIN tasks t ON t.id=tr.task_id WHERE t.business_id=?) AS fees""",
            (business_id, business_id, business_id, business_id),
        ).fetchone()
        states = conn.execute(
            """SELECT
                      SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) AS paid,
                      SUM(CASE WHEN status IN ('Assigned','In Progress') THEN 1 ELSE 0 END) AS pending,
                      SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) AS open
               FROM tasks WHERE business_id=?""",
            (business_id,),
        ).fetchone()
        monthly_rows = conn.execute(
            """SELECT CAST(strftime('%m',tr.created_at) AS INTEGER) AS month,
                      SUM(tr.gross) AS revenue
               FROM transactions tr JOIN tasks t ON t.id=tr.task_id
               WHERE t.business_id=? AND strftime('%Y',tr.created_at)=?
               GROUP BY strftime('%m',tr.created_at)""",
            (business_id, year),
        ).fetchall()
        recent = conn.execute(
            """SELECT tr.id,t.id AS task_id,t.title,tr.gross,tr.platform_fee,
                      tr.created_at,u.name AS student_name
               FROM transactions tr
               JOIN tasks t ON t.id=tr.task_id
               LEFT JOIN users u ON u.id=t.assigned_student_id
               WHERE t.business_id=? ORDER BY tr.created_at DESC LIMIT 8""",
            (business_id,),
        ).fetchall()
        return {
            **dict(totals), **dict(states),
            "monthly": {row["month"]: row["revenue"] for row in monthly_rows},
            "recent": [dict(row) for row in recent],
        }


def seed_demo_data():
    """Insert deterministic demo accounts/data if they do not already exist."""
    if get_user_by_email("naro@student.com"):
        return False

    s1 = create_user("student", "Naro", "naro@student.com", "student123")
    s2 = create_user("student", "Dara", "dara@student.com", "student123")
    b1 = create_user("business", "ABC Media", "abc@media.com", "business123")

    update_student(
        s1, "Naro",
        "Python, Video Editing, DaVinci Resolve, 3D Design",
        "Saturday, Sunday, Evening",
        15, "Intermediate"
    )
    update_student(
        s2, "Dara",
        "Canva, Graphic Design, Social Media",
        "Saturday, Evening",
        10, "Beginner"
    )
    update_business(
        b1, "ABC Media", "Media & Marketing",
        "Small creative studio posting short student-friendly projects."
    )

    create_task(
        b1, "Edit a 60-second promotional video", "Video Editing",
        "Edit supplied footage into a polished 60-second social media promo.",
        "Video Editing, DaVinci Resolve", 30, "2026-10-15",
        "Saturday, Evening", "Intermediate"
    )
    create_task(
        b1, "Design 5 Instagram posts", "Graphic Design",
        "Create five branded square posts for a small campaign.",
        "Canva, Graphic Design", 20, "2026-10-18",
        "Saturday", "Beginner"
    )
    create_task(
        b1, "Build a simple Python expense tracker", "Programming",
        "Create a command-line expense tracker with file saving.",
        "Python", 35, "2026-10-20",
        "Sunday, Evening", "Intermediate"
    )
    return True


def _message_access(conn, task_id, student_id, user_id):
    task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
    student = conn.execute("SELECT id FROM users WHERE id=? AND role='student'", (student_id,)).fetchone()
    if not task or not student or user_id not in (student_id, task['business_id']):
        raise ValueError('You do not have access to this conversation.')
    existing = conn.execute('SELECT id FROM project_messages WHERE task_id=? AND student_id=? LIMIT 1',
                            (task_id, student_id)).fetchone()
    if task['status'] != 'Open' and task['assigned_student_id'] != student_id and not existing:
        raise ValueError('This project is no longer accepting new conversations.')
    return task


def send_project_message(task_id, student_id, sender_id, body):
    body = body.strip()
    if not body or len(body) > 5000:
        raise ValueError('Enter a message between 1 and 5,000 characters.')
    with connect() as conn:
        _message_access(conn, task_id, student_id, sender_id)
        cursor = conn.execute('INSERT INTO project_messages(task_id,student_id,sender_id,body,created_at) VALUES(?,?,?,?,?)',
                              (task_id, student_id, sender_id, body, now()))
        return cursor.lastrowid


def get_project_messages(task_id, student_id, user_id):
    with connect() as conn:
        _message_access(conn, task_id, student_id, user_id)
        conn.execute("UPDATE project_messages SET read_at=? WHERE task_id=? AND student_id=? AND sender_id<>? AND read_at=''",
                     (now(), task_id, student_id, user_id))
        rows = conn.execute("""SELECT m.*,u.name sender_name FROM project_messages m
            JOIN users u ON u.id=m.sender_id WHERE task_id=? AND student_id=? ORDER BY m.id""",
                            (task_id, student_id)).fetchall()
        return [dict(row) for row in rows]


def list_conversations(user_id):
    with connect() as conn:
        rows = conn.execute("""SELECT m.task_id,m.student_id,t.title,u.name student_name,b.name business_name,
            MAX(m.id) last_id,
            SUM(CASE WHEN m.sender_id<>? AND m.read_at='' THEN 1 ELSE 0 END) unread
            FROM project_messages m JOIN tasks t ON t.id=m.task_id
            JOIN users u ON u.id=m.student_id JOIN users b ON b.id=t.business_id
            WHERE m.student_id=? OR t.business_id=? GROUP BY m.task_id,m.student_id ORDER BY last_id DESC""",
                            (user_id,user_id,user_id)).fetchall()
        return [dict(row) for row in rows]
