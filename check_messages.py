"""Check in-app conversations against an isolated database."""
import gc
import tempfile
from pathlib import Path
import tkinter as tk
import database as db
from ui import MicroInternApp
from check_student_ui import descendants


def run():
    original = db.DB_PATH
    with tempfile.TemporaryDirectory() as folder:
        db.DB_PATH = Path(folder) / 'messages.db'
        app = MicroInternApp()
        app.withdraw()
        try:
            db.seed_demo_data()
            student = db.get_user_by_email('naro@student.com')
            other = db.get_user_by_email('dara@student.com')
            business = db.get_user_by_email('abc@media.com')
            task = db.list_open_tasks()[0]
            app.current_user = student
            app.show_student_projects()
            app.update()
            app.show_messages(task['id'], student['id'])
            app.update()
            composer = next(w for w in descendants(app) if isinstance(w, tk.Text) and w.cget('state') == 'normal')
            composer.insert('1.0', 'Can we discuss the deliverables?')
            next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget('text') == 'Send Message').invoke()
            assert db.list_conversations(business['id'])[0]['unread'] == 1
            try:
                db.get_project_messages(task['id'], student['id'], other['id'])
                raise AssertionError('Conversation exposed to unrelated account')
            except ValueError:
                pass
            app.current_user = business
            app.show_messages(task['id'], student['id'])
            app.update()
            assert db.list_conversations(business['id'])[0]['unread'] == 0
            composer = next(w for w in descendants(app) if isinstance(w, tk.Text) and w.cget('state') == 'normal')
            composer.insert('1.0', 'Yes, please deliver the source files too.')
            next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget('text') == 'Send Message').invoke()
            assert db.list_conversations(student['id'])[0]['unread'] == 1
            history = db.get_project_messages(task['id'], student['id'], student['id'])
            assert len(history) == 2 and history[-1]['sender_id'] == business['id']
            app.current_user = student
            app.show_student_projects()
            assert app._messages_after_id is None
            try:
                db.send_project_message(task['id'], student['id'], student['id'], '   ')
                raise AssertionError('Blank message accepted')
            except ValueError:
                pass
        finally:
            app.destroy()
            db.DB_PATH = original
            gc.collect()
    print('Student/business messages, persistence, unread counts, access restrictions, and navigation passed.')


if __name__ == '__main__':
    run()
