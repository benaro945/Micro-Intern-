"""Isolated UI smoke check; does not touch the application's database."""
import tempfile
import gc
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk

import database as db
from ui import MicroInternApp


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def run():
    original_path = db.DB_PATH
    with tempfile.TemporaryDirectory() as directory:
        db.DB_PATH = Path(directory) / "test.db"
        app = MicroInternApp()
        app.withdraw()
        try:
            db.seed_demo_data()
            app.current_user = db.get_user_by_email("naro@student.com")
            for screen in (app.show_student_dashboard, app.show_student_tasks,
                           app.show_student_applications, app.show_student_profile):
                screen()
                app.update()
                widgets = list(descendants(app))
                assert any(isinstance(w, tk.Frame) and w.cget("bg") == "#303e4e" for w in widgets)
                assert len([w for w in widgets if isinstance(w, tk.Menubutton)]) == 1
                assert not any(isinstance(w, tk.Button) and w.cget("text") == app.t("logout") for w in widgets)
            photo = tk.PhotoImage(master=app, width=100, height=80)
            photo.put("#4169e1", to=(0, 0, 100, 80))
            source = Path(directory) / "avatar.png"
            photo.write(str(source), format="png")
            with patch("ui.filedialog.askopenfilename", return_value=str(source)):
                edit = next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget("text") == "Edit photo")
                edit.invoke()
            avatar = next(w for w in descendants(app) if isinstance(w, tk.Button) and hasattr(w, "image"))
            assert avatar.image.width() <= 90
            with patch("ui.messagebox.showinfo"):
                save = next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget("text") == "Save Changes")
                save.invoke()
            stored = Path(db.get_student(app.current_user['id'])['avatar_path'])
            assert stored.is_file() and stored != source
            source.unlink()
            app.show_student_tasks()
            app.update()
            cards = [w for w in descendants(app) if hasattr(w, 'task_id')]
            assert len(cards) == len(db.list_open_tasks())
            assert not any(isinstance(w, ttk.Treeview) for w in descendants(app))
            search = next(w for w in descendants(app) if w.winfo_class() == 'Entry')
            search.insert(0, 'no-task-matches-this-query')
            app.update()
            assert not any(hasattr(w, 'task_id') for w in descendants(app))
            search.delete(0, 'end')
            app.update()
            task_id = db.list_open_tasks()[0]['id']
            app.show_task_detail(task_id)
            app.update()
            labels = [w.cget('text') for w in descendants(app) if isinstance(w, tk.Label)]
            assert db.get_task(task_id)['business_email'] in labels
            assert 'DELIVERABLES' in labels and 'BUDGET BREAKDOWN' in labels
            with patch('ui.messagebox.showinfo'):
                apply = next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget('text') == 'Apply Now')
                apply.invoke()
            assert db.get_task(task_id)['applicants_count'] == 1
            app.show_task_detail(task_id)
            applied = next(w for w in descendants(app) if isinstance(w, tk.Button) and w.cget('text') == 'Applied')
            assert applied.cget('state') == 'disabled'
            dropdown = next(w for w in descendants(app) if isinstance(w, tk.Menubutton))
            assert dropdown.image.width() <= 32
            app.logout()
            assert app.current_user is None
        finally:
            app.destroy()
            db.DB_PATH = original_path
            gc.collect()
    print("Navigation, marketplace search, task details, application submission, avatar storage, and logout checks passed.")


if __name__ == "__main__":
    run()
